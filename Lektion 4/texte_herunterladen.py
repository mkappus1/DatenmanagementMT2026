# texte_herunterladen.py
# Datenmanagement für die MT – Lektion 4: Webscraping mit trafilatura
#
# Dieses Skript lädt den Haupttext von einer oder mehreren Webseiten herunter
# und speichert ihn in einer Textdatei: eine Zeile pro Absatz bzw. Aufzählungspunkt.
# Menüs, Suchfelder, Fusszeilen usw. (Boilerplate) werden von trafilatura entfernt.
#
# So verwenden Sie das Skript:
#   1. Passen Sie unten die drei Parameter an (nur den Text zwischen den Anführungszeichen).
#   2. Speichern Sie die Datei.
#   3. Starten Sie das Skript im Terminal:
#        Mac:      python3 texte_herunterladen.py
#        Windows:  python texte_herunterladen.py

# ---- Parameter anpassen ----
QUELLE  = "https://www.ebgb.admin.ch/de/inklusions-initiative-in-leichter-sprache-die-antwort-vom-bundesrat-in-leichter-sprache"
AUSGABE = "inklusion_de.txt"
PAUSE   = 2      # Sekunden Wartezeit zwischen zwei Seiten
# ----------------------------

# QUELLE:  eine einzelne Webadresse (beginnt mit https://)
#          ODER der Name einer Textdatei mit mehreren Webadressen, eine pro Zeile.
#          Zeilen, die nicht mit http beginnen, werden ignoriert (z. B. Notizen mit #).
# AUSGABE: Name der Textdatei, in die der Text geschrieben wird.
#          Achtung: Eine bestehende Datei mit diesem Namen wird überschrieben.
# PAUSE:   Wartezeit in Sekunden zwischen zwei Seiten, um den Server zu schonen.


# =====================================================================
# Ab hier müssen Sie nichts mehr ändern.
# =====================================================================

import sys
import time
from pathlib import Path

try:
    import trafilatura
except ImportError:
    print("Fehler: trafilatura ist noch nicht installiert.")
    print("Bitte zuerst im Terminal installieren:")
    print("  Mac:      python3 -m pip install trafilatura")
    print("  Windows:  python -m pip install trafilatura")
    sys.exit(1)

# Dateien werden immer im Ordner gesucht und gespeichert, in dem dieses Skript liegt.
ORDNER = Path(__file__).resolve().parent


def ist_webadresse(text):
    return text.strip().lower().startswith(("http://", "https://"))


def webadressen_einlesen(quelle):
    """Gibt eine Liste von Webadressen zurück – entweder die eine Adresse
    oder alle Adressen aus der angegebenen Textdatei."""
    if ist_webadresse(quelle):
        return [quelle.strip()]

    datei = ORDNER / quelle
    if not datei.is_file():
        print(f"Fehler: Die Datei '{quelle}' wurde nicht gefunden.")
        print(f"Sie muss im selben Ordner liegen wie das Skript: {ORDNER}")
        sys.exit(1)

    # utf-8-sig: funktioniert auch mit Dateien aus dem Windows-Editor
    zeilen = datei.read_text(encoding="utf-8-sig").splitlines()
    adressen = [z.strip() for z in zeilen if ist_webadresse(z)]

    if not adressen:
        print(f"Fehler: In der Datei '{quelle}' steht keine Webadresse.")
        print("Jede Zeile sollte mit https:// beginnen.")
        sys.exit(1)
    return adressen


# Bereiche, die nie zum Haupttext gehören: Such-Overlays, Seitenkopf und -fuss
# (ausser innerhalb eines Artikels), Navigation, Schaltflächen, Formulare.
BOILERPLATE = (
    "//*[@role='search'] | //form | //nav | //button"
    " | //header[not(ancestor::article) and not(ancestor::main)]"
    " | //footer[not(ancestor::article) and not(ancestor::main)]"
)


def html_vorbereiten(html):
    """Räumt das HTML auf, bevor trafilatura es analysiert.
    Hilft bei Seiten mit Suchfenstern, Menüs und aufklappbaren Abschnitten."""
    try:
        from lxml import html as lxml_html
        dokument = lxml_html.fromstring(html)
    except Exception:
        return html  # im Zweifel unverändert weitergeben

    # 1. Offensichtliche Boilerplate entfernen
    for element in dokument.xpath(BOILERPLATE):
        if element.getparent() is not None:
            element.drop_tree()

    # 2. Zugeklappte Abschnitte (Akkordeons) sichtbar machen
    for element in dokument.xpath("//*[@aria-hidden='true']"):
        del element.attrib["aria-hidden"]

    # 3. Titel der aufklappbaren Abschnitte als Zwischentitel behandeln
    for element in dokument.xpath("//label[@aria-controls] | //summary"):
        element.tag = "h3"

    return lxml_html.tostring(dokument, encoding="unicode")


def text_herunterladen(adresse):
    """Lädt eine Webseite herunter und gibt den Haupttext zurück.
    Gibt None zurück, wenn etwas nicht geklappt hat (mit Meldung)."""
    html = trafilatura.fetch_url(adresse)
    if html is None:
        print("      Fehler: Seite konnte nicht geladen werden.")
        print("      Bitte Adresse im Browser testen und Internetverbindung prüfen.")
        return None

    text = trafilatura.extract(
        html_vorbereiten(html),
        output_format="txt",
        include_comments=False,   # keine Leserkommentare (z. B. bei Blogs)
        include_tables=True,      # Tabellen-Inhalte behalten
    )
    if not text or not text.strip():
        print("      Fehler: Kein Text gefunden.")
        print("      trafilatura konnte auf dieser Seite keinen Haupttext erkennen.")
        return None

    # Leerzeilen und überflüssige Leerzeichen am Zeilenende entfernen
    zeilen = [z.rstrip() for z in text.splitlines() if z.strip()]

    # Seitentitel als erste Zeile ergänzen, falls trafilatura ihn nicht mitliefert
    metadaten = trafilatura.extract_metadata(html)
    titel = metadaten.title.strip() if metadaten and metadaten.title else ""
    if titel and zeilen[0] != titel:
        zeilen.insert(0, titel)

    return "\n".join(zeilen)


def main():
    try:
        pause = float(PAUSE)
    except (TypeError, ValueError):
        print("Fehler: PAUSE muss eine Zahl sein, z. B. PAUSE = 2")
        sys.exit(1)

    adressen = webadressen_einlesen(QUELLE)
    aus_liste = not ist_webadresse(QUELLE)
    anzahl = len(adressen)

    print(f"{anzahl} Seite(n) werden heruntergeladen ...\n")

    texte = []
    for nr, adresse in enumerate(adressen, start=1):
        if nr > 1:
            time.sleep(pause)  # Fairness: Server nicht überlasten

        print(f"[{nr}/{anzahl}] {adresse}")
        text = text_herunterladen(adresse)
        if text is None:
            continue

        print(f"      OK: {len(text.splitlines())} Zeilen Text")
        if aus_liste:
            # Bei mehreren Seiten: Herkunft über jedem Text vermerken
            texte.append(f"### {adresse}\n{text}")
        else:
            texte.append(text)

    print()
    if not texte:
        print("Es konnte keine Seite gespeichert werden. Die Ausgabedatei wurde nicht angelegt.")
        sys.exit(1)

    # Umlaute und Akzente korrekt speichern:
    # Unter Windows mit BOM (utf-8-sig), damit auch `cat` in der PowerShell
    # die Datei richtig anzeigt. Auf dem Mac normales UTF-8.
    kodierung = "utf-8-sig" if sys.platform.startswith("win") else "utf-8"
    ziel = ORDNER / AUSGABE
    ziel.write_text("\n".join(texte) + "\n", encoding=kodierung)
    print(f"Fertig: {len(texte)} von {anzahl} Seite(n) gespeichert in {AUSGABE}")


if __name__ == "__main__":
    main()
