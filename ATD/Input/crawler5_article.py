import requests
from bs4 import BeautifulSoup
import os
import hashlib
from datetime import datetime
import csv

# Funktion zum Eintrag in die CSV-Logdatei
def log_article_to_csv(csv_path, data):
    file_exists = os.path.exists(csv_path)
    with open(csv_path, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=[
            'Titel', 'URL', 'Hash', 'Revision', 'Last Modified', 'Ist Spiegel+', 'Text-Dateiname', 'HTML-Dateiname'
        ])
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)

# Hauptfunktion zum Abrufen und Speichern eines Artikels
def scrape_article(url, article_directory, html_directory, csv_log_path):
    try:
        url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()[:6]

        # Vorhandene HTML-Dateien mit gleichem Hash suchen
        matching_files = [f for f in os.listdir(html_directory) if url_hash in f]
        existing_last_modified = None
        highest_revision = 0

        for f in matching_files:
            full_path = os.path.join(html_directory, f)
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as file:
                soup = BeautifulSoup(file.read(), 'html.parser')
                meta_tag = soup.find('meta', attrs={'name': 'last-modified'})
                if meta_tag:
                    existing_last_modified = meta_tag.get('content')
            if "_rev" in f:
                rev_part = f.split("_rev")[-1].split(".")[0]
                try:
                    highest_revision = max(highest_revision, int(rev_part))
                except ValueError:
                    pass

        # Neuesten Artikel abrufen
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        current_last_modified_tag = soup.find('meta', attrs={'name': 'last-modified'})
        current_last_modified = current_last_modified_tag.get('content') if current_last_modified_tag else None

        if existing_last_modified and existing_last_modified == current_last_modified:
            print(f"Artikel unverändert – überspringe: {url}")
            return

        # Titel und Spiegel+ Status bestimmen
        meta_title_tag = soup.find('meta', property='og:title')
        is_spiegel_plus = meta_title_tag and meta_title_tag.get('content', '').startswith('(S+)')

        article_title_tag = soup.find('h1')
        article_title = article_title_tag.get_text(strip=True) if article_title_tag else "Unbenannter_Artikel"

        invalid_chars = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
        for char in invalid_chars:
            article_title = article_title.replace(char, '_')

        if is_spiegel_plus:
            article_title = "+" + article_title

        revision_suffix = f"_rev{highest_revision + 1}" if existing_last_modified else ""
        full_title = f"{article_title}_{url_hash}{revision_suffix}"

        def get_unique_filename(directory, filename):
            counter = 1
            base_filename, extension = os.path.splitext(filename)
            while os.path.exists(os.path.join(directory, filename)):
                filename = f"{base_filename}_{counter}{extension}"
                counter += 1
            return filename

        html_filename = get_unique_filename(html_directory, f"{full_title}.html")
        with open(os.path.join(html_directory, html_filename), 'w', encoding='utf-8') as file:
            file.write(response.text)
        print(f"HTML gespeichert: {html_filename}")

        text_filename = ''
        if not is_spiegel_plus:
            article_body = soup.find('div', {'data-area': 'body'})
            if article_body:
                article_text = article_body.get_text(separator='\n', strip=True)
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                article_text = f"[Erstellt am: {timestamp}]\n\n{article_text}"
                text_filename = get_unique_filename(article_directory, f"{full_title}.txt")
                with open(os.path.join(article_directory, text_filename), 'w', encoding='utf-8') as file:
                    file.write(article_text)
                print(f"Artikeltext gespeichert: {text_filename}")
            else:
                print(f"Artikeltext nicht gefunden: {url}")

        # In CSV loggen
        log_article_to_csv(csv_log_path, {
            'Titel': article_title,
            'URL': url,
            'Hash': url_hash,
            'Revision': highest_revision + 1 if existing_last_modified else 0,
            'Last Modified': current_last_modified if current_last_modified else '',
            'Ist Spiegel+': is_spiegel_plus,
            'Text-Dateiname': text_filename,
            'HTML-Dateiname': html_filename
        })

    except requests.exceptions.RequestException as e:
        print(f"Fehler beim Abrufen des Artikels {url}: {e}")

# Hauptcode
article_links_file = "/home/findus/Dokumente/Projekte/ATD/Output/txt_links/article_links.txt"
base_directory = "/home/findus/Dokumente/Projekte/ATD/Output"
article_directory = os.path.join(base_directory, 'article')
html_directory = os.path.join(base_directory, 'html_files')
csv_log_path = os.path.join(base_directory, 'artikel_log.csv')

os.makedirs(article_directory, exist_ok=True)
os.makedirs(html_directory, exist_ok=True)

with open(article_links_file, 'r', encoding='utf-8') as file:
    article_links = [line.strip() for line in file if line.strip()]

for idx, url in enumerate(article_links):
    url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()[:6]
    print(f"[{idx + 1}] Verarbeite Artikel: {url}")
    scrape_article(url, article_directory, html_directory, csv_log_path)
