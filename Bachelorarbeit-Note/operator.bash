#!/bin/bash

# 1. In das Hauptverzeichnis deines Projekts wechseln
cd /home/pi/Automations/Bachelorarbeit-Note

# 2. Das virtuelle Environment aktivieren 
source venv/bin/activate

# 2. Die Python-Skripte ausführen 
python3 Scraper.py
python3 EmailVersand.py