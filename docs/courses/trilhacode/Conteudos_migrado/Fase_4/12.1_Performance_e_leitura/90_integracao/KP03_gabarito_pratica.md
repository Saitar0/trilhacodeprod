---
arquivo_id: "f4-12-1-90-integracao-kp03-gabarito-pratica"
parent_key: "12.1"
tipo_arquivo: "answer_key_pratica"
assuntos: ["01_hipoteses_planos_explain_medicao", "03_busca_textual_aproximada"]
ordem: 3
itens_origem: ["P3"]
---

**Solução de referência:** para artigos, use `to_tsvector('portuguese', texto) @@ websearch_to_tsquery('portuguese', termos)); para nomes aproximados, habilite a extensão e use operador/índice documentados para `pg_trgm), por exemplo GIN com `gin_trgm_ops). Busca textual atende recuperação de termos e normalização; trigramas apoiam semelhança parcial/aproximada. Uma busca por substring com curinga inicial não é automaticamente rápida sem índice compatível. Serviço dedicado só se justifica por requisitos medidos de recursos, escala ou relevância, considerando sincronização adicional.

