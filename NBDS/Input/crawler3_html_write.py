


import requests
from bs4 import BeautifulSoup
import os
import re

# Verzeichnis-Struktur
base_directory = "/home/findus/Dokumente/Projekte/NBDS/Output"
txt_links_directory = os.path.join(base_directory, "txt_links")
html_directory = os.path.join(base_directory, "html", "rubriken")
os.makedirs(html_directory, exist_ok=True)

# Pfad zur Datei mit den Links
file_path = os.path.join(txt_links_directory, "crawler2_themen.txt")

# URL aus beliebigem Text extrahieren (Regex)
def extract_url(text):
    match = re.search(r'https?://[^\s,]+', text)
    return match.group(0) if match else None

# HTML jeder URL speichern
def scrape_and_save(url, filename):
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        html_text = soup.prettify()

        with open(filename, 'w', encoding='utf-8') as file:
            file.write(html_text)

        print(f"[✓] Gespeichert: {filename}")
    except requests.exceptions.RequestException as e:
        print(f"[!] Fehler bei {url}: {e}")

# Alle Zeilen durchgehen
with open(file_path, 'r', encoding='utf-8') as file:
    lines = file.readlines()

for i, line in enumerate(lines):
    url = extract_url(line)
    
    if not url:
        print(f"[!] Zeile {i+1} übersprungen – keine URL erkannt.")
        continue

    # Dateiname aus URL oder Fallback
    url_part = url.rstrip('/').split('/')[-1] or f"seite_{i+1}"
    filename = os.path.join(html_directory, f"{url_part}.html")

    scrape_and_save(url, filename)
