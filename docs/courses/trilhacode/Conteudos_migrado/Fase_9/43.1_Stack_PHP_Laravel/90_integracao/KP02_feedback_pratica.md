---
arquivo_id: "f9-43-1-90-integracao-kp02-feedback-pratica"
parent_key: "43.1"
tipo_arquivo: "answer_key_pratica"
assuntos: ["02_ciclo_requisicao_laravel", "03_filas_decisao_stack"]
ordem: 2
itens_origem: ["P02"]
---


**Feedback de referência:** carregar relação de forma apropriada pode reduzir N+1; confirme por log/profiling de queries. Job deve usar identificador do recibo/pedido e registrar efeito idempotente ou consultar provedor antes de reenviar. Escopo/policy deve ser verificado para list, show e update/delete, não só para acesso sem login.

**Erro comum:** corrigir consultas sem medir ou supor que o backend de fila impede uma segunda entrega.

