# Alevio Process Mining Plattform

Dies ist eine Streamlit-basierte Plattform für Process Mining.

## Starten der App

```bash
streamlit run alevio_app/main.py
```

## Projektstruktur

- `alevio_app/main.py`: Hauptdatei, steuert die Navigation und lädt die Unterseiten.
- `alevio_app/pages.py`: Enthält die Funktionen für die einzelnen Seiten (Login, Homescreen, Projekt anlegen, etc.).
- `requirements.txt`: Abhängigkeiten (Streamlit, Pandas).

## Zusammenarbeit

Ihr könnt gemeinsam an diesem Code arbeiten, indem ihr z.B. GitHub oder einen anderen Git-Server nutzt. Achtet darauf, regelmäßig zu committen und zu pushen, um Konflikte zu vermeiden.

## Hinweise
- Jede Unterseite ist als eigene Funktion in `pages.py` ausgelagert, damit Änderungen an einer Seite nicht die anderen beeinflussen.
- Die Navigation erfolgt über die Sidebar.
- Für Upload und Auswahl der Spalten wird Pandas verwendet.
