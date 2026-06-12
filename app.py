from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

app = Flask(__name__)

app.secret_key = "amor_vinicius_taiana"

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/")
def index():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT arquivo FROM fotos")

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

        caminho = os.path.join(
            app.config["UPLOAD_FOLDER"],
            foto.filename
        )

        foto.save(caminho)

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO fotos (arquivo)
            VALUES (?)
            """,
            (foto.filename,)
        )

        conn.commit()
        conn.close()

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)