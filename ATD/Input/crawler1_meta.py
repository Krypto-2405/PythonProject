# Ruft die Startseite auf und speichert sie als html Datei


import requests
from bs4 import BeautifulSoup
import os

# Zielverzeichnis definieren
directory = "/home/findus/Dokumente/PythonProject/ATD/Output/html"

# Falls das Verzeichnis nicht existiert, erstellen
os.makedirs(directory, exist_ok=True)

# Dateiname mit vollständigem Pfad setzen
filename = os.path.join(directory, "meta_output.html")

def scrape_and_save(url, filename):
    try:
        # Webseite abrufen
        response = requests.get(url)
        response.raise_for_status()  # Fehler abfangen
        
        # HTML mit BeautifulSoup parsen
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Kompletter HTML-Quelltext
        html_text = soup.prettify()
        
        # In Datei speichern
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(html_text)
        
        print(f"Inhalt erfolgreich in {filename} gespeichert.")
    except requests.exceptions.RequestException as e:
        print(f"Fehler beim Abrufen der Webseite: {e}")

# Beispielaufruf
url = "https://www.spiegel.de/politik/deutschland/"
scrape_and_save(url, filename)