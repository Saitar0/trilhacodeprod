---
arquivo_id: "f4-11-1-90-integracao-p03-pratica"
parent_key: "11.1"
tipo_arquivo: "practice"
assuntos: ["03_null_logica_trivalente", "04_ordenacao_limite_previsibilidade"]
ordem: 3
itens_origem: ["P3"]
---

### Atividade 3 — Encontre os dez maiores pedidos
Escreva uma consulta que retorne id, criado_em e total dos dez pedidos de maior total. Em caso de empate, o maior id vem primeiro. Exclua pedidos cujo total seja NULL.

**Tarefas**
1. Defina as colunas projetadas e o filtro.
2. Ordene pelo critério principal e pela chave de desempate.
3. Aplique LIMIT após a ordenação.
4. Explique o que mudaria se ORDER BY fosse removido.

**Dica:** uma ordem em duas colunas define como resolver empates.

