---
arquivo_id: "f9-41-1-90-integracao-r03-rubrica"
parent_key: "41.1"
tipo_arquivo: "rubric"
assuntos: ["03_consistencia_saga_compensacao", "04_outbox_entrega_operacao"]
ordem: 3
itens_origem: ["P03"]
escala_rubrica: "0–2 por critério; cinco critérios; total 10; demais condições literais."
---


**Rubrica (0–2 cada, total 10):** cobre as três falhas; estado de saga durável; compensação e falha da compensação explícitas; idempotência e redelivery tratados; monitoramento e reconciliação executáveis. Aceite com pelo menos 8 pontos e sem assumir publicação exatamente uma vez.

**Erro comum:** marcar o pedido como cancelado antes de confirmar o estorno/liberação ou remover o evento pendente para “limpar” a fila.

