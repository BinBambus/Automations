#!/bin/bash

# 1. In das Hauptverzeichnis deines Projekts wechseln
cd /home/pi/Automations/Bachelorarbeit-Note

PDF_FILE="Leistungsuebersicht.pdf"

# Prüfen, ob die PDF bereits existiert
if [ -f "$PDF_FILE" ]; then
    git add jobs.log
    git add "$PDF_FILE"
    git diff-index --quiet HEAD || git commit -m "Automatischer Commit: Neue Logs und PDF-Datei"
    git push origin main

    echo "Die Datei '$PDF_FILE' existiert bereits. Skripte werden übersprungen."
    exit 0
fi

# 2. Das virtuelle Environment aktivieren
source venv/bin/activate

# 3. Die aktuelle Version von GitHub holen
git pull origin main

# 4. Die Python-Skripte ausführen
python3 Scraper.py
python3 EmailVersand.py

# Loggen, ob die Skripte erfolgreich waren
git add jobs.log
git diff-index --quiet HEAD || git commit -m "Automatischer Commit: Neues Log"
git push origin main

# 5. Environment wieder deaktivieren
deactivate