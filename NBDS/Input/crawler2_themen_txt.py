from bs4 import BeautifulSoup
import os

# Pfade
html_file = "/home/findus/Dokumente/Projekte/NBDS/Output/html/meta_output.html"
output_dir = "/home/findus/Dokumente/Projekte/NBDS/Output/txt_links"
output_file = os.path.join(output_dir, "crawler2_themen.txt")

os.makedirs(output_dir, exist_ok=True)

def extract_links(li_elements, f_out=None, seen_urls=set()):
    for li in li_elements:
        # <a> Link finden
        a = li.find("a")
        if a and a.get("href") and a.text.strip():
            name = a.text.strip().replace("\n", " ")
            link = a["href"].strip()

            # Überprüfen, ob der Link bereits verarbeitet wurde (Duplikate verhindern)
            if link not in seen_urls:
                seen_urls.add(link)
                line = f"{name}: {link}"
                print(line)
                f_out.write(line + "\n")

        # Jetzt ALLE <ul> im <li> suchen (nicht nur direkte)
        for submenu in li.find_all("ul", recursive=False):
            extract_links(submenu.find_all("li", recursive=False), f_out=f_out, seen_urls=seen_urls)

        # UND zusätzlich prüfen, ob tiefer verschachtelte <ul class="dropdown-menu"> existieren
        dropdown = li.find("ul", class_="dropdown-menu")
        if dropdown:
            extract_links(dropdown.find_all("li"), f_out=f_out, seen_urls=seen_urls)

# Hauptlogik
with open(output_file, 'w', encoding='utf-8') as f_out:
    if not os.path.isfile(html_file):
        print(f"Fehler: Die Datei {html_file} existiert nicht.")
    else:
        with open(html_file, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")

        # Hauptmenü holen
        menu = soup.find("ul", id="menu-main-menu")
        if menu:
            extract_links(menu.find_all("li", recursive=False), f_out=f_out)
        else:
            print("Hauptmenü <ul id='menu-main-menu'> nicht gefunden.")
