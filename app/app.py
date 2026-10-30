import os
import psycopg2
from flask import Flask, request, session, redirect, render_template_string

app = Flask(__name__)
app.secret_key = "dev-secret-123"            # FAILLE 4 : secret en dur
DB_PASSWORD = "helpdesk123"                  # FAILLE 4 : secret en dur
FAKE_TOKEN = "glpat-AbCdEfGhIjKlMnOpQrSt"    # faux token pour gitleaks


def db():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "db"),
        dbname=os.getenv("DB_NAME", "helpdesk"),
        user=os.getenv("DB_USER", "helpdesk"),
        password=os.getenv("DB_PASSWORD", DB_PASSWORD),
    )


def init_db():
    c = db()
    cur = c.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, username TEXT UNIQUE, password TEXT, role TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS tickets (id SERIAL PRIMARY KEY, owner TEXT, title TEXT, body TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS comments (id SERIAL PRIMARY KEY, ticket_id INT, author TEXT, text TEXT)")
    cur.execute("SELECT count(*) FROM users")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO users (username,password,role) VALUES ('alice','alice123','user'),('bob','bob123','user'),('agent1','agent123','agent'),('admin','admin123','admin')")
        cur.execute("INSERT INTO tickets (owner,title,body) VALUES ('alice','Imprimante HS','Salle 2'),('bob','Acces VPN','Mot de passe temporaire: Tmp-2026')")
    c.commit()
    c.close()


@app.route("/")
def index():
    return "HelpDesk - application de demonstration"


@app.route("/login", methods=["POST"])
def login():
    u = request.form.get("username", "")
    p = request.form.get("password", "")
    c = db()
    cur = c.cursor()
    # FAILLE 1 : injection SQL
    cur.execute("SELECT username, role FROM users WHERE username='" + u + "' AND password='" + p + "'")
    row = cur.fetchone()
    c.close()
    if row:
        session["user"], session["role"] = row
        return "connecte: %s (%s)" % row
    return "echec", 401


@app.route("/tickets")
def tickets():
    if "user" not in session:
        return "non connecte", 401
    c = db()
    cur = c.cursor()
    cur.execute("SELECT id, title FROM tickets WHERE owner=%s", (session["user"],))
    rows = cur.fetchall()
    c.close()
    return str(rows)


@app.route("/ticket/<int:tid>")
def ticket(tid):
    if "user" not in session:
        return "non connecte", 401
    c = db()
    cur = c.cursor()
    # FAILLE 2 : IDOR, aucun controle du proprietaire
    cur.execute("SELECT id, owner, title, body FROM tickets WHERE id=%s", (tid,))
    t = cur.fetchone()
    cur.execute("SELECT author, text FROM comments WHERE ticket_id=%s", (tid,))
    cs = cur.fetchall()
    c.close()
    if not t:
        return "introuvable", 404
    html = "<h2>%s</h2><p>%s</p><hr>" % (t[2], t[3])
    for a, tx in cs:
        html += "<p><b>%s</b>: %s</p>" % (a, tx)   # FAILLE 3 : XSS stocke
    return render_template_string(html)


@app.route("/ticket/<int:tid>/comment", methods=["POST"])
def comment(tid):
    if "user" not in session:
        return "non connecte", 401
    c = db()
    cur = c.cursor()
    cur.execute("INSERT INTO comments (ticket_id, author, text) VALUES (%s,%s,%s)",
                (tid, session["user"], request.form.get("text", "")))
    c.commit()
    c.close()
    return redirect("/ticket/%d" % tid)


@app.route("/search")
def search():
    q = request.args.get("q", "")
    c = db()
    cur = c.cursor()
    # FAILLE 1 : injection SQL
    cur.execute("SELECT id, title FROM tickets WHERE title LIKE '%" + q + "%'")
    rows = cur.fetchall()
    c.close()
    return str(rows)


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
