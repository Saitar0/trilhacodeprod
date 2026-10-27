---
arquivo_id: "f4-12-3-90-integracao-p02-pratica"
parent_key: "12.3"
tipo_arquivo: "practice"
assuntos: ["01_modelo_vendas_historico", "03_pagamentos_idempotencia"]
ordem: 2
itens_origem: ["P2"]
---

### Atividade 2 — Complete o esquema de itens e pagamento
Escreva DDL para ItemPedido e TentativaPagamento. Cada linha de item tem número único dentro do pedido, produto, quantidade positiva e preço não negativo. Cada tentativa pertence a um pedido e guarda provedor, chave de idempotência e estado. Um mesmo provedor não pode receber a mesma chave local repetida.

**Tarefas**
1. Defina PKs e FKs.
2. Escolha NOT NULL, CHECK e UNIQUE conforme as regras.
3. Explique por que o preço do catálogo não substitui o preço da linha.
4. Esclareça o limite da unicidade local em relação à idempotência do provedor.

**Dica:** identifique a tabela que representa a venda e a que representa cada tentativa externa.

