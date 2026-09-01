from playwright.sync_api import sync_playwright
import time
import os
from dotenv import load_dotenv

load_dotenv()

# Zugangsdaten
USERNAME: str = os.getenv("USERNAME")
PASSWORD: str = os.getenv("PASSWORD")
OUTPUT_FILE = "Leistungsuebersicht.pdf"

START_URL = "https://cim.hs-mainz.de/qisserver/pages/cs/sys/portal/hisinoneStartPage.faces"

with sync_playwright() as p:
    # headless=False zum Debuggen – setze es später auf True, wenn alles läuft
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(accept_downloads=True)
    page = context.new_page()

    print("1. Öffne Startseite...")
    page.goto(START_URL)

    # 2. Login-Button auf der HISinOne-Seite klicken
    # HISinOne hat meist einen prominenten Anmelde-Button / Link
    print("2. Klicke auf Login/Anmelden...")
    # Sucht nach Links/Buttons mit "Anmelden" oder "Login"
    page.locator("button:has-text('Zur Anmeldung')").first.click()
    page.locator("a:has-text('Login für Studierende und Beschäftigte')").first.click()

    # 3. Warten bis der IdP (srv-idp-001.hs-mainz.de) geladen ist
    page.wait_for_url("**/idp/**")
    print("3. Auf Shibboleth IdP weitergeleitet. Gebe Zugangsdaten ein...")

    # Shibboleth Formularfelder ausfüllen (typischerweise 'j_username' und 'j_password' oder 'username'/'password')
    # Wir nutzen flexible Selektoren:
    page.locator("input[type='text']").first.fill(USERNAME)
    page.locator("input[type='password']").first.fill(PASSWORD)

    # Login absenden
    page.locator("button[type='submit']").first.click()

    # 4. Warten, bis das SAML-Handshake durch ist und wir wieder auf cim.hs-mainz.de sind
    print("4. Warte auf Rückleitung ins HISinOne-Portal...")
    page.wait_for_url("https://cim.hs-mainz.de/**")
    page.wait_for_load_state("networkidle")
    print("-> Erfolgreich eingeloggt!")

    # Navigiere z.B. zu Prüfungsverwaltung / Notenspiegel und klicke auf das PDF-Icon:
    # 5. Navigieren über das Menü
    print("5. Navigiere im Menü...")

    # Attribut-Selektoren nutzen: [name='...'] bzw. [id='...']
    # 1. Burger-Menü / Navigationsleiste öffnen
    page.locator("[name='widgetRender:4:mobileOnlyNavBar']").first.click()
    page.wait_for_timeout(500)  # Kurze Pause für die Menü-Animation

    # 2. Hauptmenüpunkt (z.B. "Mein Studium" / "Prüfungen")
    page.locator("[id='widgetRender:4:burgerNavi:1:selectedLink1'], [id='widgetRender:4:burgerNavi:1:notSelectedLink1']").first.click()
    page.wait_for_timeout(500)

    # 3. Untermenüpunkt (z.B. "Leistungen" / "Notenspiegel")
    page.locator("[id='widgetRender:4:burgerNavi:1:3:link2']").first.click()
    page.wait_for_load_state("networkidle")

    # 4. Bachelornotenspiegel auswählen (falls mehrere Studiengänge vorhanden)
    page.locator("[name='examsReadonly:degreeProgramProgressForReportAsTree:studyHistoryTree:0:0:0:0:checkTick']").first.click()
    page.wait_for_load_state("networkidle")
    page.locator("[name='examsReadonly:degreeProgramProgressForReportAsTree:studyHistoryTree:0:1:checkAll']").first.click()
    page.wait_for_load_state("networkidle")

    # 6. PDF-Download auslösen
    print("6. Starte Download der Leistungsübersicht...")
    with page.expect_download() as download_info:
        # Klicke auf den PDF-Download-Link / Button auf der Zielseite:
        # (Suchbegriff anpassen, falls der Button anders beschriftet ist)
        page.locator("button:has-text('Leistungsübersicht (alle Versuche) [PDF]')").first.click()

    # 6. Datei auf der Festplatte speichern
    download = download_info.value
    download.save_as(OUTPUT_FILE)
    print(f"Erfolg! PDF gespeichert als: {OUTPUT_FILE}")

    browser.close()