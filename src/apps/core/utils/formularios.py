def erros_por_campo(erro):
    """Converte um ValidationError de service em {campo: mensagem} para o template.

    Erros sem campo (ValidationError com mensagem simples) ficam em "geral".
    """
    if hasattr(erro, "error_dict"):
        return {campo: mensagens[0] for campo, mensagens in erro.message_dict.items()}
    return {"geral": erro.messages[0]}
