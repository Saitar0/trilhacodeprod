---
arquivo_id: "f9-41-1-90-integracao-r01-rubrica"
parent_key: "41.1"
tipo_arquivo: "rubric"
assuntos: ["01_fronteiras_orcamento_latencia", "02_timeout_retry_circuit_breaker"]
ordem: 1
itens_origem: ["P01"]
escala_rubrica: "0–2 por critério; cinco critérios; total 10; demais condições literais."
---


**Rubrica (0–2 cada, total 10):** diferencia requisitos imediatos e diferíveis; respeita deadline total; não afirma sucesso sem confirmação; define estado observável; compara custo/benefício dos dois fluxos. Aceite com pelo menos 8 pontos.

**Erro comum:** transformar qualquer chamada lenta em evento assíncrono sem definir como o usuário acompanha falha ou resultado.

