"""
Pokemon Center - Neue "30th"-Artikel Monitor (GitHub Actions Version)
=======================================================================

Läuft automatisch in GitHub Actions nach Zeitplan - dein PC muss
dafür NICHT laufen.

Token und Chat-ID werden NICHT im Code hinterlegt, sondern als
GitHub "Secrets" gesetzt und hier über Umgebungsvariablen gelesen.
Siehe README.md für die Einrichtung.
"""

import json
import os
import sys
from pathlib import Path

import requests
from playwright.sync_api import sync_playwright

# ----------------------------------------------------------------
# KONFIGURATION
# ----------------------------------------------------------------

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

CATEGORY_URL = "https://www.pokemoncenter.com/category/tcg-cards"
KEYWORD = "30th"  # Groß-/Kleinschreibung wird ignoriert

SEEN_FILE = Path(__file__).parent / "seen_products.json"

# ----------------------------------------------------------------


def load_seen() -> set:
    if SEEN_FILE.exists():
        return set(json.loads(SEEN_FILE.read_text()))
    return set()


def save_seen(seen: set) -> None:
    SEEN_FILE.write_text(json.dumps(sorted(seen)))


def send_telegram(text: str) -> None:
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    resp = requests.post(
        url,
        data={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": text,
            "disable_web_page_preview": False,
        },
        timeout=15,
    )
    if not resp.ok:
        print(f"[!] Telegram-Fehler: {resp.status_code} {resp.text}")


def fetch_products() -> list[dict]:
    products = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            ),
            locale="en-US",
        )
        page = context.new_page()
        page.goto(CATEGORY_URL, wait_until="domcontentloaded", timeout=60000)

        try:
            page.click("text=Accept All", timeout=5000)
        except Exception:
            pass

        try:
            page.select_option("select[name='sort']", label="Newest", timeout=5000)
            page.wait_for_timeout(3000)
        except Exception:
            print("[i] Sort-Dropdown nicht gefunden - fahre ohne Sortierung fort.")

        page.wait_for_timeout(3000)

        links = page.query_selector_all('a[href*="/product/"]')
        for link in links:
            name = (link.get_attribute("title") or link.inner_text() or "").strip()
            href = link.get_attribute("href") or ""
            if not name or not href:
                continue
            if href.startswith("/"):
                href = "https://www.pokemoncenter.com" + href
            products.append({"name": name, "url": href})

        browser.close()
    return products


def main():
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[!] TELEGRAM_BOT_TOKEN oder TELEGRAM_CHAT_ID Secret fehlt!")
        sys.exit(1)

    seen = load_seen()
    print(f"Prüfe {CATEGORY_URL} nach '{KEYWORD}'...")

    try:
        products = fetch_products()
    except Exception as e:
        print(f"[!] Fehler beim Laden der Seite: {e}")
        sys.exit(0)  # kein harter Fehler, nächster Run versucht's erneut

    if not products:
        print("[!] Keine Produkte gefunden - evtl. blockiert oder Selector "
              "veraltet.")
        sys.exit(0)

    print(f"[i] {len(products)} Produkte gefunden.")

    new_matches = []
    for prod in products:
        if KEYWORD.lower() in prod["name"].lower():
            if prod["url"] not in seen:
                new_matches.append(prod)
            seen.add(prod["url"])

    for match in new_matches:
        msg = f"🆕 Neuer '{KEYWORD}' Artikel!\n\n{match['name']}\n\n{match['url']}"
        print(f"[+] Match: {match['name']}")
        send_telegram(msg)

    if not new_matches:
        print("[i] Keine neuen Treffer.")

    save_seen(seen)


if __name__ == "__main__":
    main()
