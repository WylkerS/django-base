# Módulos funcionais

Documentação por área funcional do sistema — um arquivo por app de domínio (`<app>.md`), criado a partir de [`_modelo.md`](_modelo.md) quando o app ganha `views`/`urls`. Ver os apps em [`docs/arquitetura/visao-geral.md`](../arquitetura/visao-geral.md#aplicações-django).

Papéis de acesso (gestor do sistema × usuário comum) estão documentados centralmente em [`docs/seguranca/autenticacao-e-permissoes.md`](../seguranca/autenticacao-e-permissoes.md) — cada módulo só registra qual decorator (`@gestor_requerido` ou `@login_required`) cada view usa, sem duplicar a regra.

Módulos implementados:

<!-- PREENCHER: - [`<app>`](<app>.md) — resumo (decorator principal). -->

Módulos previstos:

<!-- PREENCHER -->
