---
arquivo_id: "f5-18-2-03-idempotencia-em-retries-03-gabarito-quiz"
parent_key: "18.2"
tipo_arquivo: "answer_key"
assunto: "03_idempotencia_em_retries"
ordem: 3
itens_origem: ["Q5"]
---

**Resposta:** não. O banco local e o serviço externo não participam automaticamente de uma única transação.  
   **Feedback:** coordene a operação com a dependência, use idempotência no provedor ou um fluxo durável; a chave local sozinha não elimina toda janela de falha.

