---
arquivo_id: "f9-42-1-03-drf-serializacao-views-acesso-kp02-feedback-pratica"
parent_key: "42.1"
tipo_arquivo: "answer_key_pratica"
assunto: "03_drf_serializacao_views_acesso"
ordem: 2
itens_origem: ["P02"]
---


**Feedback de referência:** `get_queryset()` pode limitar por `request.user`; atribua o owner no servidor (por exemplo, em `perform_create`) conforme o desenho. Verificações de objeto aplicadas ao detalhe não filtram automaticamente listagens; um usuário sem autenticação e um usuário autenticado sem acesso podem resultar em respostas diferentes conforme o mecanismo configurado.

**Erro comum:** testar somente que uma requisição sem token falha e concluir que o isolamento entre contas está garantido.

