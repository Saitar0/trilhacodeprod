---
arquivo_id: "f9-40-1-90-integracao-kp02-feedback-pratica"
parent_key: "40.1"
tipo_arquivo: "answer_key_pratica"
assuntos: ["01_exchange_binding_filas_consumers", "02_confirmacoes_ack_idempotencia", "03_prefetch_trabalho_em_voo"]
ordem: 2
itens_origem: ["P02"]
---


**Feedback esperado:** ack antecipado pode perder trabalho; ack posterior a gravação abre janela de duplicação. A resposta é idempotência e tratamento correto do protocolo, não escolher um momento de ack que elimine toda falha distribuída.

