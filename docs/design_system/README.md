# Design System

Fonte visual do projeto: cores, tipografia, raios, estados e as telas de referência. Cada sistema derivado do base tem o **seu** Design System; esta pasta só define onde ele fica e como ele chega ao código.

## O que colocar aqui

- o arquivo exportado do Design System (ex. `<Projeto> — Design System.html`, PDF ou link para o Figma);
- imagens de referência das telas, se houver.

## Como ele chega ao código

```text
docs/design_system/                    fonte visual (esta pasta)
        │
        ▼
src/apps/theme/static_src/src/styles.css   tokens → tema DaisyUI (@plugin "daisyui/theme") e fontes (@theme)
        │
        ▼
docs/exemplos_componentes/             um arquivo por componente: quando usar, HTML, classes
        │
        ▼
src/templates/                         telas e partials que usam os componentes
```

1. **Tokens.** Traduza as cores do Design System para as variáveis semânticas do DaisyUI (`--color-primary`, `--color-base-100`, `--color-success`...), os raios (`--radius-*`) e as fontes (`--font-sans`, `--font-mono`) em `styles.css`. Dê ao tema o nome do projeto e atualize o `data-theme` em `src/templates/base.html`. Documente a correspondência em [`../exemplos_componentes/tema-e-tokens.md`](../exemplos_componentes/tema-e-tokens.md).
2. **Fontes.** Se usar fontes web, carregue-as no bloco `fontes` do `base.html` (ex. `<link>` do Google Fonts).
3. **Layout.** Ajuste `base.html` (cabeçalho, navegação, rodapé), `core/login.html` e `403.html` ao Design System.
4. **Componentes.** Para cada componente do Design System, crie o arquivo correspondente em [`../exemplos_componentes/`](../exemplos_componentes/README.md) a partir de `_modelo-componente.md`, antes ou junto da primeira tela que o usa.
