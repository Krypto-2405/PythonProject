from bs4 import BeautifulSoup
import os
import requests

# Eingabe- und Ausgabeverzeichnisse
input_dir = "/home/findus/Dokumente/PythonProject/NBDS/Output/html/rubriken"
output_dir = "/home/findus/Dokumente/PythonProject/NBDS/Output/txt_links"
os.makedirs(output_dir, exist_ok=True)

# Ziel-Textdatei
output_file = os.path.join(output_dir, "article_links.txt")

# Funktion zur Verarbeitung einer Datei und zum Extrahieren von Artikel-Links
def extract_article_links(soup):
    links = []
    articles = soup.find_all("div", class_="single_post")
    for article in articles:
        a_tag = article.find("a", href=True)
        if a_tag:
            link = a_tag["href"]
            links.append(link)
    return links

# Funktion, die die Rubriken aus dem Ordner verarbeitet
def process_category_file(category_name, category_url):
    article_links = []
    page_number = 1

    while True:
        # Die URL für die aktuelle Seite (1. Seite oder nächste Seite)
        url = f"{category_url}/page/{page_number}/" if page_number > 1 else category_url

        try:
            # HTTP-Anfrage für die aktuelle Seite
            response = requests.get(url)
            response.raise_for_status()  # Fehler, wenn die Anfrage fehlschlägt

            # BeautifulSoup für das Parsen der Seite
            soup = BeautifulSoup(response.text, "html.parser")

            # Artikel-Links von dieser Seite extrahieren
            page_links = extract_article_links(soup)
            if not page_links:
                # Keine Artikel-Links auf dieser Seite, daher stoppen wir
                break

            # Links zur Gesamtliste hinzufügen, Duplikate entfernen
            article_links.extend(link for link in page_links if link not in article_links)

            # Paginierung: Nächste Seite
            pagination = soup.find("div", class_="cpagination")
            if pagination:
                # Update: Änderung von 'text' zu 'string' um die DeprecationWarning zu vermeiden
                next_page_tag = pagination.find("a", class_="page-link", string=str(page_number + 1))
                if next_page_tag:
                    page_number += 1
                else:
                    break
            else:
                break  # Keine Paginierung mehr, daher stoppen

        except requests.exceptions.RequestException as e:
            print(f"Fehler bei der Verarbeitung der Seite {url}: {e}")
            break

    return article_links

# Alle HTML-Dateien im Rubriken-Ordner durchgehen
with open(output_file, "w", encoding="utf-8") as f_out:
    for filename in os.listdir(input_dir):
        if filename.endswith(".html"):
            filepath = os.path.join(input_dir, filename)
            category_name = os.path.splitext(os.path.basename(filepath))[0]  # Name der Rubrik ohne .html

            with open(filepath, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f, "html.parser")

            # Basis-URL der Rubrik extrahieren (wir nehmen die URL aus der HTML-Datei, keine manuelle Ergänzung)
            category_url_tag = soup.find("meta", attrs={"property": "og:url"})
            if category_url_tag:
                category_url = category_url_tag["content"]
            else:
                print(f"Warnung: Keine og:url gefunden für {category_name}")
                continue

            # Artikel-Links von allen Seiten der Rubrik extrahieren
            print(f"Verarbeite Rubrik: {category_name} (URL: {category_url})")  # Fortschrittsanzeige im Terminal
            article_links = process_category_file(category_name, category_url)

            # Links in die Datei schreiben, ohne den Haupt-Link der Rubrik
            if article_links:
                f_out.write(f"### {category_name} ###\n")
                for link in article_links:
                    if link != category_url:  # Der Haupt-Link der Rubrik wird nicht gespeichert
                        f_out.write(link + "\n")
                f_out.write("\n")

            print(f"Fertig mit der Rubrik: {category_name}, {len(article_links)} Links gefunden.")  # Anzahl der Links

print(f"Fertig. Artikel-Links gespeichert in: {output_file}")
