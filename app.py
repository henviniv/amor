from urllib.parse import urlparse
import os
import socket
import uuid

import httpx
from flask import Flask, flash, render_template, request, redirect, session
from supabase import create_client


app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY", "amor_vinicius_taiana")

SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "fotos")


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


def _valor_storage(objeto, chave, padrao=None):
    if isinstance(objeto, dict):
        return objeto.get(chave, padrao)

    return getattr(objeto, chave, padrao)


def _listar_fotos_supabase():
    """Busca as fotos diretamente no Storage para sobreviver a redeploys."""
    if supabase is None:
        return []

    fotos = []
    offset = 0
    limit = 100

    while True:
        resposta = supabase.storage.from_(SUPABASE_BUCKET).list(
            "",
            {
                "limit": limit,
                "offset": offset,
                "sortBy": {"column": "created_at", "order": "desc"},
            },
        )

        if not resposta:
            break

        for arquivo in resposta:
            nome = _valor_storage(arquivo, "name")
            if not nome or _valor_storage(arquivo, "id") is None:
                continue

            fotos.append(
                {
                    "nome": nome,
                    "url": supabase.storage.from_(SUPABASE_BUCKET).get_public_url(nome),
                }
            )

        if len(resposta) < limit:
            break

        offset += limit

    return fotos


@app.route("/")
def index():
    try:
        fotos = _listar_fotos_supabase()
    except Exception as erro:
        print("Erro ao listar fotos do Supabase:", erro)
        fotos = []

    return render_template("index.html", fotos=fotos)


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        usuario = request.form["usuario"]
        senha = request.form["senha"]

        if (
            (usuario == "vinicius" and senha == "amoataiana")
            or (usuario == "taiana" and senha == "amovinicius")
        ):
            session["usuario"] = usuario
            return redirect("/admin")

    return render_template("login.html")


@app.route("/admin")
def admin():

    if "usuario" not in session:
        return redirect("/login")

    try:
        fotos = _listar_fotos_supabase()
    except Exception as erro:
        print("Erro ao listar fotos do Supabase:", erro)
        flash(_mensagem_erro_supabase_conexao())
        fotos = []

    return render_template("admin.html", fotos=fotos)


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
                {"content-type": foto.mimetype or "application/octet-stream"},
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
        flash("Foto enviada com sucesso.")

    return redirect("/")


@app.route("/delete/<path:nome_arquivo>", methods=["POST"])
def delete(nome_arquivo):

    if "usuario" not in session:
        return redirect("/login")

    if supabase is None:
        flash(_mensagem_erro_supabase_conexao())
        return redirect("/admin")

    try:
        supabase.storage.from_(SUPABASE_BUCKET).remove([nome_arquivo])
    except Exception as erro:
        print("Erro ao remover arquivo do Supabase:", erro)
        flash("Não foi possível excluir a foto do Supabase.")
        return redirect("/admin")

    flash("Foto excluída com sucesso.")

    return redirect("/admin")


if __name__ == "__main__":
    app.run(debug=True)
