---
arquivo_id: "f4-12-1-90-integracao-p03-pratica"
parent_key: "12.1"
tipo_arquivo: "practice"
assuntos: ["01_hipoteses_planos_explain_medicao", "03_busca_textual_aproximada"]
ordem: 3
itens_origem: ["P3"]
---

### Atividade 3 — Compare busca por termos e busca aproximada
Implemente uma busca de artigos por termos usando `to_tsvector)/`websearch_to_tsquery) e uma busca de nomes de produtos com tolerância a pequenas diferenças usando `pg_trgm). Registre o que cada abordagem encontra e quais requisitos atende.

**Tarefas**
1. Escreva a consulta de busca textual para artigos em português.
2. Ative `pg_trgm) no banco de estudo, se tiver permissão, e proponha um índice GIN ou GiST para busca de similaridade.
3. Compare buscas por termos, substring e erro de digitação.
4. Discuta quando permanecer no PostgreSQL e quando investigar um serviço dedicado.
5. Declare pré-requisitos e limitações do ambiente.

**Dica:** `pg_trgm) é uma extensão e pode exigir permissão; confirme que o ambiente permite habilitá-la. Mantenha o mesmo conjunto de dados ao comparar.

