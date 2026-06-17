# Drive Or Die - DBI (Backend)

Hier findest du die Anleitung, wie du das FastAPI-Backend und die Datenbank von **Drive Or Die** auf deinem lokalen PC startest.

## Voraussetzungen
Bevor du startest, brauchst du folgende Programme auf deinem PC:
- **Python** (Version 3.10 oder neuer)
- Einen Code-Editor wie **PyCharm** oder **VS Code**

## Projekt starten (Schritt-für-Schritt)

1. **Repository herunterladen:**
   - Klicke oben rechts auf den grünen Button **Code** und wähle **Download ZIP** aus.
   - Entpacke die ZIP-Datei auf deinem PC.
   - *(Alternativ über Git Bash: `git clone https://github.com/alinab399/DriveOrDie_DBI.git`)*

2. **Ordner öffnen & Terminal öffnen:**
   - Öffne den entpackten Projektordner in deinem Editor (z. B. PyCharm oder VS Code).
   - Öffne das integrierte Terminal im Editor.

3. **Virtuelle Umgebung erstellen (Empfohlen):**
   - Gib folgenden Befehl im Terminal ein, um eine saubere Python-Umgebung zu erstellen:
     ```bash
     python -m venv venv
     ```
   - Aktiviere die Umgebung:
     - **Windows (PowerShell):** `.\venv\Scripts\Activate.ps1`
     - **Windows (CMD):** `.\venv\Scripts\activate.bat`

4. **Benötigte Pakete (Requirements) installieren:**
   - Installiere alle Bibliotheken (FastAPI, SQLAlchemy, uvicorn, etc.) mit diesem Befehl:
     ```bash
     pip install -r requirements.txt
     ```

5. **Datenbank initialisieren:**
   - Bevor die API läuft, muss die SQLite-Datenbankdatei und die Tabellen einmalig erstellt werden. Führe dazu eure `init_db.py` aus:
     ```bash
     python init_db.py
     ```

6. **FastAPI Server starten:**
   - Starte den Uvicorn-Server mit folgendem Befehl (Hinweis: Falls eure Haupt-Python-Datei nicht `main.py` heißt, ersetze das Wort `main` vor dem Doppelpunkt durch euren Dateinamen):
     ```bash
     uvicorn main:app --reload
     ```
   - Das Backend läuft jetzt lokal unter: [http://127.0.0.1:8000](http://127.0.0.1:8000)
   - Die interaktive API-Dokumentation (Swagger UI) findest du direkt unter: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
