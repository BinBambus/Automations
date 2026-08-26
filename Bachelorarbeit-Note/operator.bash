#!/bin/bash
cd /home/pi/Automations/Bachelorarbeit-Note || exit 1

PDF_FILE="Leistungsuebersicht.pdf"

# 1. Prüfen, ob die PDF bereits existiert
if [ -f "$PDF_FILE" ]; then
    echo "Die Datei '$PDF_FILE' existiert bereits. Skripte werden übersprungen."
    exit 0
fi

# 2. Virtual Environment aktivieren
source venv/bin/activate

# 3. Neuesten Code holen
git pull origin main

# 4. Skripte unbuffered (-u) ausführen
python3 -u Scraper.py
python3 -u EmailVersand.py

# 5. Git Commit & Push (nur wenn sich im Log etwas geändert hat)
git add jobs.log
git diff-index --quiet HEAD || {
    git commit -m "Automatischer Log-Update $(date '+%Y-%m-%d %H:%M:%S')"
    git push origin main
}

deactivate