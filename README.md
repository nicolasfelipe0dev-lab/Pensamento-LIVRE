# Pensamento Livre

Site pessoal para publicar seus artigos/pensamentos, no estilo página de notícias.
Back-end em Flask, banco de dados no Supabase (Postgres via REST/PostgREST).

## O que tem aqui

- `app.py` — aplicação Flask (rotas, lógica)
- `supabase_client.py` — funções que conversam com o Supabase
- `templates/` — páginas HTML (Jinja2)
- `static/css/style.css` — estilo (paleta azul-marinho/branco/preto da sua logo)
- `static/img/logo.jpg` — sua foto/logo, usada no cabeçalho
- `supabase_schema.sql` — script para criar a tabela no Supabase
- `.env.example` — modelo das variáveis de ambiente

## Passo 1 — Criar o projeto no Supabase

1. Acesse https://supabase.com e crie um projeto novo (grátis).
2. No painel do projeto, vá em **SQL Editor** → **New query**.
3. Cole o conteúdo do arquivo `supabase_schema.sql` e clique em **Run**.
   Isso cria a tabela `artigos` (título, slug, resumo, conteúdo, tag,
   imagem de capa, publicado, data) **e** o bucket público
   `imagens-artigos` no Storage, usado para as fotos que você subir
   pelos artigos.
4. Vá em **Project Settings → API** e copie:
   - **Project URL** → vai virar `SUPABASE_URL`
   - **service_role key** (não a `anon` key) → vai virar `SUPABASE_SERVICE_KEY`

   ⚠️ A `service_role key` tem poder total sobre o banco. Ela fica só no
   back-end (nunca no navegador), por isso o Flask é quem fala com o
   Supabase, e não o front-end diretamente.

## Passo 2 — Configurar o projeto localmente

```bash
cd pensamento-livre
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# edite o .env e preencha SUPABASE_URL, SUPABASE_SERVICE_KEY,
# ADMIN_PASSWORD e SECRET_KEY
```

Carregue as variáveis de ambiente antes de rodar (no Linux/Mac):

```bash
export $(cat .env | xargs)
python app.py
```

No Windows (PowerShell), abra o `.env` e defina cada variável com `$env:NOME="valor"`,
ou instale `python-dotenv` e adicione `from dotenv import load_dotenv; load_dotenv()`
no topo do `app.py`.

Acesse **http://localhost:5000**.

## Passo 3 — Publicar um artigo

1. Vá em **"área do autor"** no topo do site.
2. Digite a senha que você definiu em `ADMIN_PASSWORD`.
3. Clique em **"+ novo artigo"**, preencha título, resumo, tag (opcional)
   e o conteúdo (aceita Markdown: `**negrito**`, `# título`, `- listas`, `> citação`).
4. Marque "publicar agora" ou deixe desmarcado para salvar como rascunho.
5. Pronto — o artigo aparece na home, o mais recente em destaque.

## Passo 4 — Deploy (colocar no ar)

O site inteiro (front + back) roda junto, então você precisa de um serviço
que rode Python/Flask — Netlify sozinho **não** serve para isso (ele hospeda
apenas sites estáticos). Opções fáceis e gratuitas para começar:

**Render.com** (recomendado, similar ao que você já viu no outro projeto):

1. Suba esta pasta para um repositório no GitHub.
2. No Render, crie um **Web Service** apontando para o repositório.
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app`
5. Em **Environment**, adicione as mesmas variáveis do `.env`
   (`SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `ADMIN_PASSWORD`, `SECRET_KEY`).
6. Deploy. Você recebe uma URL tipo `pensamento-livre.onrender.com`.

**Railway.app** funciona de forma bem parecida, se preferir.

Depois, se quiser um domínio bonito, dá para apontar um domínio próprio
para essa URL nas configurações do Render/Railway.

## Publicando artigos com imagens

Você pode subir imagens direto do computador em dois lugares do formulário
de novo artigo:

- **Imagem de capa**: campo de arquivo logo abaixo da tag. Aparece no topo
  do artigo. Se preferir, ainda dá pra colar uma URL em vez de subir arquivo.
- **Imagens dentro do texto**: clique em **"+ inserir imagem no texto"**
  acima da caixa de conteúdo, escolha o arquivo, e o link em Markdown
  (`![...](...)`) é inserido automaticamente no ponto onde o cursor estiver.

Formatos aceitos: JPG, PNG, GIF e WEBP, até 8 MB por imagem. As imagens
ficam guardadas no bucket `imagens-artigos` do Supabase Storage.

## Personalizações fáceis

- **Trocar a paleta de cores**: edite as variáveis no topo de
  `static/css/style.css` (`--navy`, `--cream`, `--gold`, etc).
- **Trocar a foto do cabeçalho**: substitua `static/img/logo.jpg`.
- **Mudar a senha de autor**: troque `ADMIN_PASSWORD` nas variáveis de ambiente.
- **Adicionar categorias fixas**: hoje a tag é texto livre; se quiser,
  dá para transformar em um `<select>` no formulário depois.
