---
arquivo_id: "f4-9-2-90-integracao-kp03-gabarito-pratica"
parent_key: "9.2"
tipo_arquivo: "answer_key_pratica"
assuntos: ["01_regras_dominio_entidades_chaves", "02_cardinalidade_opcionalidade", "03_normalizacao_esquema_revisao"]
ordem: 3
itens_origem: ["P3"]
---

**Solução de referência:** Pedido(pedido_id PK, data_pedido, cliente_id FK); Cliente(cliente_id PK, nome_cliente); Produto(produto_id PK, nome_produto); ItemPedido(pedido_id FK, produto_id FK, quantidade, preco_unitario_vendido, PK(pedido_id, produto_id)). A linha é identificada pela combinação porque um pedido pode ter várias linhas e o produto pode reaparecer em outros pedidos. data_pedido depende de pedido_id; nome_cliente depende de cliente_id; nome_produto depende de produto_id. Mantê-los todos na relação da linha causa dependências parciais ou transitivas. Quantidade e preço vendido dependem da combinação pedido-produto. O preço vendido é um fato histórico da transação, não uma cópia acidental do preço atual. Se o domínio permitir o mesmo produto em várias linhas de um pedido, a chave precisa incluir um número da linha em vez de (pedido_id, produto_id).

