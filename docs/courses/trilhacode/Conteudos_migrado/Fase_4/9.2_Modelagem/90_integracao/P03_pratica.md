---
arquivo_id: "f4-9-2-90-integracao-p03-pratica"
parent_key: "9.2"
tipo_arquivo: "practice"
assuntos: ["01_regras_dominio_entidades_chaves", "02_cardinalidade_opcionalidade", "03_normalizacao_esquema_revisao"]
ordem: 3
itens_origem: ["P3"]
---

### Atividade 3 — Normalização de pedidos
Considere a relação `LinhaPedido(pedido_id, data_pedido, cliente_id, nome_cliente, produto_id, nome_produto, quantidade, preco_unitario_vendido)`. Cada pedido pertence a um cliente; cada linha de pedido contém um produto; um produto pode aparecer em vários pedidos. A chave candidata da linha é (pedido_id, produto_id). `preco_unitario_vendido` registra o preço acordado naquela compra e deve preservar o histórico, mesmo se o preço atual do produto mudar.

**Tarefas**
1. Explique por que `pedido_id` sozinho não identifica uma linha.
2. Aponte dependências que indicam violação de 2FN ou 3FN.
3. Proponha relações normalizadas com PK e FK.
4. Justifique por que `preco_unitario_vendido` permanece na linha do pedido.

**Dica:** diferencie o preço atual do catálogo do preço histórico acordado; declare a chave antes de avaliar dependências.

