from urllib.parse import urlparse
import os
import socket
import sqlite3
import uuid

import httpx
from flask import Flask, flash, render_template, request, redirect, session
from supabase import create_client


app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY", "amor_vinicius_taiana")

UPLOAD_FOLDER = "static/uploads"
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "fotos")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def _normalizar_supabase_url(url):
    if not url:
        return None

    url = url.strip().rstrip("/")
    if not url:
        return None

    # Permite configurar apenas o project ref do Supabase, por exemplo:
    # SUPABASE_URL=abcdefghijklmnopqrst
    if "://" not in url and "/" not in url and "." not in url:
        url = f"https://{url}.supabase.co"

    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"

    parsed_url = urlparse(url)
    if not parsed_url.netloc:
        return None

    return f"{parsed_url.scheme}://{parsed_url.netloc}"


def _host_supabase_resolve(supabase_url):
    if not supabase_url:
        return False

    hostname = urlparse(supabase_url).hostname
    if not hostname:
        return False

    try:
        socket.getaddrinfo(hostname, 443)
    except socket.gaierror:
        return False

    return True


def _mensagem_erro_supabase_conexao():
    return (
        "Não foi possível conectar ao Supabase. Confira se a variável "
        "SUPABASE_URL está no formato https://SEU_PROJECT_REF.supabase.co, "
        "se a SUPABASE_KEY está correta e se o bucket existe."
    )


def criar_cliente_supabase():
    supabase_url = _normalizar_supabase_url(os.getenv("SUPABASE_URL"))
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        print(
            "Supabase não configurado. Verifique as variáveis "
            "SUPABASE_URL e SUPABASE_KEY."
        )
        return None

    print("SUPABASE_URL configurada para", supabase_url)
    print("SUPABASE_KEY existe =", bool(supabase_key))

    if not _host_supabase_resolve(supabase_url):
        print(
            "Não foi possível resolver o host da SUPABASE_URL. "
            "Use o formato https://SEU_PROJECT_REF.supabase.co."
        )
        return None

    return create_client(supabase_url, supabase_key)


supabase = criar_cliente_supabase()


@app.route("/")
def index():

    if supabase is None:
        return render_template("index.html", fotos=[])

    resultado = supabase.table("fotos").select("*").execute()

    fotos = [
        (item["url"],)
        for item in (resultado.data or [])
    ]

    print("TOTAL DE FOTOS:", len(fotos))

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

    if supabase is None:
        flash(_mensagem_erro_supabase_conexao())
        return redirect("/admin")

    foto = request.files.get("foto")

    if foto and foto.filename:

        nome = f"{uuid.uuid4()}_{foto.filename}"
        arquivo = foto.read()

        try:
            resposta = supabase.storage.from_(SUPABASE_BUCKET).upload(
                nome,
                arquivo,
                {"content-type": foto.mimetype or "application/octet-stream"}
            )
        except httpx.ConnectError as erro:
            print("Erro de conexão ao enviar imagem para o Supabase:", erro)
            flash(_mensagem_erro_supabase_conexao())
            return redirect("/admin")
        except Exception as erro:
            print("Erro ao enviar imagem para o Supabase:", erro)
            flash(
                "Não foi possível enviar a imagem para o Supabase. "
                "Confira SUPABASE_URL, SUPABASE_KEY e o bucket."
            )
            return redirect("/admin")

        print("UPLOAD:", resposta)

        url = supabase.storage.from_(SUPABASE_BUCKET).get_public_url(nome)

        print("URL:", url)

        supabase.table("fotos").insert({
            "url": str(url)
        }).execute()

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
