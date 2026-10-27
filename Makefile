SHELL := /bin/sh

# Nome da imagem lido do .env (APP_IMAGE); identifica a imagem e o projeto Compose da suíte.
APP_IMAGE ?= $(or $(shell sed -n 's/^APP_IMAGE=//p' .env 2>/dev/null | tr -d '\r'),projeto-base)
TEST_PROJECT_NAME ?= $(APP_IMAGE)-test
export TEST_IMAGE ?= $(APP_IMAGE):test

COMPOSE := docker compose
COMPOSE_DEV := $(COMPOSE) -f docker-compose.dev.yml
COMPOSE_DEV_CELERY := $(COMPOSE_DEV) --profile celery
COMPOSE_PROD := $(COMPOSE) -f docker-compose.yml
# Projeto próprio (-p): o COMPOSE_PROJECT_NAME do .env é o do ambiente de desenvolvimento,
# e o "down --remove-orphans" da suíte não pode alcançar os containers dele.
COMPOSE_TEST := $(COMPOSE) -f docker-compose.test.yml -p $(TEST_PROJECT_NAME)
DJANGO_SERVICE := django-web
TAILWIND_SERVICE := tailwind
CELERY_SERVICES := celery-worker celery-worker-rpa celery-beat flower
APP_SERVICES := $(TAILWIND_SERVICE) $(DJANGO_SERVICE) $(CELERY_SERVICES)
APP_LABEL ?=
TEST_TARGET ?=
TEST_APP_PACKAGES := $(wildcard src/tests/*/__init__.py)
TEST_APPS := $(sort $(notdir $(patsubst %/,%,$(dir $(TEST_APP_PACKAGES)))))
TEST_UNIT_TARGETS := $(addsuffix .unit,$(addprefix tests.,$(TEST_APPS)))
TEST_INTEGRATION_TARGETS := $(addsuffix .integration,$(addprefix tests.,$(TEST_APPS)))
TEST_E2E_TARGETS := $(addsuffix .e2e,$(addprefix tests.,$(TEST_APPS)))

.DEFAULT_GOAL := help

.PHONY: help up up-min down restart ps logs logs-app logs-celery \
	check test test-unit test-integration test-e2e bandit \
	makemigrations migrations-check migrate createsuperuser shell \
	tailwind-build poetry-check compose-check validate

# Remove containers, rede, volumes e a imagem da suíte ao sair, inclusive após falha ou Ctrl+C.
define test_cleanup
	set -eu; \
	cleanup() { \
		$(COMPOSE_TEST) down --volumes --remove-orphans; \
		docker image rm -f "$(TEST_IMAGE)" >/dev/null 2>&1 || true; \
	}; \
	trap 'status=$$?; trap - EXIT INT TERM; cleanup || true; exit $$status' EXIT; \
	trap 'exit 130' INT; \
	trap 'exit 143' TERM;
endef

define run_tests
	@$(test_cleanup) \
	TEST_TARGET="$(1)" $(COMPOSE_TEST) up --build --abort-on-container-exit --exit-code-from test-runner
endef

help: ## Lista os comandos disponíveis
	@awk 'BEGIN {FS = ":.*## "; printf "Uso: make <comando>\n\nComandos:\n"} /^[a-zA-Z0-9_-]+:.*## / {printf "  %-22s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

up: ## Sobe o ambiente de desenvolvimento completo (inclui worker rpa e Flower)
	$(COMPOSE_DEV_CELERY) up --build

up-min: ## Sobe o ambiente de desenvolvimento sem o worker rpa e o Flower
	$(COMPOSE_DEV) up --build

down: ## Encerra o ambiente mantendo os volumes
	$(COMPOSE_DEV_CELERY) down --remove-orphans

restart: ## Reinicia os processos contínuos (ex. após alterar tasks) sem repetir migrations
	$(COMPOSE_DEV_CELERY) restart $(APP_SERVICES)

ps: ## Mostra o estado dos containers de desenvolvimento
	$(COMPOSE_DEV_CELERY) ps --all

logs: ## Acompanha os logs de todos os serviços
	$(COMPOSE_DEV_CELERY) logs -f

logs-app: ## Acompanha os logs do Django
	$(COMPOSE_DEV) logs -f $(DJANGO_SERVICE)

logs-celery: ## Acompanha os logs dos workers, Beat e Flower
	$(COMPOSE_DEV_CELERY) logs -f $(CELERY_SERVICES)

check: ## Executa o Django check dentro do container
	$(COMPOSE_DEV) exec $(DJANGO_SERVICE) python manage.py check

test: ## Executa a suíte completa isolada; use TEST_TARGET=tests.nome_do_app para filtrar
	$(call run_tests,$(TEST_TARGET))

test-unit: ## Executa os testes unitários de todos os apps
	$(call run_tests,$(TEST_UNIT_TARGETS))

test-integration: ## Executa os testes de integração de todos os apps
	$(call run_tests,$(TEST_INTEGRATION_TARGETS))

test-e2e: ## Executa os testes E2E de todos os apps
	$(call run_tests,$(TEST_E2E_TARGETS))

bandit: ## Executa a análise de segurança do Python
	@$(test_cleanup) \
	$(COMPOSE_TEST) run --rm --no-deps --build test-runner bandit \
		--severity-level medium \
		--confidence-level high \
		-r apps config manage.py ../scripts

makemigrations: ## Gera migrations; use APP_LABEL=nome_do_app para filtrar
	$(COMPOSE_DEV) exec $(DJANGO_SERVICE) python manage.py makemigrations $(APP_LABEL)

migrations-check: ## Verifica se existem models sem migration
	$(COMPOSE_DEV) exec $(DJANGO_SERVICE) python manage.py makemigrations --check --dry-run

migrate: ## Aplica migrations; use APP_LABEL=nome_do_app para filtrar
	$(COMPOSE_DEV) exec $(DJANGO_SERVICE) python manage.py migrate $(APP_LABEL)

createsuperuser: ## Cria um superusuário interativamente
	$(COMPOSE_DEV) exec $(DJANGO_SERVICE) python manage.py createsuperuser

shell: ## Abre o shell do Django
	$(COMPOSE_DEV) exec $(DJANGO_SERVICE) python manage.py shell

tailwind-build: ## Gera o CSS de produção em um container descartável
	$(COMPOSE_DEV) run --rm --no-deps $(TAILWIND_SERVICE) sh -c "npm ci && npm run build"

poetry-check: ## Valida pyproject.toml e poetry.lock no host
	poetry check --lock

compose-check: ## Valida os arquivos Compose
	$(COMPOSE_PROD) config --quiet
	$(COMPOSE_DEV) config --quiet
	$(COMPOSE_TEST) config --quiet

validate: compose-check poetry-check check migrations-check test tailwind-build ## Executa as validações principais
