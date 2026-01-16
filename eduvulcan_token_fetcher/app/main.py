#!/usr/bin/env python3
import asyncio
import base64
import json
import logging
import os
import re
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

LOGGER = logging.getLogger("eduvulcan_token_fetcher")

JWT_PATTERN = re.compile(r"[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+")

LOGIN_URL = os.getenv("EDUVULCAN_LOGIN_URL", "https://uonetplus.vulcan.net.pl/")
LOGIN_SELECTOR = os.getenv(
    "EDUVULCAN_LOGIN_SELECTOR",
    "input[name='login'], input[name='username'], input[type='email']",
)
PASSWORD_SELECTOR = os.getenv("EDUVULCAN_PASSWORD_SELECTOR", "input[type='password']")
SUBMIT_SELECTOR = os.getenv(
    "EDUVULCAN_SUBMIT_SELECTOR",
    "button[type='submit'], input[type='submit']",
)
TOKEN_OUTPUT_PATH = os.getenv("EDUVULCAN_TOKEN_PATH", "/config/eduvulcan_token.json")


class TokenNotFoundError(RuntimeError):
    pass


def _decode_jwt(token: str) -> Dict[str, Any]:
    payload = token.split(".")[1]
    padded = payload + "=" * (-len(payload) % 4)
    decoded = base64.urlsafe_b64decode(padded.encode("utf-8"))
    return json.loads(decoded.decode("utf-8"))


def _find_jwt_in_mapping(mapping: Dict[str, Any]) -> Optional[str]:
    for value in mapping.values():
        if isinstance(value, str):
            match = JWT_PATTERN.search(value)
            if match:
                return match.group(0)
    return None


def _find_jwt_in_collection(values: Tuple[str, ...]) -> Optional[str]:
    for value in values:
        match = JWT_PATTERN.search(value)
        if match:
            return match.group(0)
    return None


async def fetch_token(login: str, password: str) -> Tuple[str, str]:
    token_candidates = []

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"],
        )
        context = await browser.new_context()
        page = await context.new_page()

        async def handle_response(response):
            content_type = response.headers.get("content-type", "")
            if "application/json" not in content_type:
                return
            try:
                data = await response.json()
            except Exception:
                return
            if isinstance(data, dict):
                for key in ("token", "access_token", "jwt", "id_token"):
                    candidate = data.get(key)
                    if isinstance(candidate, str):
                        token_candidates.append((candidate, f"response:{key}"))

        page.on("response", handle_response)

        LOGGER.info("Opening login page: %s", LOGIN_URL)
        await page.goto(LOGIN_URL, wait_until="domcontentloaded")

        login_input = page.locator(LOGIN_SELECTOR)
        if await login_input.count() == 0:
            raise RuntimeError("Login input not found on the page")
        await login_input.first.fill(login)

        password_input = page.locator(PASSWORD_SELECTOR)
        if await password_input.count() == 0:
            raise RuntimeError("Password input not found on the page")
        await password_input.first.fill(password)

        submit_button = page.locator(SUBMIT_SELECTOR)
        if await submit_button.count() > 0:
            await submit_button.first.click()
        else:
            await password_input.first.press("Enter")

        try:
            await page.wait_for_load_state("networkidle", timeout=30000)
        except PlaywrightTimeoutError:
            LOGGER.warning("Timed out waiting for network idle; continuing")

        storage = await page.evaluate(
            """
            () => {
              const toObject = (storage) => {
                const data = {};
                for (let i = 0; i < storage.length; i += 1) {
                  const key = storage.key(i);
                  data[key] = storage.getItem(key);
                }
                return data;
              };
              return {
                localStorage: toObject(window.localStorage),
                sessionStorage: toObject(window.sessionStorage),
              };
            }
            """
        )

        local_token = _find_jwt_in_mapping(storage.get("localStorage", {}))
        if local_token:
            token_candidates.append((local_token, "localStorage"))

        session_token = _find_jwt_in_mapping(storage.get("sessionStorage", {}))
        if session_token:
            token_candidates.append((session_token, "sessionStorage"))

        cookies = await context.cookies()
        cookie_values = tuple(cookie.get("value", "") for cookie in cookies)
        cookie_token = _find_jwt_in_collection(cookie_values)
        if cookie_token:
            token_candidates.append((cookie_token, "cookies"))

        await browser.close()

    if not token_candidates:
        raise TokenNotFoundError("JWT token not found in responses, storage, or cookies")

    token, source = token_candidates[0]
    LOGGER.info("Token extracted from %s", source)
    return token, source


def write_token(token: str) -> None:
    output_dir = os.path.dirname(TOKEN_OUTPUT_PATH)
    if output_dir and not os.path.isdir(output_dir):
        raise RuntimeError(f"Output directory does not exist: {output_dir}")

    payload: Dict[str, Any] = {
        "token": token,
        "source": "playwright",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }

    try:
        decoded = _decode_jwt(token)
        exp = decoded.get("exp")
        if isinstance(exp, (int, float)):
            payload["expires_at"] = datetime.fromtimestamp(exp, timezone.utc).isoformat()
    except Exception:
        LOGGER.warning("Failed to decode JWT expiry information")

    with open(TOKEN_OUTPUT_PATH, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")


async def main() -> int:
    login = os.getenv("EDUVULCAN_LOGIN")
    password = os.getenv("EDUVULCAN_PASSWORD")

    if not login or not password:
        LOGGER.error("Missing login/password in environment variables")
        return 1

    try:
        token, _source = await fetch_token(login, password)
        write_token(token)
        LOGGER.info("Token written to %s", TOKEN_OUTPUT_PATH)
        LOGGER.info("EduVulcan token fetcher finished successfully")
        return 0
    except TokenNotFoundError as exc:
        LOGGER.error("%s", exc)
        return 2
    except Exception as exc:  # noqa: BLE001 - ensure clear error for add-on logs
        LOGGER.exception("Unexpected error: %s", exc)
        return 1


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    exit_code = asyncio.run(main())
    sys.exit(exit_code)
