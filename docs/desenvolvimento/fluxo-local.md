# Desenvolvimento com Docker Compose

## Ambiente recomendado

Use sempre o Compose de desenvolvimento para executar a aplicação. Python, Django, Celery, Node.js e Tailwind não devem ser executados diretamente no host.

```bash
# Executar no host; os serviços rodam nos containers
docker compose -f docker-compose.dev.yml up --build
```

A aplicação fica disponível em `http://localhost:8001` (`APP_PORT`).

O `celery-worker` (fila `celery`) e o `celery-beat` sobem junto com o restante. Ficam sob o profile `celery`, só quando solicitados, o `celery-worker-rpa` (fila `rpa`) e o `flower`:

```bash
docker compose -f docker-compose.dev.yml --profile celery up --build
```

O worker e o beat não têm autoreload: depois de alterar uma task ou um service chamado por ela, reinicie-os com `docker compose -f docker-compose.dev.yml restart celery-worker celery-beat` (ou `make restart`).

O compose de desenvolvimento utiliza diretamente o arquivo `.env` e não sobe banco: a aplicação aponta para um PostgreSQL externo. Para funcionar dentro da rede Docker, confirme especialmente:

```dotenv
DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,django-web
DJANGO_CSRF_TRUSTED_ORIGINS=http://localhost:8001,http://127.0.0.1:8001
# Servidor do PostgreSQL externo; host.docker.internal = PostgreSQL instalado no próprio host
POSTGRES_HOST=host.docker.internal
POSTGRES_PORT=5432
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

## Atalhos do Makefile

O `Makefile` da raiz encurta os comandos do Compose. Execute-os no host (exige `make` e um shell POSIX, como o Git Bash no Windows); `make` sem argumentos lista todos:

| Comando | Equivale a |
| --- | --- |
| `make up` | `docker compose -f docker-compose.dev.yml --profile celery up --build` |
| `make up-min` | `docker compose -f docker-compose.dev.yml up --build` (sem worker `rpa` e Flower) |
| `make down` | encerra o ambiente mantendo os volumes |
| `make restart` | reinicia Tailwind, Django, workers, Beat e Flower sem repetir migrations |
| `make ps` / `make logs` / `make logs-app` / `make logs-celery` | estado e logs dos containers |
| `make check` | `manage.py check` no `django-web` |
| `make makemigrations` / `make migrate` | aceitam `APP_LABEL=<app>` para filtrar |
| `make migrations-check` | `makemigrations --check --dry-run` |
| `make createsuperuser` / `make shell` | comandos interativos no `django-web` |
| `make test` / `make test-unit` / `make test-integration` / `make test-e2e` | suíte em ambiente isolado; `TEST_TARGET=tests.<app>` filtra |
| `make bandit` | análise de segurança do Python |
| `make tailwind-build` | build de produção do CSS em container descartável |
| `make poetry-check` | `poetry check --lock` no host |
| `make compose-check` | `config --quiet` dos três arquivos Compose |
| `make validate` | Compose, Poetry, check, migrations, suíte e build do Tailwind |

Os comandos `check`, `migrate`, `makemigrations`, `migrations-check`, `createsuperuser` e `shell` usam `exec` e exigem o ambiente de desenvolvimento em execução; `test`, `bandit` e `tailwind-build` não. Ao acrescentar um serviço contínuo ao `docker-compose.dev.yml`, inclua-o em `APP_SERVICES` (ou `CELERY_SERVICES`) no `Makefile`.

## Serviços do compose de desenvolvimento

| Serviço | Função | Porta no host (padrão) | Tipo |
| --- | --- | --- | --- |
| `redis` | broker e resultados do Celery | `127.0.0.1:6379` (`REDIS_PORT`) | contínuo |
| `migrate` | aplica as migrations existentes | — | execução única |
| `tailwind` | `npm ci` + PostCSS/Tailwind em modo watch | — | contínuo |
| `django-web` | `runserver` com autoreload | `8001` → `8000` (`APP_PORT`) | contínuo |
| `celery-worker` | fila `celery` | — | contínuo |
| `celery-worker-rpa` | fila `rpa`, concorrência 1 | — | profile `celery` |
| `celery-beat` | disparo dos agendamentos | — | contínuo |
| `flower` | monitoramento do Celery | `127.0.0.1:5555` (`FLOWER_PORT`) | profile `celery` |

Nenhum serviço fixa `container_name`: os containers recebem o prefixo `COMPOSE_PROJECT_NAME`, o que permite rodar vários projetos derivados do base na mesma máquina (desde que as portas do `.env` não colidam).

## Atualização automática

O repositório é montado em `/app` dentro dos containers. Alterações em Python e templates são percebidas pelo `runserver`. O serviço `tailwind` monitora templates, Python, JavaScript e o arquivo de tema e recompila o CSS para o volume `tailwind_css_dev`, compartilhado (somente leitura) com o `django-web`.

Mudanças em `pyproject.toml`, `poetry.lock`, `src/apps/theme/static_src/package.json`, `package-lock.json`, `Dockerfile` ou pacotes de sistema exigem reconstrução:

```bash
docker compose -f docker-compose.dev.yml up --build
```

## Comandos Django

```bash
# Checagem dentro de django-web
docker compose -f docker-compose.dev.yml exec django-web python manage.py check

# Criar migrations depois de alterar modelos
docker compose -f docker-compose.dev.yml exec django-web python manage.py makemigrations

# Aplicar migrations dentro do container
docker compose -f docker-compose.dev.yml exec django-web python manage.py migrate

# Criar superusuário dentro do container
docker compose -f docker-compose.dev.yml exec django-web python manage.py createsuperuser

# Popular setores e usuários de exemplo (só com DEBUG=True)
docker compose -f docker-compose.dev.yml exec django-web python /app/scripts/utils/popular_banco.py

# Abrir o shell Django dentro do container
docker compose -f docker-compose.dev.yml exec django-web python manage.py shell
```

## Testes

A suíte usa um Compose exclusivo (`docker-compose.test.yml`), que cria o banco temporário `test_<POSTGRES_DB>` no PostgreSQL externo e não exige que o ambiente de desenvolvimento esteja ativo:

```bash
# Suíte completa
make test

# Por camada
make test-unit
make test-integration
make test-e2e

# Por app ou por app e camada
make test TEST_TARGET=tests.core
make test TEST_TARGET=tests.core.unit
```

Os testes ficam em `src/tests/<app>/{unit,integration,e2e}/`. Consulte o guia de [testes automatizados](testes.md) para escolher a camada, o tipo de caso Django e os filtros de execução.

## Frontend

O CSS de origem fica em `src/apps/theme/static_src/src/styles.css` (Tailwind CSS 4 + DaisyUI 5), com o tema DaisyUI do projeto, e o Tailwind escaneia as classes de todo o `src/`. O layout compartilhado é `src/templates/base.html`.

Diretrizes:

- prefira componentes DaisyUI;
- use cores semânticas como `primary`, `success`, `warning` e `error`;
- use Tailwind para layout, espaçamento e responsividade;
- evite CSS específico quando uma composição existente resolver;
- ao introduzir um padrão visual novo, registre-o no [catálogo de componentes](../exemplos_componentes/README.md), em arquivo próprio.

O serviço `tailwind` executa `npm ci` ao iniciar e mantém o watcher (`npm run dev`) ativo. Para validar um build de produção isolado:

```bash
docker compose -f docker-compose.dev.yml run --rm --no-deps tailwind sh -c "npm ci && npm run build"
# ou
make tailwind-build
```

## Adicionar uma nova área

1. Crie o app em `src/apps/<nome>/` com `apps.py` (`name = "apps.<nome>"`), `__init__.py` e os pacotes `models/`, `admin/`, `selectors/`, `services/`, `views/` e `migrations/` (com `__init__.py`); registre-o em `INSTALLED_APPS` como `apps.<nome>.apps.<Nome>Config`.
2. Crie `urls.py` com `app_name = "<nome>"` e inclua-o em `src/config/urls.py`.
3. Coloque os templates em `src/templates/<nome>/` e os testes em `src/tests/<nome>/{unit,integration,e2e}/test_*.py` (cada pasta com `__init__.py`; ver [testes automatizados](testes.md)).
4. Decida o papel de acesso: área de gestão → proteja views, APIs e exportações com `@gestor_requerido` (`src/apps/core/decorators.py`); área de usuário comum → `@login_required`, com validação de dono em `selectors/`/`services/` quando aplicável.
5. Adicione a navegação em `src/templates/base.html` (blocos `nav_itens` e `nav_itens_mobile`), usando `usuario_e_gestor` para mostrar/ocultar itens de gestão, e registre o namespace em `SECOES_POR_NAMESPACE` (`src/apps/core/processadores_contexto.py`) para destacar o item ativo.
6. Atualize a home, se for o caso.
7. Documente a área e sua permissão em `docs/modulos/<nome>.md` (a partir de [`_modelo.md`](../modulos/_modelo.md)) e no `AGENTS.md`.

## Alterar permissões

Não duplique regras de acesso nas views — a checagem sempre passa por `src/apps/core/selectors/permissoes.py::usuario_e_gestor`. Para mudar quem é a equipe gestora, marque/desmarque `gestor_sistema` no(s) `Setor`(es) corretos via `/admin/`; não é preciso alterar código.

## Dependências Python

`pyproject.toml` e `poetry.lock` são a única fonte das dependências Python. O Poetry no host serve apenas para alterar e validar esses arquivos; ele não executa a aplicação. Consulte [Dependências Python com Poetry](dependencias-poetry.md).

## Encerrar o ambiente

```bash
docker compose -f docker-compose.dev.yml down
```

Os volumes são preservados. `docker compose -f docker-compose.dev.yml down -v` apaga o Redis e o `node_modules` de desenvolvimento (o banco externo não é afetado) — use apenas quando quiser recriar o ambiente do zero.
