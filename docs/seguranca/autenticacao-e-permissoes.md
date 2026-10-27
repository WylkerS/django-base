# Autenticação e permissões

## Autenticação

`AUTHENTICATION_BACKENDS` (`src/config/settings.py`) contém apenas o backend padrão do Django (`django.contrib.auth.backends.ModelBackend`): usuário e senha locais. A tela de login (`src/apps/core/views/auth.py::login_view`, rotas `login`/`logout` em `src/apps/core/urls.py`) autentica com `authenticate(username=<campo e-mail>, password=...)`; por isso, crie os usuários com `username` igual ao e-mail. O logout só aceita `POST`. O redirecionamento automático de usuários sem sessão usa `LOGIN_URL = "login"`.

Para autenticação institucional (LDAP, SSO), acrescente o backend antes do `ModelBackend` e documente-o aqui e em [Dados e integrações](../arquitetura/dados-e-integracoes.md#autenticação). O backend pode sincronizar `Setor`/`Cargo` a partir dos atributos do provedor; a flag `gestor_sistema` do setor continua manual.

## Usuário

O modelo autenticável é `core.Usuario` (`src/apps/core/models/usuario.py`), derivado de `AbstractUser` com `email` único, configurado em `AUTH_USER_MODEL`. Use `get_user_model()` em código executado e `settings.AUTH_USER_MODEL` em relações de models. Contas negadas por `@gestor_requerido` recebem a página `src/templates/403.html`.

## Modelos de autorização

- `Setor` — `nome` (único), `ativo` e `gestor_sistema` (booleano, `default=False`): marca se o setor faz parte da equipe gestora do sistema.
- `Cargo` — vincula um `user` a um `setor`, com `nivel` (`analista`, `gerente`, `direcao`) e `ativo`.

Restrição de integridade: `UniqueConstraint(fields=["user", "setor"], condition=Q(ativo=True), name="unique_cargo_ativo_por_setor")` — no máximo um cargo ativo por usuário e setor.

O acesso considera o **setor**, não o nível; o nível fica disponível para regras do projeto. Um cargo só concede acesso quando o próprio cargo **e** o setor estão ativos.

## Papéis do sistema (modelagem em banco, não hardcoded)

| Papel | Regra |
| --- | --- |
| Usuário comum | qualquer usuário autenticado |
| Gestor do sistema | cargo ativo num setor ativo com `gestor_sistema=True` |

Superusuários são sempre gestores, mesmo sem `Cargo` cadastrado.

A checagem é feita por `src/apps/core/selectors/permissoes.py::usuario_e_gestor(user)`, consultado pelo decorator `src/apps/core/decorators.py::gestor_requerido`. Não há lista de setores hardcoded: quem é a equipe gestora é definido marcando `gestor_sistema=True` no(s) `Setor`(es) corretos, via `/admin/`.

Se o projeto precisar de mais papéis, siga o mesmo desenho: um campo/relacionamento em dados, um selector `usuario_e_<papel>` e um decorator `<papel>_requerido`, com testes equivalentes aos de `src/tests/core/integration/` (os helpers `criar_gestor` e `criar_usuario_com_setor` de `src/tests/_apoio.py` ajudam a montar o cenário).

## Proteção das views

```python
from apps.core.decorators import gestor_requerido


@gestor_requerido
def painel(request):
    ...
```

Comportamento do decorador:

- sem autenticação: redirecionamento para o login (preservando `next`);
- autenticado sem papel de gestor: resposta 403 (`PermissionDenied`);
- autorizado: execução normal da view.

Views de usuário comum usam `@login_required` do Django. Quando o usuário só pode ver/alterar os próprios registros, garanta a posse em duas camadas: o selector filtra pelo dono (respondendo 404 para registros alheios) e o service revalida antes de alterar.

Aplique a mesma política a páginas, APIs, exportações e operações de alteração (`@require_POST`). Proteger apenas a página HTML deixa endpoints auxiliares expostos. A ocultação de um item de menu **não** é proteção de segurança — a variável de template `usuario_e_gestor` serve só para a navegação.

## Rotas públicas

`/` (rota `home`, `core.views.home_view`) é pública no base. Se o projeto mantiver a home pública, ela deve ser somente leitura e não expor dado sensível; caso contrário, proteja-a com `@login_required`. Documente aqui toda rota pública.

## Como conceder acesso manualmente

1. Entre em `/admin/` com um superusuário.
2. Cadastre o setor com um nome canônico (minúsculo). Marque `gestor_sistema` se esse setor deve gerenciar o sistema.
3. Crie um `Cargo` para o usuário, selecione o setor e o nível e mantenha o cargo ativo.
4. Confirme que o setor também está ativo.
