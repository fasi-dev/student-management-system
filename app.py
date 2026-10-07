import os, time
import pymysql
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-only-key")

DB = dict(
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", ""),
    database=os.getenv("DB_NAME", "studentdb"),
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=True,
)

def conn():
    return pymysql.connect(**DB)

def init_db():
    for _ in range(30):  # wait for MySQL to be ready
        try:
            with conn() as c, c.cursor() as cur:
                cur.execute("""CREATE TABLE IF NOT EXISTS students (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(100) NOT NULL,
                    course VARCHAR(100) NOT NULL,
                    phone VARCHAR(20))""")
            return
        except pymysql.err.OperationalError:
            time.sleep(2)
    raise RuntimeError("Could not connect to MySQL")

@app.route("/")
def index():
    q = request.args.get("q", "").strip()
    with conn() as c, c.cursor() as cur:
        if q:
            like = f"%{q}%"
            cur.execute("SELECT * FROM students WHERE name LIKE %s OR email LIKE %s OR course LIKE %s ORDER BY id DESC", (like, like, like))
        else:
            cur.execute("SELECT * FROM students ORDER BY id DESC")
        students = cur.fetchall()
    return render_template("index.html", students=students, q=q)

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        f = request.form
        with conn() as c, c.cursor() as cur:
            cur.execute("INSERT INTO students (name,email,course,phone) VALUES (%s,%s,%s,%s)",
                        (f["name"], f["email"], f["course"], f["phone"]))
        flash("Student added.")
        return redirect(url_for("index"))
    return render_template("form.html", s=None)

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    with conn() as c, c.cursor() as cur:
        if request.method == "POST":
            f = request.form
            cur.execute("UPDATE students SET name=%s,email=%s,course=%s,phone=%s WHERE id=%s",
                        (f["name"], f["email"], f["course"], f["phone"], id))
            flash("Student updated.")
            return redirect(url_for("index"))
        cur.execute("SELECT * FROM students WHERE id=%s", (id,))
        s = cur.fetchone()
    if not s:
        return redirect(url_for("index"))
    return render_template("form.html", s=s)

@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    with conn() as c, c.cursor() as cur:
        cur.execute("DELETE FROM students WHERE id=%s", (id,))
    flash("Student deleted.")
    return redirect(url_for("index"))

init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
