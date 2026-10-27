---
arquivo_id: "f4-12-3-01-resumo"
parent_key: "12.3"
tipo_arquivo: "resumo"
ordem: 0
itens_origem: ["Resumo"]
---

## Resumo
- Derive entidades e cardinalidades de regras e estados explícitos.
- ItemPedido preserva fatos históricos da venda; chave depende da política de linhas repetidas.
- Constraints protegem invariantes declarativas; operações coordenadas exigem transações.
- Pagamento externo precisa de idempotência e reconciliação; transação SQL não desfaz efeitos no provedor.
- Agregue cada fato no nível correto para não inflar receita em joins.

