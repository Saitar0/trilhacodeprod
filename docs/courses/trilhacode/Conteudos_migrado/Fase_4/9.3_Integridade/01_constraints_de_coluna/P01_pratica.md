---
arquivo_id: "f4-9-3-01-constraints-de-coluna-p01-pratica"
parent_key: "9.3"
tipo_arquivo: "practice"
assunto: "01_constraints_de_coluna"
ordem: 1
itens_origem: ["P1"]
---

## Práticas

### Atividade 1 — Complete a proteção de uma tabela
Use a tabela Produto com id, sku, nome, preco e estoque. Regras: id identifica a linha; sku e nome são obrigatórios; sku não se repete; preço e estoque não podem ser negativos.

**Tarefas**
1. Escreva o DDL com PK, NOT NULL, UNIQUE e CHECK.
2. Indique se CHECK sozinho rejeitaria preco NULL.
3. Cite um INSERT válido e duas tentativas inválidas, indicando qual regra rejeita cada uma.

**Dica:** cada regra precisa de sua constraint; não deixe presença implícita no CHECK.

