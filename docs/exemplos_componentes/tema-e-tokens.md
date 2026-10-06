# Tema e tokens

## Quando usar

Referência de todas as cores, raios e fontes do sistema. Todo componente usa estes tokens por meio das
classes semânticas do DaisyUI/Tailwind (`bg-primary`, `text-base-content`, `rounded-box`...).

## Onde ficam

`src/apps/theme/static_src/src/styles.css`:

- `@plugin "daisyui/theme" { ... }` — tema DaisyUI (nome, cores, raios, borda);
- `@theme { ... }` — fontes (`--font-sans`, `--font-mono`) e outros tokens do Tailwind.

O tema ativo é o do atributo `data-theme` em `src/templates/base.html`.

> **Estado no projeto base:** o tema `base` tem valores **provisórios**. Ao aplicar o Design System do
> projeto, substitua os valores, renomeie o tema (e o `data-theme`) e preencha as tabelas abaixo.

## Cores

| Token DaisyUI | Classe | Valor | Uso no Design System |
|---|---|---|---|
| `--color-base-100` | `bg-base-100` | | superfícies (cards, inputs) |
| `--color-base-200` | `bg-base-200` | | fundo da página |
| `--color-base-300` | `border-base-300` | | bordas |
| `--color-base-content` | `text-base-content` | | texto principal |
| `--color-primary` | `btn-primary`, `text-primary` | | ação principal |
| `--color-secondary` | `bg-secondary` | | cabeçalho |
| `--color-accent` | `bg-accent` | | destaques suaves |
| `--color-info` | `alert-info` | | informação |
| `--color-success` | `alert-success` | | sucesso |
| `--color-warning` | `alert-warning` | | atenção |
| `--color-error` | `alert-error` | | erro |

## Raios e borda

| Token | Classe | Valor | Uso |
|---|---|---|---|
| `--radius-box` | `rounded-box` | | cards, modais |
| `--radius-field` | `rounded-field` | | botões, inputs |
| `--radius-selector` | `rounded-selector` | | checkboxes, badges |
| `--border` | — | | espessura das bordas dos componentes |

## Tipografia

| Token | Classe | Fonte | Uso |
|---|---|---|---|
| `--font-sans` | `font-sans` | | texto geral |
| `--font-mono` | `font-mono` | | números, datas, códigos |
