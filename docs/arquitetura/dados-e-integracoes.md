# Bancos de dados e integrações

## Banco de dados

O arquivo `src/config/settings.py` define um único alias de banco.

| Alias | Tecnologia | Finalidade |
| --- | --- | --- |
| `default` | PostgreSQL 17 | todos os modelos Django: usuários, setores, cargos, agendamentos do Celery Beat e os modelos de domínio |

<!-- PREENCHER: se o projeto consumir bases externas (SQL Server, APIs), acrescente aliases/integrações aqui e em settings.py. -->

O container `db` fornece o PostgreSQL. O volume `postgres_data` preserva os dados do compose completo; o compose de desenvolvimento usa `postgres_data_dev` para não misturar os ambientes. Os volumes recebem o prefixo `COMPOSE_PROJECT_NAME`, então cada projeto derivado tem os seus. Em desenvolvimento, a porta é publicada apenas em `127.0.0.1:${DB_PORT}` (padrão `5433`); no compose completo, o banco não é publicado no host.

As variáveis de conexão (`POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`) inicializam a imagem oficial do PostgreSQL e configuram o alias `default`. Dentro do Compose, `POSTGRES_HOST` deve ser `db` — nunca `localhost`.

## Autenticação

O base usa apenas o `ModelBackend` do Django. Para integrar um provedor institucional (LDAP, SSO), crie o backend em `src/config/` ou em `src/apps/core/`, acrescente-o em `AUTHENTICATION_BACKENDS` antes do `ModelBackend` e documente aqui: servidor, atributos lidos e como eles viram `Usuario`, `Setor` e `Cargo`. Certificados e chaves ficam na raiz do projeto, fora do Git (acrescente-os ao `.gitignore`).

## Redis e Celery

O Redis (`redis:7-alpine`) funciona como broker e backend de resultados do Celery. O worker padrão consome a fila `celery`; há também um worker para a fila `rpa` (concorrência 1, sob o profile `celery`). O Celery Beat lê os agendamentos gravados pelo `django-celery-beat` no PostgreSQL principal.

Consulte [Celery e tarefas assíncronas](../operacao/celery-e-tarefas.md).

## E-mail

O Django usa SMTP com TLS (`EMAIL_USE_TLS = True`). As variáveis `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` e `EMAIL_FROM` (remetente padrão) alimentam o `EMAIL_BACKEND` SMTP. `EMAIL_PORT` é convertido com `int()` na inicialização — não deixe vazio.

Envie e-mails por tarefas Celery (nunca na requisição) e teste conectividade e autenticação SMTP antes de habilitar agendamentos.
