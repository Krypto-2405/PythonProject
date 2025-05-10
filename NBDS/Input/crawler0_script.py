import subprocess
import os

# Das Verzeichnis zu den Skripten
directory = "/home/findus/Dokumente/PythonProject/NBDS/Input"

# Wechsle in das Verzeichnis, in dem die Skripte liegen
os.chdir(directory)

# Liste der Skripte, die du ausführen möchtest
scripts = [
    "crawler1_meta.py",
    "crawler2_themen_txt.py",
    "crawler3_html_write.py",
    "crawler4_article_links.py",
    "crawler5_metadaten.py",
]

# Alle Skripte nacheinander ausführen
for script in scripts:
    try:
        subprocess.run(["python3", script], check=True)
        print(f"{script} wurde ausgeführt.")
    except subprocess.CalledProcessError as e:
        print(f"Fehler beim Ausführen von {script}: {e}")
