---
arquivo_id: "f9-42-1-03-drf-serializacao-views-acesso-p02-pratica"
parent_key: "42.1"
tipo_arquivo: "practice"
assunto: "03_drf_serializacao_views_acesso"
ordem: 2
itens_origem: ["P02"]
---


### Atividade 2 — Revise o isolamento entre usuários
**Contexto:** uma API tem `permission_classes = [IsAuthenticated]` e `queryset = Task.objects.all()`. Cada tarefa possui um campo `owner`. A listagem responde com tarefas de todas as contas.

**Instruções:** explique por que o login não resolve o vazamento; proponha um queryset limitado ao usuário atual; diga como a criação deve definir `owner`; descreva os casos a verificar ao abrir, alterar e excluir uma tarefa de outra pessoa. Use o guia de permissões do DRF como referência.

**Entrega:** revisão curta com falha, ajuste proposto e quatro casos de aceite: listar apenas próprias; criar sem poder forjar proprietário; acessar tarefa alheia; alterar/excluir tarefa alheia.

**Dica:** pense no conjunto retornado pela listagem separadamente da permissão geral de acesso à view. Para criação, não existe ainda um objeto recuperado do banco sobre o qual aplicar a verificação de objeto.

