# Dependências Python com Poetry

## Fonte de verdade

O projeto usa Poetry 2.4 para gerenciar as dependências Python:

- `pyproject.toml` declara o Python suportado (`>=3.13`) e as dependências diretas;
- `poetry.lock` fixa as versões diretas e transitivas usadas nas imagens;
- os dois arquivos devem ser atualizados e versionados juntos.

Não existem arquivos `requirements*.txt` neste projeto. Não os crie nem use `pip install -r`.

## Modelo de execução

A aplicação deve ser executada e validada pelo `docker-compose.dev.yml`. Uma `.venv` no host é opcional para IDEs ou ferramentas auxiliares, mas não é necessária nem representa o ambiente oficial. O Dockerfile instala o Poetry apenas no estágio `builder`, executa `poetry sync --only main --no-root` em `/opt/venv` e copia essa virtualenv para a imagem final.

O Poetry instalado no host é usado principalmente para alterar e validar `pyproject.toml` e `poetry.lock`. Use `--lock` para atualizar somente esses arquivos, sem instalar o pacote em uma virtualenv local.

## Preparar o Poetry no host

Instale o `pipx` pelo gerenciador de pacotes do host e, com ele disponível:

```bash
# Executar no host, uma única vez
pipx ensurepath

# Executar no host, uma única vez
pipx install --force "poetry==2.4.1"

# Conferir a ferramenta
poetry --version
```

Python 3.13/3.14, Node.js e as bibliotecas da aplicação não precisam ser instalados no host.

## Adicionar, remover e atualizar pacotes

```bash
# Escolher uma versão compatível e atualizar somente manifesto/lock
poetry add --lock nome-do-pacote

# Fixar uma versão específica
poetry add --lock "nome-do-pacote==1.2.3"

# Dependência exclusiva de desenvolvimento ou testes
poetry add --group dev --lock nome-do-pacote

# Remover do manifesto e recalcular o lock
poetry remove --lock nome-do-pacote

# Atualizar somente um pacote no lock
poetry update --lock nome-do-pacote

# Recalcular o lock após uma edição manual excepcional do pyproject.toml
poetry lock

# Validar a consistência entre manifesto e lockfile
poetry check --lock
```

O Dockerfile instala apenas o grupo `main`. Ao criar um grupo `dev`, ajuste explicitamente a imagem usada em desenvolvimento antes de depender da ferramenta dentro do container.

Evite `poetry update --lock` sem indicar um pacote, salvo quando o objetivo for atualizar todo o conjunto. Nunca edite `poetry.lock` manualmente e não instale pacotes em um container em execução.

## Instalar as dependências

No fluxo oficial, instalar significa reconstruir a imagem:

```bash
docker compose -f docker-compose.dev.yml up --build
```

Uma mudança em `pyproject.toml` ou `poetry.lock` invalida a camada de dependências, e o próximo build recria `/opt/venv` dentro da imagem. O bind mount `.:/app` não oculta essa virtualenv porque ela fica fora de `/app`.

## Fluxo completo depois de mudar uma dependência

```bash
# 1. No host: validar os arquivos do Poetry
poetry check --lock

# 2. No host: reconstruir e iniciar o ambiente de desenvolvimento
docker compose -f docker-compose.dev.yml up --build -d

# 3. No host; Python executa dentro do container django-web
docker compose -f docker-compose.dev.yml exec django-web python manage.py check

# 4. No host; confirmar uma importação dentro do mesmo ambiente da aplicação
docker compose -f docker-compose.dev.yml exec django-web python -c "import nome_do_modulo"
```

Revise e versione `pyproject.toml` e `poetry.lock` juntos. Se um módulo usado diretamente pelo projeto estiver presente apenas como dependência transitiva, declare-o explicitamente com `poetry add --lock`.

## Atualização do servidor

```bash
docker compose up -d --build --remove-orphans
```

Não use `docker compose down -v` para atualizar dependências: isso remove volumes e apaga o PostgreSQL.
