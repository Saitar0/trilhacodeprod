---
arquivo_id: "f9-40-1-90-integracao-kp03-feedback-pratica"
parent_key: "40.1"
tipo_arquivo: "answer_key_pratica"
assuntos: ["02_confirmacoes_ack_idempotencia", "04_dead_letter_recuperacao"]
ordem: 3
itens_origem: ["P03"]
---


**Feedback esperado:** “tem DLQ” não prova que a mensagem chega lá em todas as falhas. Verifique destination, queue type, política de dead-letter e comportamento se o destino estiver indisponível.

