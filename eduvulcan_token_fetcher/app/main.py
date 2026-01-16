#!/usr/bin/env python3
import asyncio
import json
import os
import base64
import logging
from datetime import datetime, timezone

from playwright.async_api import async_playwright

LOGGER = logging.getLogger("eduvulcan_token_fetcher")

# Ścieżki w HA
TOKEN_FILE = "/config/eduvulcan_token.json"
STORAGE_FILE = "/data/eduvulcan_storage.json"

# Startujemy ZAWSZE od /api/ap
EDUVULCAN_URL = "https://eduvulcan.pl/api/ap"


def decode_jwt_payload(jwt: str) -> dict:
    payload = jwt.split(".")[1]
    payload += "=" * (-len(payload) % 4)
    decoded = base64.urlsafe_b64decode(payload)
    return json.loads(decoded)


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

            # 3) Odczyt tokena Z #ap (jedyna prawidłowa metoda)
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


async def main() -> int:
    login = os.getenv("EDUVULCAN_LOGIN")
    password = os.getenv("EDUVULCAN_PASSWORD")

    if not login or not password:
        LOGGER.error("Missing login/password in environment variables")
        return 1

    try:
        await fetch_new_token(login, password)
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
