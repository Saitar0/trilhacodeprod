---
arquivo_id: "f5-18-1-90-integracao-kp01-gabarito-pratica-compartilhado"
parent_key: "18.1"
tipo_arquivo: "answer_key_pratica"
assuntos: ["01_recursos_e_semantica_http", "04_status_e_erros_http"]
ordem: 1
itens_origem: ["P1"]
---

**Solução de referência:** GET /tarefas e GET /tarefas/{id} leem; POST /tarefas cria e retorna 201; PUT /tarefas/{id} substitui; PATCH /tarefas/{id} altera parcialmente; DELETE /tarefas/{id} remove e pode retornar 204. Filtro por estado entra na query da listagem. Respostas de ausência, entrada inválida, falta de autenticação/permissão e conflito são escolhidas conforme o cenário e documentadas. GET é seguro; GET, PUT e DELETE são idempotentes; POST não é por padrão.

