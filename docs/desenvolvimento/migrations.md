# Migrations versionadas

## Regra do projeto

As migrations do PostgreSQL fazem parte do código-fonte. Toda alteração em um model Django deve incluir, no mesmo PR, a migration correspondente, gerada no ambiente Docker e revisada antes da aplicação.

- mantenha os arquivos numerados em `src/apps/<app>/migrations/` sob controle de versão;
- gere migrations apenas para mudanças reais de models do projeto;
- não gere migrations vazias ou não relacionadas à tarefa;
- revise dependências e operações antes de adicionar o arquivo ao Git.

## Fluxo de desenvolvimento

Com o ambiente de desenvolvimento em execução, execute:

```bash
# Gerar somente as migrations decorrentes da alteração de models
docker compose -f docker-compose.dev.yml exec django-web python manage.py makemigrations

# Conferir se todos os models estão representados pela cadeia versionada
docker compose -f docker-compose.dev.yml exec django-web python manage.py makemigrations --check --dry-run

# Aplicar a cadeia no PostgreSQL de desenvolvimento
docker compose -f docker-compose.dev.yml exec django-web python manage.py migrate

# Validar o projeto e a suíte
docker compose -f docker-compose.dev.yml exec django-web python manage.py check
docker compose -f docker-compose.dev.yml exec django-web python manage.py test
```

Revise o arquivo gerado e confirme que ele contém somente as operações esperadas. Migrations de dados precisam ser deliberadas e revisadas.

Os apps são importados como `apps.<nome>`, mas preservam labels Django simples. Use labels como `core` em dependências e relações serializadas (ex.: `"core.Setor"`, `("core", "0001_initial")`); mover ou renomear apenas o módulo Python não justifica criar uma migration.

## Antes do merge

Até existir uma CI, execute manualmente no ambiente Docker:

1. `makemigrations --check --dry-run`, que não deve detectar alterações;
2. `migrate --noinput`, aplicando toda a cadeia;
3. `manage.py check`;
4. a suíte completa com `manage.py test --noinput`.

## Produção

O serviço `migrate` do `docker-compose.yml` executa exclusivamente:

```sh
python manage.py migrate --noinput
```

Gere e revise as migrations antes da implantação; o deploy nunca executa `makemigrations`.

## Baseline

O base traz `core/0001_initial.py`, que cria `core.Usuario` (usuário customizado, `AUTH_USER_MODEL`), `Setor` (com `gestor_sistema`) e `Cargo` desde o início. Como `AUTH_USER_MODEL` não pode ser trocado depois da primeira migration, **não** remova o `core.Usuario`: acrescente campos a ele quando precisar.

Para recriar o banco de desenvolvimento do zero (apaga os dados de dev):

```bash
docker compose -f docker-compose.dev.yml down -v
docker compose -f docker-compose.dev.yml up --build
docker compose -f docker-compose.dev.yml exec django-web python manage.py createsuperuser
```
