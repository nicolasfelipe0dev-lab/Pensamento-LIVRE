-- Rode este script no Supabase: Painel > SQL Editor > New query > Run

create extension if not exists pgcrypto;

create table if not exists public.artigos (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  slug text not null unique,
  summary text,
  content text not null,
  tag text,
  cover_image_url text,
  published boolean not null default true,
  created_at timestamptz not null default now()
);

create index if not exists artigos_created_at_idx on public.artigos (created_at desc);
create index if not exists artigos_slug_idx on public.artigos (slug);

-- Habilita Row Level Security.
-- O back-end Flask usa a "service_role key", que ignora RLS por padrão,
-- então essas políticas abaixo servem apenas caso você queira, no futuro,
-- ler os artigos publicados direto do front-end com a chave "anon".
alter table public.artigos enable row level security;

create policy "Leitura pública de artigos publicados"
  on public.artigos
  for select
  using (published = true);


-- ==========================================================
-- Storage: bucket público para as imagens dos artigos (capa
-- e imagens inseridas no meio do texto).
-- ==========================================================
insert into storage.buckets (id, name, public)
values ('imagens-artigos', 'imagens-artigos', true)
on conflict (id) do nothing;
