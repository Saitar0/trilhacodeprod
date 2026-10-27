---
arquivo_id: "f4-12-3-90-integracao-kp02-gabarito-pratica"
parent_key: "12.3"
tipo_arquivo: "answer_key_pratica"
assuntos: ["01_modelo_vendas_historico", "03_pagamentos_idempotencia"]
ordem: 2
itens_origem: ["P2"]
---

**Solução de referência:**
```sql
CREATE TABLE item_pedido (
  pedido_id bigint NOT NULL REFERENCES pedido(id),
  numero_linha integer NOT NULL CHECK (numero_linha > 0),
  produto_id bigint NOT NULL REFERENCES produto(id),
  quantidade integer NOT NULL CHECK (quantidade > 0),
  preco_unitario numeric(12,2) NOT NULL CHECK (preco_unitario >= 0),
  PRIMARY KEY (pedido_id, numero_linha)
);

CREATE TABLE tentativa_pagamento (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  pedido_id bigint NOT NULL REFERENCES pedido(id),
  provedor text NOT NULL,
  chave_idempotencia text NOT NULL,
  estado text NOT NULL,
  UNIQUE (provedor, chave_idempotencia)
);
```
O preço da linha preserva o preço contratado. A unicidade local impede reutilizar a mesma chave para o provedor registrado no sistema, mas a integração também deve seguir a semântica, escopo e janela de retenção do provedor, além de reconciliar respostas incertas.

