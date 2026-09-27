import re

# ---- Parameter anpassen ----
DATEI   = "beispiel.tmx"
MUSTER  = r"Climate"
MODUS   = "zeilen"      # "zeilen", "treffer" oder "ersetzen"
ERSATZ  = ""            # nur für MODUS "ersetzen"
AUSGABE = "climate.txt"
# ----------------------------

with open(DATEI, encoding="utf-8") as f:
    text = f.read()

if MODUS == "zeilen":
    ergebnis = [z for z in text.splitlines() if re.search(MUSTER, z)]
elif MODUS == "treffer":
    ergebnis = re.findall(MUSTER, text)
else:
    neu, anzahl = re.subn(MUSTER, ERSATZ, text)
    ergebnis = [neu]

with open(AUSGABE, "w", encoding="utf-8") as f:
    f.write("\n".join(ergebnis))

if MODUS == "ersetzen":
    print(anzahl, "Ersetzungen gespeichert in", AUSGABE)
else:
    print(len(ergebnis), "Treffer gespeichert in", AUSGABE)
