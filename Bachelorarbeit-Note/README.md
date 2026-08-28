# Bachelorarbeit-Note Scraper
Der Bachelorarbeits-Noten Scraper ist ein Tool, welches mit *playwrite* die **Leistungsübersicht.pdf** aus dem Accounts des Nutzers im Campus Information (CIM) ausliest und prüft.

Wird eine neue Note für die Bachelorarbeit gefunden wird eine Automatisierte Email an den Nutzer verschickt mit PDF und Note im Titel.


## Projekt aufbau

### 1 Konfigurationsdatei *.env*

Beispielsdatei:
```
USERNAME="Maq911"
PASSWORD="passwort123"

EMAIL_USER=email_issuer@gmail.com
EMAIL_PASS=xxxxxxxxxxxxxxxx
```

### 2. Python umgebung aufbauen

``` bash
# 1. Viruelles Environment erstellen
python3 -m venv .venv

# 2. In das Environment wechseln
source .venv/bin/activate

# 3. Dependencies installieren
pip install pypdf python-dotenv playwright
playwright install chromium
```
---

## Verwendung
### 1. Manuelle Verwendung
``` bash
# 1. Im Verzeichnis "Bachelorarbeit-Note"
chmod +x operator.bash
./operator.bash
```

### 2. Automatisiert mit CRON
``` bash
# 1. Cronjobs öffnen
crontab -e
# 2. Neuen Eintrag erstellen (Rennt Alle 5 minuten)
*/5 * * * * /home/Automations/Bachelorarbeit-Note/operator.bash > /home/Automations/Bachelorarbeit-Note/jobs.log 2>&1
```

