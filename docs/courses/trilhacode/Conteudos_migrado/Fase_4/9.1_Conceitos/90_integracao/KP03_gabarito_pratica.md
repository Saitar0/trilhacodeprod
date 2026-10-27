---
arquivo_id: "f4-9-1-90-integracao-kp03-gabarito-pratica"
parent_key: "9.1"
tipo_arquivo: "answer_key_pratica"
assuntos: ["01_modelo_relacional_esquema_json", "02_chaves_primarias_identificacao", "03_chaves_estrangeiras_integridade_referencial", "04_cardinalidades_associacoes"]
ordem: 3
itens_origem: ["P3"]
---

**Solução de referência:** cliente(id, nome, email); pedido(id, cliente_id FK, data_pedido); produto(id, nome, preco_atual); item_pedido(pedido_id FK, produto_id FK, quantidade, preco_unitario_venda). Cliente–pedido é 1:N. Pedido–produto é N:N, representada por item_pedido e suas duas FKs. O preço no momento da compra fica no item_pedido para preservar o valor praticado mesmo que o preço atual do catálogo mude. Se só houver uma linha do mesmo produto por pedido, (pedido_id, produto_id) pode formar a PK composta; caso contrário, use uma chave que identifique cada linha e declare a regra. Email só deve ser único se essa for uma regra confirmada do domínio.

**Entregáveis:** diagrama ou lista de tabelas, campos, chaves, cardinalidades e hipóteses adotadas; uma justificativa para cada campo que foi movido para a tabela associativa.

