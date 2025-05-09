#!/bin/bash

# === Konfiguration ===
PYTHON_SCRIPT="/home/findus/Dokumente/Projekte/NBDS/Input/crawler0_script.py"
LOGFILE="/home/findus/Dokumente/Projekte/NBDS/logs/crawler_log.txt"
JSONLOG="/home/findus/Dokumente/Projekte/NBDS/logs/crawler_log.jsonl"
MAXLOGSIZE=51200  # Max 50KB für Rotation
EMAIL="deinname@example.com"  # Für Mailbenachrichtigung (optional)

# === Farben ===
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# === Zeitstempel ===
timestamp=$(date '+%Y-%m-%d %H:%M:%S')
iso_time=$(date -Iseconds)

# === Log-Verzeichnis sicherstellen ===
mkdir -p "$(dirname "$LOGFILE")"

# === Logrotation ===
if [ -f "$LOGFILE" ] && [ $(stat -c%s "$LOGFILE") -ge $MAXLOGSIZE ]; then
    mv "$LOGFILE" "$LOGFILE.bak_$(date +%s)"
fi

# === Endlosschleife für 3-Stunden-Wiederholung ===
while true; do
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')  # Zeitstempel aktualisieren
    iso_time=$(date -Iseconds)  # ISO-Zeit aktualisieren

    # === Ausführung starten ===
    echo -e "${YELLOW}[$timestamp] Starte Python-Crawler...${NC}"
    echo "🕒 [$timestamp] Start" | tee -a "$LOGFILE"

    # JSON Log init
    echo "{\"timestamp\": \"$iso_time\", \"status\": \"start\"}" | tee -a "$JSONLOG"

    # === Python-Script ausführen mit unbuffered Ausgabe ===
    python3 -u "$PYTHON_SCRIPT" 2>&1 | tee -a "$LOGFILE"

    exit_code=$?

    # === Ergebnis prüfen ===
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}[$timestamp] ✅ Erfolgreich ausgeführt${NC}" | tee -a "$LOGFILE"
        echo "✅ [$timestamp] Erfolgreich" | tee -a "$LOGFILE"
        echo "{\"timestamp\": \"$iso_time\", \"status\": \"success\"}" | tee -a "$JSONLOG"
    else
        echo -e "${RED}[$timestamp] ❌ Fehler beim Ausführen${NC}" | tee -a "$LOGFILE"
        echo "❌ [$timestamp] Fehler beim Crawler" | tee -a "$LOGFILE"
        echo "{\"timestamp\": \"$iso_time\", \"status\": \"error\"}" | tee -a "$JSONLOG"

        # Optional: E-Mail bei Fehler
        # echo -e "Fehler im Crawler-Script um $timestamp.\nSiehe Log: $LOGFILE" | mail -s "Crawler Fehler" $EMAIL
    fi

    # === 3 Stunden warten ===
    echo -e "${YELLOW}[$timestamp] Warte 3 Stunden bevor der Crawler erneut gestartet wird...${NC}"
    sleep 10800  # 3 Stunden in Sekunden (3 * 60 * 60)
done
