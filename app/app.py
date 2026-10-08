from flask import Flask, request
import sqlite3
import subprocess

app = Flask(__name__)

# VULNERABILITE 1 : secrets en dur (detectes par gitleaks)
GITLAB_TOKEN = "glpat-AbCdEfGhIjKlMnOpQrSt"
DB_PASSWORD = "admin123"

def get_db():
    conn = sqlite3.connect("users.db")
    conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER, name TEXT)")
    return conn

@app.route("/")
def index():
    return "Cyber Sentinel - application de demonstration"

# VULNERABILITE 2 : injection SQL
@app.route("/user")
def user():
    name = request.args.get("name", "")
    conn = get_db()
    query = "SELECT * FROM users WHERE name = '" + name + "'"
    return str(conn.execute(query).fetchall())

# VULNERABILITE 3 : injection de commande
@app.route("/ping")
def ping():
    host = request.args.get("host", "127.0.0.1")
    return "<pre>" + subprocess.getoutput("ping -c 1 " + host) + "</pre>"

if __name__ == "__main__":
    # VULNERABILITE 4 : debug actif
    app.run(host="0.0.0.0", port=5000, debug=True)
