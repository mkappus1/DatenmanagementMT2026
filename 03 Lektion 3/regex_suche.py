# regex_suche.py
# Datenmanagement für die MT – Lektion 3 (und Lektion 4)
#
# Passen Sie nur die beiden Werte in diesem Block an:

DATEINAME = "segmente.txt"
MUSTER = r"\d+"          # <- Ihr Muster aus regex101

# Erst ab Lektion 4 – bis dahin nichts verändern:
MODUS   = "suchen"       # "suchen" oder "ersetzen"
ERSATZ  = ""             # nur für MODUS "ersetzen"
AUSGABE = ""             # nur für MODUS "ersetzen": Name der neuen Datei

# --- Ab hier nichts mehr verändern ---
import re
import sys

try:
    with open(DATEINAME, encoding="utf-8") as f:
        text = f.read()
except FileNotFoundError:
    sys.exit(f"Die Datei '{DATEINAME}' wurde nicht gefunden. Liegt sie im selben Ordner wie das Skript?")
except UnicodeDecodeError:
    sys.exit(f"Die Datei '{DATEINAME}' ist nicht in UTF-8 gespeichert.")

try:
    muster = re.compile(MUSTER)
except re.error as fehler:
    sys.exit(f"Das Muster '{MUSTER}' ist ungültig: {fehler}")

if MODUS == "suchen":
    zeilen = text.splitlines()
    anzahl_zeilen = 0
    anzahl_treffer = 0
    for nummer, zeile in enumerate(zeilen, start=1):
        gefunden = [m.group() for m in muster.finditer(zeile) if m.group()]
        if gefunden:
            anzahl_zeilen += 1
            anzahl_treffer += len(gefunden)
            print(f"Zeile {nummer}: {zeile}")
            print(f"   Treffer: {', '.join(gefunden)}")
    print(f"\n{anzahl_zeilen} von {len(zeilen)} Zeilen enthalten das Muster '{MUSTER}'.")
    print(f"Treffer insgesamt: {anzahl_treffer}")

elif MODUS == "ersetzen":
    if not AUSGABE:
        sys.exit("Bitte bei AUSGABE den Namen der neuen Datei angeben.")
    if AUSGABE == DATEINAME:
        sys.exit("AUSGABE darf nicht gleich heissen wie DATEINAME – sonst wird Ihre Originaldatei überschrieben.")
    neu, anzahl = muster.subn(ERSATZ, text)
    with open(AUSGABE, "w", encoding="utf-8") as f:
        f.write(neu)
    print(f"{anzahl} Ersetzungen gespeichert in {AUSGABE}")

else:
    sys.exit(f'MODUS muss "suchen" oder "ersetzen" sein, nicht "{MODUS}".')
