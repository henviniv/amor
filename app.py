from flask import Flask, render_template, request, redirect, session
import sqlite3
import os
import supabase
from supabase import create_client

app = Flask(__name__)

app.secret_key = "amor_vinicius_taiana"

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

print("SUPABASE_URL =", SUPABASE_URL)
print("SUPABASE_KEY existe =", bool(SUPABASE_KEY))

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

print("Cliente Supabase criado")



@app.route("/")
def index():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT url FROM fotos")

    fotos = cursor.fetchall()

    conn.close()

    return render_template(
        "index.html",
        fotos=fotos
    )


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        usuario = request.form["usuario"]
        senha = request.form["senha"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM usuarios
            WHERE username = ?
            AND password = ?
            """,
            (usuario, senha)
        )

        user = cursor.fetchone()

        conn.close()

        if user:
            session["usuario"] = usuario
            return redirect("/admin")

    return render_template("login.html")


@app.route("/admin")
def admin():

    if "usuario" not in session:
        return redirect("/login")

    return render_template("admin.html")


@app.route("/upload", methods=["POST"])
def upload():

    if "usuario" not in session:
        return redirect("/login")

    foto = request.files["foto"]

    if foto:

        import uuid

        nome = f"{uuid.uuid4()}_{foto.filename}"

        arquivo = foto.read()

        resposta = supabase.storage.from_("fotos").upload(
            nome,
            arquivo
        )

        print("UPLOAD:", resposta)

        url = supabase.storage.from_("fotos").get_public_url(nome)

        print("URL:", url)

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO fotos (url) VALUES (?)",
            (str(url),)
        )

        conn.commit()
        conn.close()

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)