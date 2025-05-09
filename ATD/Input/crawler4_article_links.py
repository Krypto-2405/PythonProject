


import requests
from bs4 import BeautifulSoup
import os

# Funktion zum Extrahieren und Speichern der Artikel-Links
def scrape_article_links(base_url, save_directory, max_pages=10):
    try:
        links = set()  # Ein Set speichert nur eindeutige Links
        
        # Schleife über die Seiten von 1 bis max_pages
        for page_num in range(1, max_pages + 1):
            # URL für die aktuelle Seite (z.B. /p1/, /p2/, ...)
            page_url = f"{base_url}/p{page_num}/" if page_num > 1 else base_url
            
            print(f"Verarbeite Seite: {page_url}")
            response = requests.get(page_url)
            response.raise_for_status()  # Sicherstellen, dass die Anfrage erfolgreich war
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Alle Artikel-Links extrahieren (wir suchen nach 'a'-Tags mit der entsprechenden Klasse)
            article_links = soup.find_all('a', class_='text-black dark:text-shade-lightest block')
            
            # Schleife über alle gefundenen Links und Hinzufügen zur Menge
            for link in article_links:
                article_url = link.get('href')
                
                # Stelle sicher, dass der Link eine vollständige URL ist
                if article_url and not article_url.startswith('http'):
                    article_url = 'https://www.spiegel.de' + article_url  # Falls der Link relativ ist
                
                links.add(article_url)  # Link zur Menge (Set) hinzufügen
        
        # Speichern der Links in einer Textdatei
        links_file_path = os.path.join(save_directory, 'article_links.txt')
        with open(links_file_path, 'w', encoding='utf-8') as links_file:
            for idx, link in enumerate(links):
                links_file.write(link + '\n')  # Jeden Link in eine neue Zeile
                print(f"[{idx + 1}] Link gespeichert: {link}")
    
    except requests.exceptions.RequestException as e:
        print(f"Fehler beim Abrufen der Seite {base_url}: {e}")

# Hauptcode
base_url = "https://www.spiegel.de/wissenschaft/"  # URL der Wissenschafts-Rubrik
save_directory = "/home/findus/Dokumente/PythonProject/ATD/Output/txt_links"  # Verzeichnis zum Speichern der Textdatei mit Links

os.makedirs(save_directory, exist_ok=True)  # Falls das Verzeichnis noch nicht existiert

# Alle Artikel-Links extrahieren und speichern
scrape_article_links(base_url, save_directory)
