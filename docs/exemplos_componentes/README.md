# Catálogo de componentes HTML

Este catálogo reúne os componentes visuais reutilizáveis do sistema, derivados do Design System em
[`docs/design_system/`](../design_system/README.md). Os arquivos aqui documentam **quando usar cada um,
as dependências, o HTML esperado e as classes correspondentes**, para que quem constrói uma tela nova
não precise reinventar o padrão.

Veja também a seção "Interface" do [`AGENTS.md`](../../AGENTS.md), que define as regras gerais do
front-end.

**Por que não há um arquivo CSS de componentes?** O projeto usa Tailwind CSS 4 + DaisyUI 5 pelo app
`theme`: cada componente é uma combinação de classes DaisyUI (`card`, `alert`, `input`, `btn`,
`navbar`...) e utilitários Tailwind aplicada direto no template, com as cores semânticas do tema.
O único CSS de origem é `src/apps/theme/static_src/src/styles.css`, que define os
[tokens do tema](tema-e-tokens.md). Por isso, nos arquivos desta pasta, a seção que em um projeto
com CSS próprio listaria as regras CSS se chama **Classes**: ela explica o papel de cada classe.

## Regra de uso

- **Antes de montar uma tela**, verifique se já existe um componente equivalente aqui e parta do
  HTML documentado.
- **Use cores semânticas** (`primary`, `secondary`, `accent`, `success`, `warning`, `error`,
  `info`, `base-*`) — nunca `blue-600`, hexadecimais ou `style="..."`.
- **Se precisar de um componente novo** (não coberto pelo DaisyUI nem pelos componentes abaixo),
  implemente-o com classes DaisyUI/Tailwind no template **e** documente-o nesta pasta, em um
  arquivo próprio criado a partir de [`_modelo-componente.md`](_modelo-componente.md), e
  acrescente-o à tabela abaixo.
- Se o mesmo trecho de HTML se repetir em várias telas, extraia-o para um partial
  (`src/templates/<app>/partials/_<nome>.html`, ou `src/templates/partials/_<nome>.html` quando
  servir a mais de um app) e documente o `{% include %}` no arquivo do componente. Partials do base:
  `partials/_erro_do_campo.html` (erro abaixo de um campo) e `partials/_paginacao.html`
  (rodapé de paginação).
- CSS personalizado só em último caso, em `src/apps/theme/static_src/src/styles.css`, e documentado no
  arquivo do componente.
- **Nunca use `style="..."`**, nem para valores calculados. Quando uma classe depende de um dado
  (ex.: `row-start-{{ item.linha }}`), o Tailwind não a encontra no código-fonte; declare o
  intervalo possível com `@source inline(...)` em `styles.css`.
- **Única exceção: templates de e-mail.** Clientes de e-mail não carregam o CSS do Tailwind nem
  entendem variáveis CSS; o modelo de e-mail usa estilo inline com os hexadecimais do tema.

## Componentes

A coluna **Em uso** indica em quais templates o componente já está implementado (caminhos relativos a
`src/templates/`). Componentes especificados a partir do Design System, mas ainda sem tela, ficam com
`—`.

| Grupo | Componente | Arquivo | Em uso |
|---|---|---|---|
| Fundamentos | Tema e tokens | [tema-e-tokens.md](tema-e-tokens.md) | `styles.css` |

<!-- PREENCHER: uma linha por componente, agrupados como no Design System (estrutura da página,
ações e formulários, retorno e status, navegação, dados e listas, e-mail...). -->

## Origem

<!-- PREENCHER: de onde vieram os componentes (páginas do Design System) e quais telas os usam. -->

O que é específico de uma única tela fica no próprio template e não entra no catálogo.
