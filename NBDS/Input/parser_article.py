import os

# Verzeichnisse definieren
input_directory = "/home/findus/Dokumente/PythonProject/NBDS/Output/article"
output_file = "/home/findus/Dokumente/PythonProject/NBDS/Output/keyword_hits.txt"

# Schlüsselwörter
keywords = [input("Keywords:")]

# Datei zur Ergebnisspeicherung öffnen
with open(output_file, 'w', encoding='utf-8') as result_file:
    result_file.write("Keyword-Suche in Artikeln\n")
    result_file.write("="*50 + "\n\n")

    for filename in os.listdir(input_directory):
        if filename.endswith(".txt"):
            filepath = os.path.join(input_directory, filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                lines = file.readlines()

            # Treffer pro Datei sammeln
            keyword_hits = {}
            context_lines = []

            for i, line in enumerate(lines):
                for keyword in keywords:
                    if keyword.lower() in line.lower():
                        keyword_hits[keyword] = keyword_hits.get(keyword, 0) + 1
                        context_lines.append(f"  Zeile {i+1}: {line.strip()}")

            if keyword_hits:
                result_file.write(f"📄 Datei: {filename}\n")
                for k, v in keyword_hits.items():
                    result_file.write(f"  - {k}: {v}x\n")
                if context_lines:
                    result_file.write("  Kontext:\n")
                    for c in context_lines:
                        result_file.write(c + "\n")
                result_file.write("\n")

print(f"\n✅ Suche abgeschlossen. Ergebnisse gespeichert in:\n{output_file}")
