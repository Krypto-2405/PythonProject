import requests
from bs4 import BeautifulSoup
import os
import hashlib
from datetime import datetime
import csv

# Funktion zum Schreiben in die CSV-Logdatei
def log_article_to_csv(csv_path, data):
    file_exists = os.path.exists(csv_path)
    with open(csv_path, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=[
            'Titel', 'URL', 'Hash', 'Revision', 'Published Time',
            'Last Modified', 'Modified Time', 'Keywords',
            'Autor', 'Lesedauer', 'Text-Dateiname', 'HTML-Dateiname'
        ])
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)

# Funktion zum Erzeugen eines Dateinamens mit Revision
def generate_filename(title, url_hash, revision, extension):
    return f"{title}_{url_hash}_rev{revision}{extension}"

# Funktion zum Extrahieren von Metadaten
def extract_metadata(soup):
    def get_meta_content(attrs):
        tag = soup.find('meta', attrs=attrs)
        return tag.get('content') if tag else ''

    # Metadaten extrahieren
    published = get_meta_content({'property': 'article:published_time'})
    modified = get_meta_content({'property': 'article:modified_time'})
    keywords = [tag['content'] for tag in soup.find_all('meta', attrs={'property': 'article:tag'})]
    autor = get_meta_content({'name': 'twitter:data1'})
    lesedauer = get_meta_content({'name': 'twitter:data2'})

    return published, modified, keywords, autor, lesedauer

# Hauptfunktion für einen Artikel
def scrape_article(url, article_dir, html_dir, csv_log_path):
    try:
        os.makedirs(article_dir, exist_ok=True)
        os.makedirs(html_dir, exist_ok=True)

        url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()[:6]
        existing_files = [f for f in os.listdir(html_dir) if url_hash in f and f.endswith(".html")]
        highest_revision = 0
        last_metadata = {}

        # Überprüfen der vorhandenen Dateien und Metadaten
        for file in existing_files:
            rev_str = file.split("_rev")[-1].split(".")[0]
            try:
                highest_revision = max(highest_revision, int(rev_str))
            except ValueError:
                continue

            with open(os.path.join(html_dir, file), 'r', encoding='utf-8', errors='ignore') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
                pub, mod, keys, author, duration = extract_metadata(soup)
                last_metadata = {
                    'published': pub,
                    'modified': mod,
                    'keywords': set(keys),
                    'author': author,
                    'duration': duration
                }

        # Aktuelle Version vom Server holen
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Aktuelle Metadaten extrahieren
        published, modified, keywords, author, duration = extract_metadata(soup)

        # Prüfen, ob sich die Metadaten geändert haben
        if last_metadata and all([
            published == last_metadata['published'],
            modified == last_metadata['modified'],
            set(keywords) == last_metadata['keywords'],
            author == last_metadata['author'],
            duration == last_metadata['duration']
        ]):
            print(f"Unverändert: {url}")
            return

        # Titel aus <h1>
        h1 = soup.find('h1')
        title = h1.get_text(strip=True) if h1 else "Unbenannter_Artikel"

        # Sonderzeichen im Titel ersetzen
        for ch in ['\\', '/', ':', '*', '?', '"', '<', '>', '|']:
            title = title.replace(ch, '_')

        revision = highest_revision + 1
        html_filename = generate_filename(title, url_hash, revision, '.html')
        html_path = os.path.join(html_dir, html_filename)

        # HTML speichern
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"HTML gespeichert: {html_filename}")

        # Artikeltext extrahieren aus <div class="content">
        content_div = soup.find('div', class_='content')
        text_filename = ''
        if content_div:
            article_text = content_div.get_text(separator='\n', strip=True)
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            full_text = f"[Erstellt am: {timestamp}]\n\n{article_text}"

            text_filename = generate_filename(title, url_hash, revision, '.txt')
            text_path = os.path.join(article_dir, text_filename)

            if not os.path.exists(text_path):
                with open(text_path, 'w', encoding='utf-8') as f:
                    f.write(full_text)
                print(f"Text gespeichert: {text_filename}")
            else:
                print(f"Text bereits vorhanden: {text_filename}")
        else:
            print(f"Kein <div class='content'> gefunden für: {url}")

        # Zusätzliche Metadaten extrahieren
        published_tag = soup.find('meta', attrs={'property': 'article:published_time'})
        published_time = published_tag.get('content') if published_tag else ''

        modified_tag = soup.find('meta', attrs={'property': 'article:modified_time'})
        modified_time = modified_tag.get('content') if modified_tag else ''

        keywords_tags = soup.find_all('meta', attrs={'property': 'article:tag'})
        keywords = '; '.join(tag.get('content') for tag in keywords_tags if tag.get('content'))

        # Logging
        log_article_to_csv(csv_log_path, {
            'Titel': title,
            'URL': url,
            'Hash': url_hash,
            'Revision': revision,
            'Published Time': published_time,
            'Last Modified': '',  # für serverseitiges Last-Modified falls relevant
            'Modified Time': modified_time,
            'Keywords': keywords,
            'Autor': author,
            'Lesedauer': duration,
            'Text-Dateiname': text_filename,
            'HTML-Dateiname': html_filename
        })

    except Exception as e:
        print(f"Fehler bei {url}: {e}")

# Hauptablauf
if __name__ == "__main__":
    base_dir = "/home/findus/Dokumente/PythonProject/NBDS/Output"
    article_dir = os.path.join(base_dir, "article")
    html_dir = os.path.join(base_dir, "html_files")
    csv_log = os.path.join(base_dir, "artikel_log.csv")
    article_links_file = os.path.join(base_dir, "txt_links", "article_links.txt")

    with open(article_links_file, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]

    for idx, link in enumerate(urls):
        print(f"[{idx+1}] Verarbeite: {link}")
        scrape_article(link, article_dir, html_dir, csv_log)
