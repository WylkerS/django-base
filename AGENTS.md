# AGENTS.md — Projeto Base

## Objetivo

<!-- PREENCHER: descreva o sistema (o que faz, para quem) ao iniciar um projeto a partir do base. -->

Este repositório é o **projeto base** dos sistemas Django internos: stack, estrutura, camadas de código, documentação e ambiente Docker extraídos do Agendamento de Salas (arquitetura herdada do Portal do Analista). Cada sistema novo nasce de uma cópia dele.

Ao alterar o projeto, preserve as regras de acesso por setor, o padrão de apps de domínio e o padrão visual Tailwind CSS / DaisyUI. Mantenha a documentação em `docs/` coerente com a mudança.

## Estado atual do projeto

Concluído: esqueleto Django (`src/config/`), app `core` (`Usuario`, `Setor`, `Cargo`, login/logout, home e a política de acesso — `Setor.gestor_sistema`, `src/apps/core/selectors/permissoes.py`, `src/apps/core/decorators.py`, `src/apps/core/processadores_contexto.py`), app `theme` (Tailwind CSS 4 + DaisyUI 5, tema provisório `base`), integração com Celery, ambiente Docker (`docker-compose.yml`, `docker-compose.dev.yml` e `docker-compose.test.yml`), `Makefile` e suíte de testes por camada (`unit`/`integration`/`e2e`).

<!-- PREENCHER: apps de domínio implementados e planejados. -->

## Fluxo de desenvolvimento recomendado

Use sempre o ambiente Docker com atualização automática. Não execute Django, Celery ou npm diretamente no host:

```bash
# Executar no host; os serviços rodam nos containers
docker compose -f docker-compose.dev.yml up --build
```

A aplicação fica em `http://localhost:8001` (porta `APP_PORT` do `.env`). O compose de desenvolvimento executa Redis, migrations, Django com autoreload, Tailwind em modo watch, o worker Celery da fila `celery` e o Celery Beat; com `--profile celery`, também sobem o worker da fila `rpa` e o Flower. Worker e beat não recarregam sozinhos: reinicie-os (`docker compose -f docker-compose.dev.yml restart celery-worker celery-beat`) após alterar tasks ou os services que elas chamam.

Nenhum compose sobe banco de dados: a aplicação, as tasks e a suíte apontam para um PostgreSQL externo configurado pelas variáveis `POSTGRES_*` do `.env`.

Comandos frequentes:

```bash
# Executar no host; cada comando roda no container indicado
docker compose -f docker-compose.dev.yml exec django-web python manage.py check
docker compose -f docker-compose.dev.yml exec django-web python manage.py makemigrations
docker compose -f docker-compose.dev.yml exec django-web python manage.py migrate
docker compose -f docker-compose.dev.yml exec django-web python manage.py createsuperuser
docker compose -f docker-compose.dev.yml run --rm --no-deps tailwind sh -c "npm ci && npm run build"

# Executar no host; a suíte usa um runner próprio (docker-compose.test.yml) e cria test_<POSTGRES_DB> no banco externo
make test
make test-unit
make test-integration
make test-e2e
make test TEST_TARGET=tests.core
make bandit
```

O `Makefile` também encurta os comandos do Compose (`make up`, `make up-min`, `make check`, `make migrate`, `make restart`, `make validate`...); `make` sem argumentos lista todos. Ver [`docs/desenvolvimento/fluxo-local.md`](docs/desenvolvimento/fluxo-local.md#atalhos-do-makefile).

O compose completo é iniciado com:

```bash
# Executar no host do servidor
docker compose up --build -d
```

Nele, como no de desenvolvimento, o worker da fila `celery` e o Celery Beat sobem sempre; o worker da fila `rpa` e o Flower só com `--profile celery`.

Nome do projeto Compose, imagem e portas vêm do `.env` (`COMPOSE_PROJECT_NAME`, `APP_IMAGE`, `APP_PORT`, `REDIS_PORT`, `FLOWER_PORT`). Não fixe `container_name` nos serviços: vários projetos derivados do base precisam conviver na mesma máquina.

## Aplicações e arquitetura

O código Django fica em `src/`. O projeto está em `src/config/` (settings, urls, wsgi, asgi e `celery.py`), os apps em `src/apps/<nome>/`, os templates compartilhados em `src/templates/` (`base.html` e `403.html` na raiz, `partials/` e uma pasta por app) e os testes em `src/tests/<app>/{unit,integration,e2e}/test_*.py`, com helpers compartilhados em `src/tests/_apoio.py`. Use o namespace `apps.<nome>` nos imports Python entre aplicações. `.env`, `staticfiles/` e `media/` ficam na raiz do repositório (`PROJECT_ROOT`).

Registradas em `INSTALLED_APPS` (como `apps.<nome>.apps.<Nome>Config`): `core` e `theme`, além de `django_celery_beat` e `tailwind`.

- `core`: usuário (`core.Usuario`), setores, cargos, login/logout, a home e a política de acesso (`selectors/permissoes.py`, `decorators.py`, `processadores_contexto.py`);
- `theme`: build do Tailwind CSS e DaisyUI (`django-tailwind`, `TAILWIND_APP_NAME = "theme"`).

<!-- PREENCHER: apps de domínio (nome, responsabilidade, link para docs/modulos/<app>.md). -->

Organização de cada app de domínio: pacotes `models/`, `views/` e `admin/` com `__init__.py` reexportando os símbolos públicos; `urls.py` com rotas nomeadas e `app_name` (namespace); escrita em `services/`; leitura composta (filtros, `annotate`, `select_related`) em `selectors/`; tarefas Celery em `tasks.py`. Views são **funções** (sem Class-Based Views), com `@gestor_requerido`/`@login_required`, `messages`, `get_object_or_404` e `@require_POST` nas mutações. **Sem `forms.py`/Django Forms** — views leem `request.POST`/`request.GET` diretamente. Templates do app em `src/templates/<app>/` e testes em `src/tests/<app>/`, nunca dentro do app. Regras completas de cada camada em [`docs/arquitetura/camadas-e-padroes-de-codigo.md`](docs/arquitetura/camadas-e-padroes-de-codigo.md).

## Banco de dados

Um único alias `default`: PostgreSQL 17 **externo**, apontado por `POSTGRES_*` no `.env`. Não acrescente serviço de banco aos arquivos Compose. <!-- PREENCHER: bases externas, se houver. -->

As migrations ficam em `src/apps/<app>/migrations/` e são versionadas. O namespace Python `apps.<nome>` não altera o label Django do app: dependências e relações nas migrations usam labels simples como `core`. Crie migrations somente quando modelos Django forem alterados. Revise os arquivos gerados antes de aplicar. Não gere migrations vazias ou não relacionadas à tarefa. O serviço `migrate` do compose completo executa apenas `migrate --noinput`; gere e revise as migrations antes da implantação. Fluxo completo em [`docs/desenvolvimento/migrations.md`](docs/desenvolvimento/migrations.md).

## Autenticação e acesso

A autenticação usa o `ModelBackend` do Django (usuário e senha locais). Para autenticação institucional (LDAP, SSO), acrescente o backend em `AUTHENTICATION_BACKENDS`, antes do `ModelBackend`, e documente-o em `docs/seguranca/autenticacao-e-permissoes.md`.

O modelo autenticável é `core.Usuario`, definido em `src/apps/core/models/usuario.py` a partir de `AbstractUser` (e-mail único). Use `get_user_model()` em código executado e `settings.AUTH_USER_MODEL` em relações de models; não importe o `User` padrão diretamente. Novos campos exigem migration, testes e ajuste do `UsuarioAdmin` quando forem administráveis.

Um `Cargo` vincula usuário a `Setor` (com `nivel` e `ativo`) e só concede acesso com o cargo **e** o setor ativos.

Papéis do sistema, definidos por dados (não hardcoded em Python):

| Papel | Regra |
| --- | --- |
| Usuário comum | qualquer usuário autenticado (`@login_required`) |
| Gestor do sistema | cargo ativo num setor ativo com `Setor.gestor_sistema=True` (`@gestor_requerido`) |

Superusuários são sempre gestores, mesmo sem cargo cadastrado.

Regras obrigatórias:

- proteja páginas, APIs, exportações e mutações de gestão com `@gestor_requerido` (`src/apps/core/decorators.py`); áreas do usuário comum usam `@login_required`;
- não considere a ocultação de um item de menu uma proteção de segurança;
- defina quem é a equipe gestora marcando `gestor_sistema` no(s) `Setor`(es) corretos via `/admin/`, sem duplicar regras nas views — a checagem sempre passa por `src/apps/core/selectors/permissoes.py::usuario_e_gestor`;
- ao adicionar uma área nova, atualize home, navegação e documentação;
- cargos e setores desativados não concedem acesso.

## Interface

O frontend usa Tailwind CSS 4 e DaisyUI 5 pelo app `theme`. O CSS de origem é `src/apps/theme/static_src/src/styles.css`, que define o tema DaisyUI do projeto (provisório `base` até o Design System ser aplicado). O layout base é `src/templates/base.html` (cabeçalho, navegação, mensagens); a tela de login o estende sobrescrevendo o bloco `corpo`. O Design System do projeto fica em `docs/design_system/` e os componentes reutilizáveis são catalogados em `docs/exemplos_componentes/` (um arquivo por componente; índice no `README.md`).

Diretrizes:

- prefira componentes DaisyUI;
- use cores semânticas (`primary`, `success`, `warning`, `error`, `info`, `base-*`) — nunca hexadecimais ou `style="..."`;
- use Tailwind para layout, espaçamento e responsividade;
- evite CSS personalizado quando houver componente ou utilitário adequado;
- siga o Design System em `docs/design_system/`;
- antes de montar uma tela, consulte o catálogo em `docs/exemplos_componentes/`; ao introduzir um componente novo, documente-o lá em arquivo próprio (a partir de `_modelo-componente.md`) e adicione-o à tabela do `README.md`.

## Celery e tarefas

- fila padrão: `celery`;
- fila `rpa`: para rotinas longas/serializadas (concorrência 1), sob o profile `celery`;
- agendamentos: `django-celery-beat` no PostgreSQL principal, administrados pelo Django Admin; os que o sistema exige são declarados em `CELERY_BEAT_SCHEDULE` (`src/config/settings.py`);
- broker e resultados: Redis;
- monitoramento: Flower (`:5555`), sob o profile `celery` nos dois arquivos compose.

Tasks vivem em `src/apps/<app>/tasks.py`, chamam `services/` e fecham as conexões ao terminar (modelo em `src/apps/core/tasks.py`). Valide SMTP e destinatários antes de habilitar um agendamento.

## Variáveis e dependências

- crie `.env` a partir de `.env.example`;
- `DEBUG` só é ativado pela string `True`;
- `DJANGO_ALLOWED_HOSTS` e `DJANGO_CSRF_TRUSTED_ORIGINS` são listas separadas por vírgula, sem colchetes;
- `POSTGRES_HOST` aponta para o PostgreSQL externo (`host.docker.internal` para um banco no próprio host), nunca `localhost`;
- `pyproject.toml` declara apenas as dependências diretas e `poetry.lock` fixa todo o ambiente;
- use Poetry 2.4 e versione `pyproject.toml` e `poetry.lock` juntos;
- use o Poetry no host apenas para editar e validar os arquivos (`poetry add --lock`, `poetry remove --lock`, `poetry check --lock`);
- não crie arquivos `requirements*.txt` nem edite `poetry.lock` manualmente;
- a imagem Docker sincroniza o grupo `main` em `/opt/venv` durante o build; não é necessário `poetry install`/`sync`/`run` no host;
- não use `pip install` para registrar dependências do projeto;
- dependências de front-end ficam em `src/apps/theme/static_src/package.json` / `package-lock.json`.

Consulte `docs/desenvolvimento/dependencias-poetry.md` antes de atualizar pacotes.

## Validação antes de entregar

Execute conforme o escopo da mudança:

```bash
# No host; Django executa dentro de django-web
docker compose -f docker-compose.dev.yml exec django-web python manage.py check
docker compose -f docker-compose.dev.yml exec django-web python manage.py makemigrations --check --dry-run

# No host; a suíte e o Bandit usam um runner próprio; a suíte cria test_<POSTGRES_DB> no banco externo
make test
make bandit

# No host; Poetry valida somente manifesto/lock
poetry check --lock

# No host; npm executa dentro de um container tailwind descartável
docker compose -f docker-compose.dev.yml run --rm --no-deps tailwind sh -c "npm ci && npm run build"

# No host; validação dos arquivos Compose
docker compose -f docker-compose.yml config --quiet
docker compose -f docker-compose.dev.yml config --quiet
docker compose -f docker-compose.test.yml -p projeto-base-test config --quiet
```

`make validate` executa em sequência a validação dos Compose, o `poetry check --lock`, o `check`, o `makemigrations --check`, a suíte e o build do Tailwind.

Também verifique:

- sintaxe dos templates alterados;
- testes novos ou alterados em `src/tests/<app>/<camada>/test_*.py` e a suíte completa (`make test`; regras em `docs/desenvolvimento/testes.md`);
- `manage.py makemigrations --check --dry-run` sem alterações pendentes;
- proteção de todas as rotas novas;
- ausência de segredos no diff;
- documentação correspondente à mudança;
- `git diff --check` sem erros.

## Arquivos de referência

- `src/config/settings.py`: Django, banco, autenticação e Celery;
- `src/config/celery.py`: app Celery e autodiscover;
- `src/apps/core/models/`: `Usuario`, `Setor` (com `gestor_sistema`) e `Cargo`;
- `src/apps/core/admin/usuario.py`: integração do usuário ao Django Admin;
- `src/apps/core/selectors/permissoes.py`: `usuario_e_gestor`, usado por `src/apps/core/decorators.py::gestor_requerido`;
- `src/apps/core/processadores_contexto.py`: `app_nome`, `usuario_e_gestor` e `secao_ativa` para os templates;
- `src/templates/base.html`: layout compartilhado; `src/templates/403.html`: acesso negado;
- `src/tests/`: suíte automatizada organizada por app e camada (`unit`, `integration`, `e2e`); `src/tests/_apoio.py`: helpers compartilhados;
- `docker-compose.yml`: ambiente completo;
- `docker-compose.dev.yml`: desenvolvimento com autoreload;
- `docker-compose.test.yml`: runner Django da suíte (banco externo do `.env`);
- `Makefile`: atalhos de desenvolvimento, testes (`make test`), Bandit e validação;
- `docs/desenvolvimento/testes.md`: camadas, helpers e execução da suíte;
- `docs/arquitetura/camadas-e-padroes-de-codigo.md`: regras de models, services, selectors e views;
- `docs/README.md`: índice da documentação.
