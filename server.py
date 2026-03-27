# pip install flask flask-cors mysql-connector-python

from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)  # Erlaubt HTML-Seite den Zugriff

# ─── FESTE KONFIGURATION ───────────────────
DB_HOST = "192.168.1.100"   # <- deine feste IP
DB_PORT = 3306               # <- dein fester Port
DB_NAME = "meine_datenbank"  # <- deine Datenbank
NEUES_PASSWORT = "TestPasswort"
# ───────────────────────────────────────────


@app.route("/rotate", methods=["POST"])
def rotate():
    # Daten aus dem HTML-Formular empfangen
    daten = request.json
    eingabe_user = daten.get("user")
    eingabe_pass = daten.get("password")

    if not eingabe_user or not eingabe_pass:
        return jsonify({"erfolg": False, "nachricht": "User oder Passwort fehlt!"}), 400

    # Schritt 1: Mit DB verbinden (Login prüfen)
    try:
        verbindung = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=eingabe_user,
            password=eingabe_pass
        )
    except mysql.connector.Error as fehler:
        return jsonify({"erfolg": False, "nachricht": f"Login fehlgeschlagen: {fehler}"}), 401

    # Schritt 2: Passwort ändern
    try:
        cursor = verbindung.cursor()
        sql = f"ALTER USER '{eingabe_user}'@'%' IDENTIFIED BY '{NEUES_PASSWORT}'"
        cursor.execute(sql)
        cursor.execute("FLUSH PRIVILEGES")
        return jsonify({"erfolg": True, "nachricht": f"Passwort für '{eingabe_user}' erfolgreich geändert!"})

    except mysql.connector.Error as fehler:
        return jsonify({"erfolg": False, "nachricht": f"Fehler beim Ändern: {fehler}"}), 500

    finally:
        if verbindung.is_connected():
            cursor.close()
            verbindung.close()


if __name__ == "__main__":
    app.run(port=5000, debug=True)
    # Öffne: http://localhost:5000
