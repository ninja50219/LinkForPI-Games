from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import mysql.connector
import os

app = Flask(__name__, static_folder=".")
CORS(app)

# ── FESTE KONFIGURATION ──────────────────────────────────────
# Trage hier deine echten Daten ein!
DB_HOST     = os.environ.get("DB_HOST",  "192.168.1.100")
DB_PORT     = int(os.environ.get("DB_PORT", 3306))
DB_NAME     = os.environ.get("DB_NAME",  "meine_datenbank")
NEUES_PW    = os.environ.get("NEUES_PW", "TestPasswort")
# ─────────────────────────────────────────────────────────────


# index.html ausliefern wenn jemand die Seite öffnet
@app.route("/")
def index():
    return send_from_directory(".", "index.html")


# HTML ruft diese Route auf wenn User auf Button klickt
@app.route("/rotate", methods=["POST"])
def rotate():
    daten = request.json
    eingabe_user = daten.get("user", "").strip()
    eingabe_pass = daten.get("password", "")

    if not eingabe_user or not eingabe_pass:
        return jsonify({"erfolg": False, "nachricht": "User oder Passwort fehlt!"}), 400

    # Schritt 1: Mit DB verbinden (prüft ob Login korrekt ist)
    try:
        verbindung = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=eingabe_user,
            password=eingabe_pass,
            connection_timeout=5
        )
    except mysql.connector.Error as e:
        return jsonify({"erfolg": False, "nachricht": f"Login fehlgeschlagen: {e}"}), 401

    # Schritt 2: Passwort ändern
    try:
        cursor = verbindung.cursor()
        cursor.execute(f"ALTER USER '{eingabe_user}'@'%' IDENTIFIED BY '{NEUES_PW}'")
        cursor.execute("FLUSH PRIVILEGES")
        return jsonify({"erfolg": True, "nachricht": f"Passwort für '{eingabe_user}' erfolgreich geändert!"})

    except mysql.connector.Error as e:
        return jsonify({"erfolg": False, "nachricht": f"Fehler beim Ändern: {e}"}), 500

    finally:
        if verbindung.is_connected():
            cursor.close()
            verbindung.close()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
