# Variáveis de ambiente

O projeto carrega `.env` com `python-dotenv` (`load_dotenv()` em `settings.py`), e os arquivos Compose também fornecem o arquivo aos containers via `env_file` e o usam para interpolar nomes e portas. Comece sempre pela cópia de `.env.example`.

```bash
# Executar no host
cp .env.example .env
```

## Identificação do projeto e portas

| Variável | Padrão | Descrição |
| --- | --- | --- |
| `APP_NOME` | `Projeto Base` | nome exibido no título das páginas, no cabeçalho e no rodapé |
| `COMPOSE_PROJECT_NAME` | nome da pasta | prefixo de containers, volumes e rede do Compose — use um valor único por projeto |
| `APP_IMAGE` | `projeto-base` | nome da imagem Docker (`:dev` no desenvolvimento, `:latest` no completo) |
| `APP_PORT` | `8001` | porta da aplicação no host (Nginx no completo, `runserver` no dev) |
| `DB_PORT` | `5433` | porta do PostgreSQL no host (só dev, em `127.0.0.1`) |
| `REDIS_PORT` | `6379` | porta do Redis no host (só dev, em `127.0.0.1`) |
| `FLOWER_PORT` | `5555` | porta do Flower no host (profile `celery`) |

Ao mudar `APP_PORT`, ajuste também `DJANGO_CSRF_TRUSTED_ORIGINS`.

A suíte (`docker-compose.test.yml`) não lê o `.env`: o runner recebe configurações fixas de teste. O `Makefile` só lê `APP_IMAGE` dele, para nomear a imagem (`<APP_IMAGE>:test`, sobrescrevível com `TEST_IMAGE`) e o projeto Compose da suíte (`<APP_IMAGE>-test`, sobrescrevível com `TEST_PROJECT_NAME`).

## Django

| Variável | Obrigatória | Descrição |
| --- | --- | --- |
| `SECRET_KEY` | sim | chave criptográfica do Django; use um valor longo e exclusivo |
| `DEBUG` | sim | somente a string `True` ativa o modo de desenvolvimento |
| `DJANGO_ALLOWED_HOSTS` | sim | hosts separados por vírgula, sem colchetes (padrão: `localhost,127.0.0.1`) |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | recomendada | origens completas, com protocolo, separadas por vírgula (padrão: `https://127.0.0.1`) |

Exemplo local:

```dotenv
DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,django-web
DJANGO_CSRF_TRUSTED_ORIGINS=http://localhost:8001,http://127.0.0.1:8001
```

## PostgreSQL principal

| Variável | Descrição |
| --- | --- |
| `POSTGRES_DB` | nome do banco criado pelo container |
| `POSTGRES_USER` | usuário do banco |
| `POSTGRES_PASSWORD` | senha do banco |
| `POSTGRES_HOST` | use `db` dentro do Compose (padrão do código: `localhost`) |
| `POSTGRES_PORT` | normalmente `5432` (porta interna da rede Docker) |

## SMTP

| Variável | Descrição |
| --- | --- |
| `EMAIL_HOST` | servidor SMTP (padrão `smtp.gmail.com`) |
| `EMAIL_PORT` | porta numérica, normalmente `587`; convertida com `int()` |
| `EMAIL_HOST_USER` | usuário SMTP |
| `EMAIL_HOST_PASSWORD` | senha ou token de aplicativo |
| `EMAIL_FROM` | remetente padrão (`DEFAULT_FROM_EMAIL`); vazio usa `EMAIL_HOST_USER` |

## Redis e Celery

| Variável | Valor usual no Compose |
| --- | --- |
| `CELERY_BROKER_URL` | `redis://redis:6379/0` |
| `CELERY_RESULT_BACKEND` | `redis://redis:6379/0` |

## Flower

| Variável | Descrição |
| --- | --- |
| `FLOWER_USER` | usuário da interface Flower |
| `FLOWER_PASSWORD` | senha da interface Flower |

## Arquivos sensíveis

O `.env` é ignorado pelo Git. Certificados e chaves de integrações (LDAP, APIs) também devem ficar fora do Git — acrescente-os ao `.gitignore` ao criá-los. Não copie valores reais para documentação, logs, commits ou imagens públicas.
