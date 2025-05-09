#Rubriken durchsuchen und Artikel links speichern
from bs4 import BeautifulSoup
import os

# Eingabe- und Ausgabeverzeichnisse
input_dir = "/home/findus/Dokumente/PythonProject/NBDS/Output/html/rubriken"
output_dir = "/home/findus/Dokumente/PythonProject/NBDS/Output/txt_links"
os.makedirs(output_dir, exist_ok=True)

# Ziel-Textdatei
output_file = os.path.join(output_dir, "alle_artikel_links.txt")

# Funktion zur Verarbeitung einer Datei
def extract_article_links(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    links = []
    articles = soup.find_all("div", class_="single_post")
    for article in articles:
        a_tag = article.find("a", href=True)
        if a_tag:
            link = a_tag["href"]
            links.append(link)
    return links

# Alle HTML-Dateien im Eingabeverzeichnis verarbeiten
with open(output_file, "w", encoding="utf-8") as f_out:
    for filename in os.listdir(input_dir):
        if filename.endswith(".html"):
            filepath = os.path.join(input_dir, filename)
            category = os.path.splitext(filename)[0]  # Dateiname ohne .html
            article_links = extract_article_links(filepath)

            if article_links:
                f_out.write(f"### {category} ###\n")
                for link in article_links:
                    f_out.write(link + "\n")
                f_out.write("\n")

print(f"Fertig. Artikel-Links gespeichert in: {output_file}")
