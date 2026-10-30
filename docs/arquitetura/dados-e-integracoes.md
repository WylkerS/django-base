# Bancos de dados e integrações

## Banco de dados

O arquivo `src/config/settings.py` define um único alias de banco.

| Alias | Tecnologia | Finalidade |
| --- | --- | --- |
| `default` | PostgreSQL 17 | todos os modelos Django: usuários, setores, cargos, agendamentos do Celery Beat e os modelos de domínio |

<!-- PREENCHER: se o projeto consumir bases externas (SQL Server, APIs), acrescente aliases/integrações aqui e em settings.py. -->

O PostgreSQL é **externo**: nenhum arquivo Compose sobe um serviço de banco. Desenvolvimento, implantação e suíte apontam para o servidor configurado pelas variáveis `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST` e `POSTGRES_PORT`, que configuram o alias `default`. `POSTGRES_HOST` é um PostgreSQL externo (hostname ou IP do servidor; `host.docker.internal` para um PostgreSQL instalado no próprio host) — nunca `localhost`, que dentro do container é o próprio container. Os serviços Django recebem `extra_hosts: host.docker.internal:host-gateway`, para que esse nome funcione também no Linux.

Backup, retenção e criação do banco e do usuário ficam a cargo de quem administra o servidor PostgreSQL. Projetos derivados do base usam bancos (`POSTGRES_DB`) distintos.

O `docker-compose.test.yml` também não sobe banco: a suíte cria `test_<POSTGRES_DB>` no mesmo servidor, aplica as migrations e o remove ao final (o usuário precisa de `CREATEDB`); o Makefile remove o container e a rede mesmo quando a execução falha ou é interrompida.

## Autenticação

O base usa apenas o `ModelBackend` do Django. Para integrar um provedor institucional (LDAP, SSO), crie o backend em `src/config/` ou em `src/apps/core/`, acrescente-o em `AUTHENTICATION_BACKENDS` antes do `ModelBackend` e documente aqui: servidor, atributos lidos e como eles viram `Usuario`, `Setor` e `Cargo`. Certificados e chaves ficam na raiz do projeto, fora do Git (acrescente-os ao `.gitignore`).

## Redis e Celery

O Redis (`redis:7-alpine`) funciona como broker e backend de resultados do Celery. O worker padrão consome a fila `celery`; há também um worker para a fila `rpa` (concorrência 1, sob o profile `celery`). O Celery Beat lê os agendamentos gravados pelo `django-celery-beat` no PostgreSQL principal.

Consulte [Celery e tarefas assíncronas](../operacao/celery-e-tarefas.md).

## E-mail

O Django usa SMTP com TLS (`EMAIL_USE_TLS = True`). As variáveis `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` e `EMAIL_FROM` (remetente padrão) alimentam o `EMAIL_BACKEND` SMTP. `EMAIL_PORT` é convertido com `int()` na inicialização — não deixe vazio.

Envie e-mails por tarefas Celery (nunca na requisição) e teste conectividade e autenticação SMTP antes de habilitar agendamentos.
