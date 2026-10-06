# Documentação

Índice da documentação técnica do projeto. Para convenções de desenvolvimento (pessoas e agentes de IA), ver [`AGENTS.md`](../AGENTS.md).

## Arquitetura

- [Visão geral](arquitetura/visao-geral.md) — componentes, apps Django, fluxo de requisição, estrutura do repositório.
- [Camadas de código](arquitetura/camadas-e-padroes-de-codigo.md) — regras de `models`, `services`, `selectors` e `views`.
- [Dados e integrações](arquitetura/dados-e-integracoes.md) — banco de dados, Redis/Celery, e-mail.

## Segurança

- [Autenticação e permissões](seguranca/autenticacao-e-permissoes.md) — `Usuario`, `Setor`/`Cargo`, papéis de gestor e usuário comum.

## Desenvolvimento

- [Fluxo local com Docker Compose](desenvolvimento/fluxo-local.md) — ambiente de desenvolvimento, comandos frequentes, como adicionar uma nova área.
- [Dependências Python com Poetry](desenvolvimento/dependencias-poetry.md).
- [Migrations versionadas](desenvolvimento/migrations.md).

## Configuração

- [Variáveis de ambiente](configuracao/variaveis-ambiente.md).

## Instalação

- [Docker](instalacao/docker.md).

## Operação

- [Celery e tarefas](operacao/celery-e-tarefas.md).

## Interface

- [Design System](design_system/README.md) — fonte visual do projeto.
- [Catálogo de componentes](exemplos_componentes/README.md) — um arquivo por componente, derivado do Design System.

## Módulos funcionais

- [Módulos](modulos/README.md) — documentação por área funcional, preenchida conforme cada app de domínio ganha views.
