# Módulo `<app>`

> Modelo: copie para `docs/modulos/<app>.md`, preencha e liste o módulo em [`README.md`](README.md).

## Objetivo

O que a área resolve e para quem.

## Modelos

| Model | Arquivo | Campos principais | Observações |
| --- | --- | --- | --- |
| `<Model>` | `src/apps/<app>/models/<model>.py` | ... | constraints, choices, relações |

## Rotas e permissões

| Rota (nome) | URL | View | Método | Acesso |
| --- | --- | --- | --- | --- |
| `<app>:lista` | `/<app>/` | `views.lista` | GET | `@login_required` |
| `<app>:criar` | `/<app>/novo/` | `views.criar` | GET/POST | `@gestor_requerido` |

## Regras de negócio

Services (`src/apps/<app>/services/`) e o que cada um valida; selectors (`src/apps/<app>/selectors/`) e o que retornam.

## Tarefas assíncronas

Tasks em `src/apps/<app>/tasks.py`, disparo (service ou beat) e fila.

## Templates

Telas em `src/templates/<app>/` e os componentes do catálogo que usam.

## Testes

Arquivos em `src/tests/<app>/{unit,integration,e2e}/` e o que cobrem.
