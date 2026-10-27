---
arquivo_id: "f9-41-1-90-integracao-r02-rubrica"
parent_key: "41.1"
tipo_arquivo: "rubric"
assuntos: ["01_fronteiras_orcamento_latencia", "02_timeout_retry_circuit_breaker"]
ordem: 2
itens_origem: ["P02"]
escala_rubrica: "0–2 por critério; cinco critérios; total 10; demais condições literais."
---


**Rubrica (0–2 cada, total 10):** orçamento não excede deadline; retries só para falhas elegíveis; limite/backoff/jitter explícitos; fallback preserva semântica; métricas permitem detectar saturação e breaker aberto. Aceite com pelo menos 8 pontos e nenhuma confirmação falsa de estoque.

**Erro comum:** configurar três tentativas de 500 ms para inventário sem contar o tempo de espera e o restante do fluxo.

