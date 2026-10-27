---
arquivo_id: "f9-40-3-90-integracao-r02-rubrica"
parent_key: "40.3"
tipo_arquivo: "rubric"
assuntos: ["02_entrega_falhas_duplicatas", "03_ordem_escala_replay", "04_operacao_custo_decisao"]
ordem: 2
itens_origem: ["P02"]
escala_rubrica: "0–2 por critério; cinco critérios; total 10; demais condições literais."
---


**Rubrica (0–2 cada, total 10):** distingue estado do broker e do banco; identifica redelivery; propõe idempotência verificável; define retry/DLQ observável; descreve redrive sem repetir efeito. Aceite com 8 pontos e tratamento explícito de cada cenário.

**Erro comum:** confirmar antes de persistir o efeito ou reenviar DLQ sem deduplicação e sem registrar a causa corrigida.

