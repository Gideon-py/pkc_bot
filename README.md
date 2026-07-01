# Pokemon Center "30th" Monitor - Setup-Anleitung

Läuft 24/7 in der Cloud (GitHub Actions), dein PC muss dafür nicht laufen.

## 1. Telegram-Bot erstellen (falls noch nicht geschehen)
1. In Telegram nach **@BotFather** suchen
2. `/newbot` senden, Namen und Benutzernamen vergeben
3. Den **API-Token** notieren (z.B. `123456789:ABCdefGHI...`)
4. Deinem neuen Bot eine beliebige Nachricht schicken (z.B. "hi")
5. Im Browser öffnen: `https://api.telegram.org/bot<DEIN_TOKEN>/getUpdates`
6. Die **Chat-ID** (eine Zahl) aus der Antwort notieren

## 2. GitHub Repository erstellen
1. Auf github.com kostenloses Konto erstellen (falls noch nicht vorhanden)
2. Neues Repository erstellen, z.B. `pokemon-monitor`
   - **Public** empfohlen (unbegrenzte kostenlose Actions-Minuten).
     Das ist unproblematisch, da keine Geheimnisse im Code stehen -
     Token/Chat-ID werden separat als "Secrets" hinterlegt (siehe Schritt 3),
     die für niemanden sichtbar sind.
   - Falls du **Private** bevorzugst: funktioniert auch, du hast dann
     aber nur 2000 kostenlose Actions-Minuten pro Monat (sollte bei
     10-Minuten-Intervall meist reichen, aber knapp werden können).
3. Alle Dateien aus diesem Ordner (`monitor.py`, `requirements.txt`,
   `.github/workflows/monitor.yml`) in das Repository hochladen
   (einfachster Weg: auf GitHub "Add file" -> "Upload files" per Drag & Drop,
   Ordnerstruktur bleibt dabei erhalten)

## 3. Secrets hinterlegen
1. Im Repository: **Settings** -> **Secrets and variables** -> **Actions**
2. **New repository secret** klicken
3. Zwei Secrets anlegen:
   - Name: `TELEGRAM_BOT_TOKEN` -> Wert: dein Bot-Token
   - Name: `TELEGRAM_CHAT_ID` -> Wert: deine Chat-ID

## 4. Testen
1. Im Repository auf **Actions** -> **Pokemon Center Monitor** gehen
2. **Run workflow** klicken (manueller Test, damit du nicht 10 Min. warten musst)
3. Nach ca. 1-2 Minuten sollte der Lauf grün (erfolgreich) sein
4. Falls ein Treffer gefunden wird, kommt sofort eine Telegram-Nachricht

Danach läuft es automatisch alle 10 Minuten - auch wenn dein PC aus ist,
im Standby ist, oder du unterwegs bist.

## Wichtig zu wissen
- Pokémon Center nutzt Bot-Erkennung. Falls der Lauf in den Actions-Logs
  "Keine Produkte gefunden" zeigt, wurde der Zugriff evtl. blockiert -
  meld dich dann, wir passen die Erkennungslogik an.
- Der letzte Schritt (Warenkorb, Bestellung abschliessen) bleibt bewusst
  bei dir - das Skript schickt dir nur Name + direkten Link per Telegram.
  Achte darauf, dass du bei pokemoncenter.com auf deinem Handy eingeloggt
  bleibst und deine Adresse/Zahlungsmethode dort hinterlegt hast, damit
  der Checkout nach dem Klick auf den Link nur noch wenige Sekunden dauert.
