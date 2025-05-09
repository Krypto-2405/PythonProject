import os
import csv
from bs4 import BeautifulSoup


# Funktion zum Extrahieren von Keywords aus HTML-Dateien und Speichern in einer CSV-Datei
def extract_news_keywords_from_html_files(html_directory, output_csv_file):
    keywords_data = []  # Liste, um die Keywords zu speichern

    # Durchlaufe alle HTML-Dateien im angegebenen Verzeichnis
    for html_file in os.listdir(html_directory):
        if html_file.endswith('.html'):  # Stelle sicher, dass es eine HTML-Datei ist
            html_path = os.path.join(html_directory, html_file)
            try:
                with open(html_path, 'r', encoding='utf-8', errors='ignore') as file:
                    soup = BeautifulSoup(file.read(), 'html.parser')

                    # Suche nach dem meta-Tag mit den news_keywords
                    meta_keywords_tag = soup.find('meta', attrs={'name': 'news_keywords'})
                    if meta_keywords_tag and 'content' in meta_keywords_tag.attrs:
                        keywords = meta_keywords_tag['content']
                        keywords_data.append({'file': html_file, 'keywords': keywords})
                    else:
                        keywords_data.append({'file': html_file, 'keywords': 'Keine Keywords gefunden'})
            except Exception as e:
                print(f"Fehler beim Verarbeiten der Datei {html_file}: {e}")

    # Speichern der gesammelten Keywords in der CSV-Datei
    with open(output_csv_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Dateiname', 'Keywords']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()  # Schreibe die Kopfzeile (Header)
        for entry in keywords_data:
            writer.writerow({'Dateiname': entry['file'], 'Keywords': entry['keywords']})

    print(f"Keywords wurden in '{output_csv_file}' gespeichert.")


# Verzeichnisse und Dateipfade
html_directory = "/home/findus/Dokumente/PythonProject/ATD/Output/html_files"  # Pfad zu den HTML-Dateien
output_csv_file = "/home/findus/Dokumente/PythonProject/ATD/Output/news_keywords_output.csv"  # Ausgabedatei für Keywords (CSV)

# Keywords extrahieren und speichern
extract_news_keywords_from_html_files(html_directory, output_csv_file)
