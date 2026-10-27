# Camadas de código: models, services, selectors e views

## 1. Visão geral

O projeto é **Django puro** (views + templates, sem Django REST Framework nem serializers). Toda interação é via views que renderizam HTML ou, pontualmente, respondem JSON para chamadas AJAX.

Este documento adapta o [HackSoft Django Styleguide](https://github.com/HackSoftware/Django-Styleguide): separa `models` → `services`/`selectors` → `views`, trocando a camada `apis.py` (baseada em DRF) por views finas tradicionais do Django. Complementa a [Visão geral da arquitetura](visao-geral.md) e a [Autenticação e permissões](../seguranca/autenticacao-e-permissoes.md) (proteção de rotas).

Todo código novo já nasce seguindo este documento. Os exemplos abaixo usam um domínio fictício (`pedidos`) apenas para ilustrar.

## 2. Camadas e fluxo de dependência

```
views  →  services (escrita)  →  models
       →  selectors (leitura)  →
```

Regras:
- **Views** nunca acessam o ORM diretamente para aplicar regra de negócio. Podem fazer buscas triviais por PK para exibir uma página (`get_object_or_404`), mas qualquer filtro/regra composta vai para um selector.
- **Services** nunca lidam com `request`/`response`, nem renderizam template. Recebem dados já parseados pela view.
- **Selectors** nunca escrevem no banco (`save`, `update`, `delete`, `create`).
- **Models** não conhecem `services`/`selectors`/`views` (sem import de cima para baixo).

## 3. Models

Models devem ser **finos**: campos, `Meta`, `__str__` e, no máximo, properties/métodos triviais de apresentação. Regra de negócio não trivial (cálculo com múltiplas condições, efeitos colaterais, envio de notificação) vai para `services`.

Um arquivo por model, reexportado em `models/__init__.py`, como em [`src/apps/core/models/`](../../src/apps/core/models):

```python
# core/models/__init__.py
from .usuario import Usuario
from .setor import Setor
from .cargo import Cargo
```

## 4. Services — escrita e mutação

Services são **funções soltas** (não classes), uma função por caso de uso de negócio, nomeadas em português no padrão `verbo_substantivo`:

```python
# pedidos/services/pedidos.py
@transaction.atomic
def aprovar_pedido(pedido, usuario):
    if pedido.status != Pedido.Status.PENDENTE:
        raise ValidationError("Só pedidos pendentes podem ser aprovados.")
    pedido.status = Pedido.Status.APROVADO
    pedido.decidido_por = usuario
    pedido.decidido_em = timezone.now()
    pedido.save(update_fields=["status", "decidido_por", "decidido_em"])
    HistoricoPedido.objects.create(pedido=pedido, usuario=usuario, acao="APROVACAO")
    transaction.on_commit(lambda: enviar_email_aprovacao.delay(pedido.id))
```

Regras:
- Ficam em `<app>/services/`, um arquivo por domínio/subdomínio, reexportados em `services/__init__.py`.
- Usam `@transaction.atomic` sempre que a operação altera mais de um objeto ou precisa ser tudo-ou-nada.
- Validam entradas e levantam `django.core.exceptions.ValidationError` com mensagem clara (com dicionário `{campo: mensagem}` quando o erro é de um campo — ver `apps.core.utils.formularios.erros_por_campo`).
- **Não fazem leitura/consulta complexa** — isso é responsabilidade de um selector. Um service pode buscar um objeto pontual necessário para a operação, mas não monta querysets com múltiplos filtros/`annotate`.
- Uma função = um caso de uso. Evitar funções "canivete suíço" que fazem várias coisas dependendo de flags (preferir `aprovar_pedido` e `recusar_pedido` a um `decidir_pedido(aprovar: bool)`).
- Disparo de tarefas Celery fica no fim do service, depois do estado já estar consistente — nunca dentro da view.

## 5. Selectors — leitura

Consultas complexas (`.values()`, `.annotate()`, filtros compostos, `select_related`/`prefetch_related`) vão para `<app>/selectors/`, paralelo a `services/`.

Convenção de nomes: `buscar_`, `listar_`, `obter_` ou `contar_` + substantivo (predicados podem usar `existe_`/`usuario_e_`):

```python
# pedidos/selectors/pedidos.py
def listar_pedidos_do_painel(setor=None, status=None, data_inicio=None, data_fim=None):
    qs = Pedido.objects.select_related("solicitante", "setor")
    if setor is not None:
        qs = qs.filter(setor=setor)
    if status is not None:
        qs = qs.filter(status=status)
    if data_inicio is not None:
        qs = qs.filter(criado_em__date__gte=data_inicio)
    if data_fim is not None:
        qs = qs.filter(criado_em__date__lte=data_fim)
    return qs
```

Exemplo real: [`src/apps/core/selectors/permissoes.py`](../../src/apps/core/selectors/permissoes.py) (`usuario_e_gestor`).

Regras:
- Selectors retornam querysets (quando a view ainda vai paginar/filtrar mais) ou `list`/`values` já prontos para consumo.
- Concentram `select_related`/`prefetch_related`/`annotate` — a view e o service não devem montar isso inline.
- Não alteram estado.
- Views e services podem chamar selectors; selectors não chamam services.

## 6. Views

Views devem ser **finas**: parseiam o request, chamam **um** service ou selector e formatam a resposta (render de template ou redirect). São **funções** (sem Class-Based Views). Não devem conter:
- lógica de decisão de negócio;
- montagem de queryset com múltiplos filtros inline;
- lógica duplicada que já existe em um service, selector ou model.

```python
@gestor_requerido
@require_POST
def aprovar(request, pedido_id):
    pedido = get_object_or_404(Pedido, pk=pedido_id)
    try:
        aprovar_pedido(pedido=pedido, usuario=request.user)  # service
    except ValidationError as erro:
        messages.error(request, erro.messages[0])
    else:
        messages.success(request, "Pedido aprovado.")
    return redirect("pedidos:detalhe", pedido_id=pedido.pk)


@gestor_requerido
def painel(request):
    pedidos = listar_pedidos_do_painel(status=request.GET.get("status") or None)  # selector
    return render(request, "pedidos/painel.html", {"pedidos": pedidos})
```

A proteção de rota (`@gestor_requerido` / `@login_required`) é sempre da view — nunca depende de a navegação esconder ou não o link (ver [Autenticação e permissões](../seguranca/autenticacao-e-permissoes.md)).

### 6.1 Sem `forms.py`

O projeto **não usa `forms.py` nem `django.forms.Form`/`ModelForm`**. A view lê `request.POST`/`request.GET` diretamente e chama o service/selector ou, no caso de autenticação, as funções do próprio Django (`authenticate`, `login`, `logout`). Validação de negócio vai para `services`. O template recebe variáveis simples no contexto (valores e erros por campo) e renderiza `<input>` comuns com classes DaisyUI/Tailwind; o erro de cada campo usa o partial `partials/_erro_do_campo.html`.

Exemplo real ([`src/apps/core/views/auth.py`](../../src/apps/core/views/auth.py)):

```python
def login_view(request):
    erro = None
    email = ""
    proximo = request.POST.get("next") or request.GET.get("next", "")
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        senha = request.POST.get("password", "")
        user = authenticate(request, username=email, password=senha)
        if user is not None:
            auth_login(request, user)
            return redirect(proximo or "home")
        erro = "E-mail ou senha inválidos."
    return render(request, "core/login.html", {"erro": erro, "email": email, "proximo": proximo})
```

## 7. Exceptions

Use `django.core.exceptions.ValidationError` para erros de validação de negócio dentro de services. Não introduza uma camada de exceptions de domínio customizadas a menos que surja um caso concreto que `ValidationError` não resolva — evite abstração sem uso real.

## 8. Testes

- **Services e selectors**: testar isoladamente, sem cliente HTTP — chamar a função diretamente, montar o cenário com o ORM, verificar o resultado/estado final.
- **Views**: testar só o "encaixe" — permissão exigida (`@gestor_requerido`/`@login_required`), status code, redirect esperado, contexto básico do template. Não reteste a regra de negócio já coberta no teste do service.

Os testes ficam fora dos apps, em `src/tests/<app>/`, separados por camada; rode um app isolado com `make test TEST_TARGET=tests.<app>`:

```
src/tests/<app>/
    __init__.py
    unit/                          # regras puras, sem banco (SimpleTestCase)
        __init__.py
    integration/                   # ORM, services, selectors e views (TestCase)
        __init__.py
        test_services_<dominio>.py
        test_selectors_<dominio>.py
        test_views_<dominio>.py
    e2e/                           # live server e navegador real
        __init__.py
```

Detalhes de camadas, helpers (`tests._apoio`) e execução em [Testes automatizados](../desenvolvimento/testes.md).

## 9. Nomenclatura geral

- Identificadores de domínio (models, campos, funções de service/selector, nomes de rota) em **português**.
- Services e selectors: `verbo_substantivo` (ex. `aprovar_pedido`, `listar_pedidos_do_painel`).
- Rotas nomeadas com namespace por app (`app_name = "pedidos"` → `pedidos:painel`).

## 10. Checklist rápido para código novo

- [ ] A view só orquestra (parseia request → chama 1 service/selector → renderiza/redireciona)?
- [ ] Toda regra de negócio está em um `service`, não na view nem no model?
- [ ] Toda leitura com filtro/`annotate`/`select_related` composto está em um `selector`?
- [ ] O model continua fino?
- [ ] Se a operação altera mais de um objeto, o service usa `@transaction.atomic`?
- [ ] A view está protegida com `@gestor_requerido`/`@login_required` e, se for mutação, com `@require_POST`?
- [ ] Nomes seguem `verbo_substantivo` em português?
- [ ] Há testes de service/selector e de encaixe da view?
