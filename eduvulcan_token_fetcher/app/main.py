#!/usr/bin/env python3
import asyncio
import json
import os
import base64
import logging
import argparse
import time
from datetime import datetime, timezone

from playwright.async_api import async_playwright

LOGGER = logging.getLogger("eduvulcan_token_fetcher")

# Ścieżki w HA
TOKEN_FILE = "/config/eduvulcan_token.json"
STORAGE_FILE = "/data/eduvulcan_storage.json"

# Startujemy ZAWSZE od /api/ap
EDUVULCAN_URL = "https://eduvulcan.pl/api/ap"

# Zapas przed wygaśnięciem JWT (sekundy)
REFRESH_MARGIN = 300  # 5 minut


def decode_jwt_payload(jwt: str) -> dict:
    payload = jwt.split(".")[1]
    payload += "=" * (-len(payload) % 4)
    decoded = base64.urlsafe_b64decode(payload)
    return json.loads(decoded)


def read_saved_token():
    if not os.path.exists(TOKEN_FILE):
        return None
    try:
        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        LOGGER.warning("Failed to read token file: %s", exc)
        return None


def token_validity(token_data: dict):
    """
    Zwraca: (is_valid: bool, exp_ts: int, seconds_left: int)
    """
    try:
        payload = token_data["jwt_payload"]
        exp = int(payload["exp"])
        now = int(time.time())
        seconds_left = exp - now
        return seconds_left > REFRESH_MARGIN, exp, seconds_left
    except Exception:
        return False, 0, 0


async def fetch_new_token(login: str, password: str):
    LOGGER.info("Launching Playwright (headless Chromium)")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )

        # Wczytaj cookies / sesję jeśli istnieją
        if os.path.exists(STORAGE_FILE):
            LOGGER.info("Loading stored cookies/session")
            context = await browser.new_context(storage_state=STORAGE_FILE)
        else:
            context = await browser.new_context()

        page = await context.new_page()

        try:
            # 1) Idziemy na /api/ap (backend przekieruje na /logowanie jeśli trzeba)
            LOGGER.info("Opening: %s", EDUVULCAN_URL)
            await page.goto(EDUVULCAN_URL, wait_until="networkidle")

            # Usuń overlay cookies (jeśli jest)
            await page.evaluate("""
                const el = document.getElementById("respect-privacy-wrapper");
                if (el) el.remove();
            """)

            # 2) Sprawdź czy sesja już aktywna (czy istnieje #ap)
            try:
                await page.wait_for_selector("#ap", timeout=5000)
                LOGGER.info("Active session detected – token available without login")
            except:
                LOGGER.info("No active session – performing login flow")

                # Krok 1: login
                await page.wait_for_selector("#Alias", timeout=30000)
                await page.fill("#Alias", login)
                await page.click("#btNext")

                # Krok 2: hasło
                await page.wait_for_selector("#Password", timeout=30000)
                await page.fill("#Password", password)

                # Captcha (jeśli się pojawi)
                try:
                    await page.wait_for_selector("#captcha", state="visible", timeout=5000)
                    await page.wait_for_function(
                        "document.querySelector('#captcha-response') && document.querySelector('#captcha-response').value !== ''",
                        timeout=30000
                    )
                except:
                    pass

                await page.click("#btLogOn")

                # Czekamy aż backend zwróci stronę z #ap
                await page.wait_for_selector("#ap", state="attached", timeout=60000)

            # 3) Odczyt tokena z #ap (jedyna prawidłowa metoda)
            token_json = await page.eval_on_selector("#ap", "el => el.value")
            data = json.loads(token_json)

            tokens = data.get("Tokens") or []
            jwt = tokens[0] if tokens else None
            if not jwt:
                raise RuntimeError("Brak JWT w polu Tokens[]")

            payload = decode_jwt_payload(jwt)
            tenant = payload.get("tenant")
            if not tenant:
                raise RuntimeError("Nie udało się odczytać tenant z JWT")

            # 4) Zapis tokena do /config
            output = {
                "tenant": tenant,
                "jwt": jwt,
                "jwt_payload": payload,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "source": "eduvulcan.pl/api/ap",
            }

            with open(TOKEN_FILE, "w", encoding="utf-8") as f:
                json.dump(output, f, indent=2, ensure_ascii=False)
                f.write("\n")

            # 5) Zapis cookies / localStorage do /data
            await context.storage_state(path=STORAGE_FILE)

            LOGGER.info("Token saved to: %s", TOKEN_FILE)
            LOGGER.info("Storage saved to: %s", STORAGE_FILE)
            LOGGER.info("Done (tenant: %s)", tenant)

        finally:
            await browser.close()


async def watchdog_loop(login: str, password: str):
    """
    Tryb ciągły:
    - sprawdza exp JWT
    - odświeża tylko gdy trzeba
    """
    LOGGER.info("Starting JWT watchdog loop (refresh margin: %ss)", REFRESH_MARGIN)

    while True:
        token_data = read_saved_token()

        if token_data:
            valid, exp, seconds_left = token_validity(token_data)
            if valid:
                sleep_for = max(60, seconds_left - REFRESH_MARGIN)
                exp_dt = datetime.fromtimestamp(exp, tz=timezone.utc).isoformat()
                LOGGER.info(
                    "Token still valid. Expires at %s (in %ss). Next check in %ss",
                    exp_dt, seconds_left, sleep_for
                )
                await asyncio.sleep(sleep_for)
                continue

        LOGGER.info("Token missing or expired – refreshing now...")
        try:
            await fetch_new_token(login, password)
        except Exception as exc:
            LOGGER.exception("Refresh failed: %s", exc)
            # Nie pętlimy agresywnie przy błędzie
            await asyncio.sleep(300)
            continue

        # Krótka pauza po odświeżeniu
        await asyncio.sleep(30)


async def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="Refresh token once and exit")
    args = parser.parse_args()

    login = os.getenv("EDUVULCAN_LOGIN")
    password = os.getenv("EDUVULCAN_PASSWORD")

    if not login or not password:
        LOGGER.error("Missing login/password in environment variables")
        return 1

    try:
        if args.once:
            LOGGER.info("Running in one-shot mode (--once)")
            await fetch_new_token(login, password)
        else:
            await watchdog_loop(login, password)
        return 0
    except Exception as exc:
        LOGGER.exception("Unexpected error: %s", exc)
        return 1


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    exit_code = asyncio.run(main())
    raise SystemExit(exit_code)
