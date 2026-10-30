# Instalação com Docker

## Requisitos

- Git;
- Docker Engine ou Docker Desktop;
- Docker Compose v2, disponível pelo comando `docker compose`.

Não é necessário instalar Python, Node.js ou Redis diretamente na máquina. O PostgreSQL é externo: nenhum compose sobe banco, e é preciso um servidor PostgreSQL 17 acessível pelos containers. O Poetry no host é usado somente para alterar `pyproject.toml` e `poetry.lock`.

Para desenvolvimento, o fluxo recomendado é `docker-compose.dev.yml`, descrito em [Desenvolvimento com Docker Compose](../desenvolvimento/fluxo-local.md). O `docker-compose.yml` completo desta página representa o ambiente integrado usado em implantação.

## 1. Obter o projeto

```bash
# Executar no host
git clone <url-do-repositorio>
cd <pasta-do-projeto>
```

## 2. Criar o arquivo de ambiente

```bash
# Executar no host
cp .env.example .env
```

Revise pelo menos:

- `APP_NOME`, `COMPOSE_PROJECT_NAME`, `APP_IMAGE` e `APP_PORT`;
- `SECRET_KEY` e `DEBUG` (`False` em produção);
- `DJANGO_ALLOWED_HOSTS` e `DJANGO_CSRF_TRUSTED_ORIGINS`;
- conexão com o PostgreSQL externo (`POSTGRES_*`; `POSTGRES_HOST` é um PostgreSQL externo (hostname ou IP do servidor; `host.docker.internal` para um PostgreSQL instalado no próprio host) — nunca `localhost`, que dentro do container é o próprio container);
- SMTP (`EMAIL_*`);
- credenciais do Flower (`FLOWER_USER`, `FLOWER_PASSWORD`).

Consulte a [referência de variáveis de ambiente](../configuracao/variaveis-ambiente.md).

## 3. Subir o ambiente completo

```bash
# Executar no host; os serviços rodam nos containers
docker compose up --build -d
```

Na primeira inicialização, o Docker:

1. cria o Redis (com healthcheck); o PostgreSQL já deve existir e estar acessível;
2. compila o frontend e sincroniza `poetry.lock` em `/opt/venv` durante o build da imagem;
3. executa `migrate` pelo serviço `migrate`;
4. executa `collectstatic` e preenche o volume `static_files`;
5. inicia Gunicorn, o worker Celery da fila `celery`, o Celery Beat e o Nginx.

O worker da fila `rpa` e o Flower ficam sob o profile `celery`. Para subi-los também:

```bash
# Executar no host
docker compose --profile celery up --build -d
```

Confira o estado e os logs:

```bash
# Executar no host
docker compose ps
docker compose logs -f django-web frontend-proxy
```

## 4. Criar o primeiro superusuário

```bash
# Executar no host; o comando Django roda dentro de django-web
docker compose exec django-web python manage.py createsuperuser
```

Acesse:

- aplicação: `http://localhost:8001`;
- administração Django: `http://localhost:8001/admin/`;
- Flower (com `--profile celery`): `http://localhost:5555`.

## Serviços do compose completo

| Serviço | Função | Porta no host (padrão) | Tipo |
| --- | --- | --- | --- |
| `redis` | broker e resultados do Celery | — (só rede interna) | contínuo |
| `migrate` | migrations do Django | — | execução única |
| `collectstatic` | coleta de arquivos estáticos no volume `static_files` | — | execução única |
| `django-web` | aplicação via Gunicorn (`0.0.0.0:8000`) | — (via Nginx) | contínuo |
| `celery-worker` | fila `celery` | — | contínuo |
| `celery-worker-rpa` | fila `rpa`, concorrência 1 | — | profile `celery` |
| `celery-beat` | disparo dos agendamentos | — | contínuo |
| `flower` | monitoramento do Celery | `5555` (`FLOWER_PORT`) | profile `celery` |
| `frontend-proxy` | Nginx e arquivos estáticos | `8001` → `80` (`APP_PORT`) | contínuo |

Os serviços contínuos usam `restart: unless-stopped`. O serviço `migrate` executa apenas `migrate --noinput`; as migrations devem ser geradas e revisadas antes da implantação.

## Comandos de manutenção

```bash
# Executar no host; o comando Django roda dentro do container
docker compose exec django-web python manage.py check

# Executar no host; aplicar migrations em um container descartável
docker compose run --rm migrate

# Executar no host; acompanhar todos os logs
docker compose logs -f

# Executar no host; reconstruir após mudança de dependências ou Dockerfile
docker compose up --build -d

# Executar no host; parar os containers mantendo os volumes
docker compose down
```

`docker compose down -v` também remove os volumes (`redis_data`, `static_files`). O banco é externo e não é afetado. Use apenas quando a intenção for recriar completamente o ambiente.

## Poetry e atualização das dependências

O build usa exclusivamente `pyproject.toml` e `poetry.lock`. O Poetry é instalado apenas no estágio intermediário do Dockerfile; a imagem executada pelos serviços já contém a virtualenv pronta em `/opt/venv`.

Depois de receber uma mudança nesses arquivos, reconstrua a imagem:

```bash
# Executar no host do servidor
docker compose up -d --build --remove-orphans
```

Não remova volumes Docker para atualizar bibliotecas. Para administrar dependências no desenvolvimento, consulte [Dependências Python com Poetry](../desenvolvimento/dependencias-poetry.md).
