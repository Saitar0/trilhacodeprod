---
arquivo_id: "f4-9-3-01-constraints-de-coluna-kp01-gabarito-pratica"
parent_key: "9.3"
tipo_arquivo: "answer_key_pratica"
assunto: "01_constraints_de_coluna"
ordem: 1
itens_origem: ["P1"]
---

**Solução de referência:**
```sql
CREATE TABLE produto (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  sku text NOT NULL UNIQUE,
  nome text NOT NULL,
  preco numeric(10,2) NOT NULL CHECK (preco >= 0),
  estoque integer NOT NULL CHECK (estoque >= 0)
);
```
Um produto com SKU distinto, nome preenchido, preço 10.00 e estoque 0 é válido. Preço -1 viola CHECK; SKU já existente viola UNIQUE. NULL em preço viola NOT NULL.

