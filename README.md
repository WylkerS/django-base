# Projeto Base

Projeto base Django para sistemas internos, extraído da arquitetura do **Agendamento de Salas** (por sua vez herdada do Portal do Analista): mesma stack, mesma estrutura de pastas, mesmas camadas de código, mesma documentação e o mesmo ambiente Docker. Serve de ponto de partida — clone, siga o checklist abaixo e comece a criar os apps de domínio.

O que já vem pronto:

- projeto Django em `src/config/` (settings via `.env`, urls, wsgi/asgi, app Celery);
- app `core`: usuário customizado (`core.Usuario`), `Setor`, `Cargo`, login/logout, home, página 403 e a política de acesso por dados (`Setor.gestor_sistema` + `@gestor_requerido`);
- app `theme`: Tailwind CSS 4 + DaisyUI 5 com um tema provisório, e o `base.html` com cabeçalho, navegação e mensagens;
- Celery, Celery Beat (agendamentos no banco) e Flower;
- Docker Compose de desenvolvimento (autoreload + Tailwind watch), completo (Gunicorn + Nginx) e de testes (runner isolado), com um `Makefile` de atalhos; o PostgreSQL é externo e nenhum compose sobe banco;
- suíte de testes por camada (`unit`/`integration`/`e2e`, `make test`, Bandit) e a estrutura de `docs/` (arquitetura, segurança, desenvolvimento, operação, design system e catálogo de componentes).

## Tecnologias

- Django 5.2;
- PostgreSQL 17;
- Redis, Celery, Celery Beat e Flower;
- autenticação local do Django (`ModelBackend`), extensível para LDAP/SSO;
- Gunicorn e Nginx;
- Poetry para gerenciamento das dependências Python;
- Tailwind CSS 4 e DaisyUI 5 (app `theme`, via `django-tailwind`);
- Docker e Docker Compose.

## Iniciar um projeto a partir do base

1. Copie o repositório (ou use-o como *template* no GitHub) para o novo projeto e crie as branches `main` e `dev`.
2. No `.env.example`, troque `APP_NOME`, `COMPOSE_PROJECT_NAME`, `APP_IMAGE` e `POSTGRES_DB`; aponte `POSTGRES_*` para o banco externo do projeto; ajuste as portas (`APP_PORT`, `REDIS_PORT`, `FLOWER_PORT`) se outro projeto já as usar na mesma máquina.
3. Em `pyproject.toml`, troque `name`, `description` e `authors`.
4. Reescreva este `README.md` e o `AGENTS.md` (trechos marcados com `<!-- PREENCHER -->`) com o objetivo e o domínio do sistema.
5. Coloque o Design System do projeto em `docs/design_system/` e aplique os tokens em `src/apps/theme/static_src/src/styles.css` (ver [`docs/exemplos_componentes/tema-e-tokens.md`](docs/exemplos_componentes/tema-e-tokens.md)).
6. Ajuste a home (`src/templates/core/home.html`), a chamada da tela de login e a navegação do `base.html`.
7. Crie os apps de domínio seguindo [Adicionar uma nova área](docs/desenvolvimento/fluxo-local.md#adicionar-uma-nova-área).

O pacote Django continua se chamando `config` em todos os projetos — não é preciso renomeá-lo.

## Preparação com Docker

### Requisitos

- Git;
- Docker Engine ou Docker Desktop;
- Docker Compose v2 (`docker compose`);
- um servidor PostgreSQL 17 acessível pelos containers, com um banco e um usuário para o projeto (o usuário precisa de `CREATEDB` para rodar a suíte).

Python, Node.js e Redis não precisam ser instalados no host; o PostgreSQL é externo e nenhum compose o sobe. O Poetry só é necessário para alterar `pyproject.toml` / `poetry.lock`.

### 1. Configurar o ambiente

```bash
cp .env.example .env
```

Edite o `.env` e ajuste principalmente:

- `SECRET_KEY`;
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`;
- `POSTGRES_HOST` e `POSTGRES_PORT`: um PostgreSQL externo (hostname ou IP do servidor; `host.docker.internal` para um PostgreSQL instalado no próprio host) — nunca `localhost`, que dentro do container é o próprio container;
- `DJANGO_ALLOWED_HOSTS` e `DJANGO_CSRF_TRUSTED_ORIGINS`;
- SMTP (`EMAIL_*`), quando os e-mails forem enviados;
- `FLOWER_USER` e `FLOWER_PASSWORD`.

### 2. Subir o ambiente de desenvolvimento

```bash
docker compose -f docker-compose.dev.yml up --build
```

### 3. Criar o superusuário

```bash
docker compose -f docker-compose.dev.yml exec django-web python manage.py createsuperuser
```

Opcionalmente, popule setores e usuários de exemplo:

```bash
docker compose -f docker-compose.dev.yml exec django-web python /app/scripts/utils/popular_banco.py
```

### 4. Acessar

| Serviço | Endereço (dev, portas padrão) |
| --- | --- |
| Aplicação | `http://localhost:8001` |
| Django Admin | `http://localhost:8001/admin/` |
| Flower (com `--profile celery`) | `http://localhost:5555` |
| Redis | `localhost:6379` |

## Ambiente completo (produção)

```bash
docker compose up --build -d
```

Sobe a stack com Gunicorn atrás do Nginx (`frontend-proxy` na porta `APP_PORT`, padrão 8001), além de `migrate`, `collectstatic`, o worker Celery da fila `celery` e o Celery Beat. O worker da fila `rpa` e o Flower sobem com `docker compose --profile celery up --build -d`. O Redis não é publicado no host nesse ambiente.

```bash
# Logs
docker compose logs -f django-web frontend-proxy
docker compose logs -f celery-worker celery-beat

# Django check
docker compose exec django-web python manage.py check

# Encerrar mantendo os dados
docker compose down
```

`docker compose down -v` apaga os volumes (Redis e estáticos); o banco externo não é afetado. Não use com dados que precisa manter.

## Comandos frequentes

```bash
# Verificar o Django
docker compose -f docker-compose.dev.yml exec django-web python manage.py check

# Criar migrations
docker compose -f docker-compose.dev.yml exec django-web python manage.py makemigrations

# Aplicar migrations
docker compose -f docker-compose.dev.yml exec django-web python manage.py migrate

# Rodar os testes (no host; ambiente isolado, não exige o compose de dev ativo)
make test

# Encerrar mantendo os volumes
docker compose -f docker-compose.dev.yml down
```

As dependências Python são declaradas em `pyproject.toml` e fixadas em `poetry.lock`; alterá-las exige rebuild da imagem (`--build`). As dependências de front-end ficam em `src/apps/theme/static_src/package.json` / `package-lock.json`.

## Estrutura

| Caminho | Responsabilidade |
| --- | --- |
| `src/manage.py` | comandos Django (executados em `/app/src` dentro dos containers) |
| `src/config/` | configuração do projeto Django (settings, urls, wsgi, asgi, `celery.py`) |
| `src/apps/core/` | usuário (`core.Usuario`), setores, cargos, login/logout, home e política de acesso |
| `src/apps/theme/` | front-end com Tailwind CSS / DaisyUI (tema `base`) |
| `src/templates/` | templates compartilhados (`base.html`, `403.html`, `partials/`) e uma pasta por app |
| `src/tests/` | testes automatizados por app e camada (`unit/`, `integration/`, `e2e/`) e helpers em `_apoio.py` |
| `scripts/utils/` | utilitários de desenvolvimento (ex. `popular_banco.py`) |
| `docs/` | documentação técnica ([índice](docs/README.md)) |
| `Dockerfile` | imagem da aplicação (build do front-end + venv Poetry) |
| `docker-compose.yml` | stack completa (Gunicorn + Nginx + Celery) |
| `docker-compose.dev.yml` | stack de desenvolvimento (autoreload + Tailwind watch) |
| `docker-compose.test.yml` | runner da suíte (cria `test_<POSTGRES_DB>` no banco externo) |
| `Makefile` | atalhos de desenvolvimento, testes e validação (`make` lista todos) |
| `nginx.conf` | proxy reverso e arquivos estáticos |
| `AGENTS.md` | convenções para quem desenvolve (pessoas e agentes de IA) |
