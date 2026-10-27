---
arquivo_id: "f4-12-3-90-integracao-kp01-gabarito-pratica"
parent_key: "12.3"
tipo_arquivo: "answer_key_pratica"
assuntos: ["01_modelo_vendas_historico", "02_invariantes_constraints_transacoes"]
ordem: 1
itens_origem: ["P1"]
---

**Solução de referência:** Cliente 1 para 0..N Pedidos; cada Pedido tem um Cliente. Pedido rascunho pode ter 0 itens, mas a transição para confirmado exige pelo menos um; cada Item pertence a um Pedido. Cada Item aponta para uma Variante/Produto e pode existir uma linha para cada personalização; use (pedido_id, numero_linha) ou item_id como chave. Pedido tem 0..N TentativasPagamento; cada tentativa pertence a um pedido. Preço acordado e quantidade, além de SKU/descrição vendidos se necessários para recibos, são registrados como fatos históricos.

