"""
Cliente simples para falar com o Supabase usando a REST API (PostgREST),
sem depender da lib supabase-py (menos dependências, menos dor de cabeça
com versões). Usa a service_role key, então NUNCA deixe essa chave
exposta no front-end -- ela só vive aqui no back-end.
"""
import os
import uuid
import mimetypes
import requests

SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")

TABLE = "artigos"
BUCKET = "imagens-artigos"


def _headers(prefer=None):
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
    }
    if prefer:
        headers["Prefer"] = prefer
    return headers


def _base_url():
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise RuntimeError(
            "SUPABASE_URL / SUPABASE_SERVICE_KEY não configurados. "
            "Veja o README para saber como configurar."
        )
    return f"{SUPABASE_URL}/rest/v1/{TABLE}"


def list_articles(only_published=True, limit=100):
    params = {
        "select": "*",
        "order": "created_at.desc",
        "limit": str(limit),
    }
    if only_published:
        params["published"] = "eq.true"
    resp = requests.get(_base_url(), headers=_headers(), params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


def get_article_by_slug(slug):
    params = {"select": "*", "slug": f"eq.{slug}", "limit": "1"}
    resp = requests.get(_base_url(), headers=_headers(), params=params, timeout=10)
    resp.raise_for_status()
    rows = resp.json()
    return rows[0] if rows else None


def create_article(data):
    resp = requests.post(
        _base_url(),
        headers=_headers(prefer="return=representation"),
        json=data,
        timeout=10,
    )
    resp.raise_for_status()
    rows = resp.json()
    return rows[0] if rows else None


def slug_exists(slug):
    params = {"select": "id", "slug": f"eq.{slug}", "limit": "1"}
    resp = requests.get(_base_url(), headers=_headers(), params=params, timeout=10)
    resp.raise_for_status()
    return len(resp.json()) > 0


def upload_image(file_storage):
    """
    Recebe um arquivo do Flask (request.files['campo']) e sobe pro
    Supabase Storage. Retorna a URL pública da imagem.
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise RuntimeError(
            "SUPABASE_URL / SUPABASE_SERVICE_KEY não configurados. "
            "Veja o README para saber como configurar."
        )

    filename = file_storage.filename or "imagem"
    ext = os.path.splitext(filename)[1].lower() or ".jpg"
    if ext not in (".jpg", ".jpeg", ".png", ".gif", ".webp"):
        raise ValueError("formato de imagem não suportado (use jpg, png, gif ou webp)")

    path = f"{uuid.uuid4().hex}{ext}"
    content_type = (
        file_storage.mimetype
        or mimetypes.guess_type(filename)[0]
        or "application/octet-stream"
    )
    data = file_storage.read()

    upload_url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET}/{path}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": content_type,
    }
    resp = requests.post(upload_url, headers=headers, data=data, timeout=30)
    resp.raise_for_status()

    return f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{path}"
