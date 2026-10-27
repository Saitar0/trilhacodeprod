---
arquivo_id: "f4-9-1-90-integracao-p03-pratica"
parent_key: "9.1"
tipo_arquivo: "practice"
assuntos: ["01_modelo_relacional_esquema_json", "02_chaves_primarias_identificacao", "03_chaves_estrangeiras_integridade_referencial", "04_cardinalidades_associacoes"]
ordem: 3
itens_origem: ["P3"]
---

### 3. Integrada — normalize o esboço de pedidos
Uma planilha repete cliente e produto em cada linha: id_pedido, nome_cliente, email_cliente, data_pedido, nome_produto, quantidade e preco_unitario. Modele tabelas para cliente, pedido, produto e itens do pedido. Identifique PK/FK, cardinalidades e indique onde manteria o preço praticado naquela venda. Declare qualquer hipótese sobre repetição de produto dentro de um mesmo pedido.

**Dica:** um cliente pode ter vários pedidos; um pedido pode conter vários produtos e um produto pode aparecer em pedidos diferentes. Os dados do vínculo pedido-produto podem descrever a linha vendida.

