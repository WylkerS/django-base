# Celery e tarefas assíncronas

## Serviços assíncronos

Há quatro componentes Celery. Nos dois arquivos compose (completo e de desenvolvimento), `celery-worker` e `celery-beat` sobem sempre; `celery-worker-rpa` e `flower` ficam sob o profile `celery` (`--profile celery`):

| Serviço | Responsabilidade |
| --- | --- |
| `celery-worker` | tarefas da fila `celery` (padrão) |
| `celery-worker-rpa` | tarefas da fila `rpa`, com concorrência 1 (rotinas longas ou que não podem rodar em paralelo) |
| `celery-beat` | leitura e disparo dos agendamentos do banco |
| `flower` | monitoramento de workers e tarefas, porta `5555` |

O Redis atua como broker e backend de resultados (`CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`). O app Celery é `config` (`src/config/celery.py`), carregado em `src/config/__init__.py`, com `autodiscover_tasks()` — toda `tasks.py` de um app em `INSTALLED_APPS` é registrada.

Para mandar uma tarefa para a fila `rpa`, declare a rota nas settings:

```python
CELERY_TASK_ROUTES = {"apps.<app>.tasks.<tarefa>": {"queue": "rpa"}}
```

## Agendamentos

O projeto usa `django-celery-beat` com `CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"`. Os agendamentos ficam no PostgreSQL principal e são administrados pelo Django Admin (`/admin/django_celery_beat/`). As tarefas periódicas das quais o sistema depende são declaradas em `CELERY_BEAT_SCHEDULE` (`src/config/settings.py`, vazio no base, com exemplo comentado): ao subir, o `DatabaseScheduler` grava cada entrada no banco (cria ou atualiza pelo nome), e ela aparece no Admin como as demais. `CELERY_TIMEZONE` acompanha `America/Sao_Paulo`.

## Escrevendo uma tarefa

Modelo em `src/apps/core/tasks.py`:

```python
from celery import shared_task
from django.db import close_old_connections

from apps.<app> import services


@shared_task(name="apps.<app>.tasks.<tarefa>")
def tarefa(objeto_id):
    try:
        return services.<caso_de_uso>(objeto_id)
    finally:
        close_old_connections()
```

Regras:

- a task só orquestra: a regra de negócio fica em `services/`;
- passe IDs, nunca objetos do ORM, como argumentos;
- dispare a task no fim do service (preferencialmente com `transaction.on_commit`), nunca na view;
- dê `name` explícito para que o nome registrado no beat não dependa do caminho de import.

## Tarefas do base

| Task | Disparo | Função |
| --- | --- | --- |
| `apps.core.tasks.verificar_celery` | manual | diagnóstico: retorna `"ok"` se o worker executa tarefas |

```bash
# No host: dispara a tarefa de diagnóstico e espera o resultado
docker compose -f docker-compose.dev.yml exec django-web python -c "from apps.core.tasks import verificar_celery; print(verificar_celery.delay().get(timeout=10))"
```

<!-- PREENCHER: tabela das tarefas do projeto (task, disparo, função). -->

## Antes de ativar uma tarefa periódica

1. confirme que o worker da fila correspondente está ativo;
2. valide as conexões externas usadas pela rotina (SMTP, APIs);
3. configure SMTP e destinatários;
4. execute a tarefa manualmente em ambiente controlado;
5. só então habilite o agendamento (em `CELERY_BEAT_SCHEDULE` ou no Django Admin).

## Operação

```bash
# No host: estado dos workers
docker compose ps celery-worker celery-beat

# No host: logs da fila padrão
docker compose logs -f celery-worker

# No host: logs do agendador
docker compose logs -f celery-beat
```

Ao investigar uma falha, verifique a tarefa no Flower, os logs do worker correto, a conectividade SMTP e a configuração de e-mail.
