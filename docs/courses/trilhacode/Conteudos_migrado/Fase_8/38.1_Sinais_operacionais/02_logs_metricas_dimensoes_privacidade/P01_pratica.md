---
arquivo_id: "f8-38-1-02-logs-metricas-dimensoes-privacidade-p01-pratica-md"
parent_key: "38.1"
tipo_arquivo: "practice"
assunto: "02_logs_metricas_dimensoes_privacidade"
ordem: 1
itens_origem: ["P01"]
---

### Atividade 1 — Normalizar logs para investigação
Transforme três registros de texto fictícios em um esquema estruturado consistente para uma API: uma resposta 200, uma resposta 500 e uma chamada com timeout. Inclua timestamp, severity, `service.name`, ambiente, rota normalizada, status, duração e trace ID quando disponível. Remova token, corpo da requisição, email e outros dados desnecessários.

**Entrega:** os três registros normalizados, uma breve definição dos campos e a lista de dados removidos/mascarados.

**Critérios de aceite:** todos os registros usam os mesmos campos e tipos; rota não contém IDs variáveis; o erro é pesquisável sem expor segredo ou payload; a ausência de trace ID não é inventada.

**Feedback esperado:** campos inconsistentes ou valores pessoais devem ser removidos ou justificados; log em JSON com chaves variáveis não é um esquema estável.

