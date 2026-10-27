---
arquivo_id: "f8-39-2-07-rubrica-final-md"
parent_key: "39.2"
tipo_arquivo: "rubric"
ordem: 0
itens_origem: ["6 dimensões"]
escala_rubrica: "0–2 por dimensão; 6 dimensões; total 12; aceite ≥10/12, com bloqueadores literais da fonte"
---


## Rubrica final

Avalie cada dimensão de 0 a 2: **0 — ausente ou sem evidência; 1 — parcial, pouco reproduzível ou com lacunas; 2 — completo, reproduzível e coerente com o projeto**.

| Dimensão | O que comprova nível 2 |
|---|---|
| Deploy e recuperação | pipeline/gates, plano revisado, health check e rollback com limites documentados. |
| Requisito do tipo | sinal e teste específicos de T1–T5 atendem ao critério do guia. |
| Instrumentação | métricas/traces/logs são úteis, correlacionáveis e sem dados sensíveis/cardinalidade indevida. |
| Painel e runbook | pergunta operacional, alerta, sequência de investigação e validação estão claros. |
| Exercício e aprendizado | simulação segura tem evidências, postmortem sistêmico e ações verificáveis. |
| Reprodução e higiene | README, configuração por ambiente, teste, proteção de segredos e limpeza são suficientes para outra pessoa repetir. |

**Aceite:** pelo menos **10 de 12 pontos**, sem nota 0 em deploy/recuperação, requisito do tipo ou proteção/higiene de dados. Uma nota 1 exige registrar a lacuna e a próxima ação antes de apresentar o projeto como concluído.

