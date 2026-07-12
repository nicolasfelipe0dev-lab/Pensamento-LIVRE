import os
import re
import unicodedata
from datetime import datetime

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    abort,
    jsonify,
)
import markdown as md

import supabase_client as db

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "troque-esta-chave-em-producao")
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024  # 8 MB por upload

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "livre123")


# ---------- helpers ----------

def slugify(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def is_logged_in():
    return session.get("admin_ok") is True


def render_markdown(text):
    return md.markdown(text or "", extensions=["extra", "nl2br"])


app.jinja_env.filters["markdown"] = render_markdown


@app.template_filter("data_br")
def data_br(value):
    if not value:
        return ""
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.strftime("%d/%m/%Y")
    except Exception:
        return value


# ---------- rotas públicas ----------

@app.route("/")
def index():
    try:
        artigos = db.list_articles(only_published=True)
    except Exception as e:
        artigos = []
        flash(f"Não consegui carregar os artigos: {e}", "erro")
    destaque = artigos[0] if artigos else None
    resto = artigos[1:] if len(artigos) > 1 else []
    return render_template(
        "index.html", destaque=destaque, artigos=resto, total=len(artigos)
    )


@app.route("/artigo/<slug>")
def artigo(slug):
    try:
        post = db.get_article_by_slug(slug)
    except Exception as e:
        flash(f"Não consegui carregar o artigo: {e}", "erro")
        return redirect(url_for("index"))
    if not post or (not post.get("published") and not is_logged_in()):
        abort(404)
    return render_template("article.html", post=post)


# ---------- área do autor ----------

@app.route("/entrar", methods=["GET", "POST"])
def entrar():
    if request.method == "POST":
        senha = request.form.get("senha", "")
        if senha == ADMIN_PASSWORD:
            session["admin_ok"] = True
            return redirect(url_for("novo_artigo"))
        flash("Senha incorreta.", "erro")
    return render_template("login.html")


@app.route("/sair")
def sair():
    session.pop("admin_ok", None)
    return redirect(url_for("index"))


@app.route("/upload-imagem", methods=["POST"])
def upload_imagem():
    if not is_logged_in():
        return jsonify({"erro": "não autorizado"}), 401

    arquivo = request.files.get("imagem")
    if not arquivo or arquivo.filename == "":
        return jsonify({"erro": "nenhum arquivo enviado"}), 400

    try:
        url = db.upload_image(arquivo)
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400
    except Exception as e:
        return jsonify({"erro": f"falha no upload: {e}"}), 500

    return jsonify({"url": url})


@app.route("/novo", methods=["GET", "POST"])
def novo_artigo():
    if not is_logged_in():
        return redirect(url_for("entrar"))

    if request.method == "POST":
        titulo = request.form.get("titulo", "").strip()
        resumo = request.form.get("resumo", "").strip()
        conteudo = request.form.get("conteudo", "").strip()
        tag = request.form.get("tag", "").strip()
        capa = request.form.get("capa_url", "").strip()
        capa_arquivo = request.files.get("capa_arquivo")
        publicar = request.form.get("publicado") == "on"

        if not titulo or not conteudo:
            flash("Título e conteúdo são obrigatórios.", "erro")
            return render_template("new_article.html", form=request.form)

        if capa_arquivo and capa_arquivo.filename:
            try:
                capa = db.upload_image(capa_arquivo)
            except Exception as e:
                flash(f"Erro ao enviar imagem de capa: {e}", "erro")
                return render_template("new_article.html", form=request.form)

        base_slug = slugify(titulo)
        slug = base_slug
        i = 2
        try:
            while db.slug_exists(slug):
                slug = f"{base_slug}-{i}"
                i += 1

            db.create_article(
                {
                    "title": titulo,
                    "slug": slug,
                    "summary": resumo,
                    "content": conteudo,
                    "tag": tag or None,
                    "cover_image_url": capa or None,
                    "published": publicar,
                }
            )
        except Exception as e:
            flash(f"Erro ao salvar no Supabase: {e}", "erro")
            return render_template("new_article.html", form=request.form)

        flash("Artigo publicado com sucesso!" if publicar else "Rascunho salvo.", "ok")
        return redirect(url_for("artigo", slug=slug))

    return render_template("new_article.html", form={})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
