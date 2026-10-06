from celery import shared_task
from django.db import close_old_connections


@shared_task(name="apps.core.tasks.verificar_celery")
def verificar_celery():
    """Tarefa de exemplo/diagnóstico: confirma que o worker executa tarefas.

    Modelo para as tarefas do projeto: a task só orquestra, chama a regra de negócio
    em `services/` e fecha as conexões de banco ao terminar.
    """
    try:
        return "ok"
    finally:
        close_old_connections()
