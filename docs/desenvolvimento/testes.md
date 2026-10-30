# Testes automatizados

A suíte usa o test runner nativo do Django e é organizada por aplicação e camada:

```text
src/tests/
├── __init__.py
├── _apoio.py              # helpers compartilhados (login, usuários com/sem cargo, gestor)
└── <app>/
    ├── __init__.py
    ├── unit/
    │   └── test_*.py
    ├── integration/
    │   └── test_*.py
    └── e2e/
        └── test_*.py
```

Todas essas pastas são pacotes Python e devem conter `__init__.py`. O base já traz `core/` (com casos) e `theme/` (camadas vazias).

## Camadas

- **Unitários (`unit`)**: exercitam regras isoladas, sem banco de dados, rede ou navegador real. Use mocks para isolar integrações.
- **Integração (`integration`)**: exercitam ORM, constraints, e-mail local, Django Admin, processadores de contexto que consultam o banco, services persistentes ou requisições com `django.test.Client`.
- **Ponta a ponta (`e2e`)**: reservados a fluxos com live server e navegador real. Essa camada ainda não possui casos de teste.

O uso do Django Client não torna um teste E2E: ele executa a aplicação no próprio processo e, neste projeto, é classificado como integração.

Prefira `SimpleTestCase` quando o caso não acessar o banco. Use `TestCase` quando o teste depender do ORM ou da transação isolada fornecida pelo Django. Uma tentativa de consultar o banco a partir de `SimpleTestCase` falha, ajudando a manter a separação explícita.

O que testar em cada camada de código (services, selectors, views) está em [Camadas de código](../arquitetura/camadas-e-padroes-de-codigo.md#8-testes).

## Helpers compartilhados

`src/tests/_apoio.py` concentra o setup repetido dos testes de integração. Como o nome não começa com `test_`, o runner não o coleta:

- `login(usuario)`: devolve um `Client` já autenticado;
- `criar_usuario_com_setor(nome_setor, username, gestor_sistema=False)`: usuário com cargo ativo no setor;
- `criar_gestor(username, nome_setor)`: usuário com cargo num setor com `gestor_sistema=True`;
- `criar_usuario_sem_cargo(username)`: usuário autenticável sem nenhum cargo.

Importe com `from tests._apoio import login, criar_gestor`. Acrescente aqui um helper quando ele for útil a mais de um app; o que é específico de um app fica no próprio módulo de teste.

## Execução

Execute os comandos no host. O Makefile constrói o runner exclusivo de teste, que usa o PostgreSQL externo do `.env`:

```bash
# Suíte completa
make test

# Uma camada em todos os apps
make test-unit
make test-integration
make test-e2e

# Análise de segurança do código Python
make bandit

# Um app completo
make test TEST_TARGET=tests.core

# Uma camada de um app
make test TEST_TARGET=tests.core.unit
```

Os targets por camada descobrem automaticamente os apps que possuem `src/tests/<app>/__init__.py`; não há uma lista de apps para manter no Makefile.

O target `make bandit` executa o Bandit (grupo Poetry `dev`) no mesmo container de testes e analisa os apps Django (`src/apps/`), o projeto (`src/config/`), o `manage.py` e os scripts em `scripts/`. A execução bloqueia achados de severidade média ou alta com confiança alta; ocorrências de menor severidade ou confiança permanecem visíveis no relatório, mas não interrompem o comando.

Sem `make` disponível, o equivalente é `docker compose -f docker-compose.test.yml -p <APP_IMAGE>-test up --build --abort-on-container-exit --exit-code-from test-runner`, seguido de `docker compose -f docker-compose.test.yml -p <APP_IMAGE>-test down --volumes --remove-orphans`. Sempre informe `-p`: sem ele, o Compose usa o `COMPOSE_PROJECT_NAME` do `.env`, que é o do ambiente de desenvolvimento, e o `--remove-orphans` derrubaria os containers de dev.

## Banco de testes e limpeza

O `docker-compose.test.yml` não sobe banco: o runner se conecta ao mesmo PostgreSQL externo do projeto, pelas variáveis `POSTGRES_*` do `.env` (sobrescrevíveis no shell, ex. `POSTGRES_HOST=outro-servidor make test`). O usuário precisa de permissão `CREATEDB`. O runner é construído com `POETRY_INSTALL_GROUPS=dev` (inclui o Bandit) e executa `python manage.py test --noinput`; as demais configurações são locais de teste, sem depender do restante do `.env` nem do ambiente de desenvolvimento. O broker do Celery é `memory://` e o Django troca o backend de e-mail por `locmem` durante os testes.

Durante a execução, o Django cria o banco `test_<POSTGRES_DB>` no servidor, aplica as migrations nele e o remove ao terminar; o banco `POSTGRES_DB` do projeto não é tocado. Se uma execução interrompida deixar o `test_<POSTGRES_DB>` para trás, a próxima o recria (`--noinput`). O Makefile é responsável pelo ciclo do Compose: usa um projeto próprio (`<APP_IMAGE>-test`, sobrescrevível com `TEST_PROJECT_NAME`) e sempre executa `down --volumes --remove-orphans` e remove a imagem `<APP_IMAGE>:test` (`TEST_IMAGE`), inclusive após falha ou interrupção. Assim, a suíte não depende de `django-web` ativo, e vários projetos derivados do base podem rodar a suíte na mesma máquina (cada um com seu `POSTGRES_DB`).

Em CI, defina `TEST_PROJECT_NAME` e `TEST_IMAGE` com o identificador da execução (ex. `projeto-base-test-${{ github.run_id }}`) para que jobs simultâneos não colidam.

## Adicionar testes

Para um app novo chamado `relatorios`:

1. Crie `src/tests/relatorios/__init__.py`.
2. Crie `unit/`, `integration/` e `e2e/`, cada qual com seu `__init__.py`.
3. Salve cada caso em `test_*.py` na camada correspondente.
4. Importe o código da aplicação pelo namespace `apps.relatorios` e os helpers de `tests._apoio`.
5. Execute `make test TEST_TARGET=tests.relatorios` e depois a suíte completa com `make test`.

Mesmo que uma camada ainda esteja vazia, mantenha seu pacote. Isso preserva a estrutura uniforme e permite que os targets do Makefile a descubram automaticamente.
