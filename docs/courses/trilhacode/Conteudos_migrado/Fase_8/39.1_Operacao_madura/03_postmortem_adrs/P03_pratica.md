---
arquivo_id: "f8-39-1-03-postmortem-adrs-p03-pratica-md"
parent_key: "39.1"
tipo_arquivo: "practice"
assunto: "03_postmortem_adrs"
ordem: 3
itens_origem: ["P03"]
---

### Atividade 3 — Produzir postmortem e ADR a partir do cenário
Use a linha do tempo fictícia: 10:00 publicação da versão 2.4; 10:04 aumento de 5xx; 10:08 alerta de erro recebido; 10:12 rollback iniciado; 10:16 erros voltam ao patamar anterior. Considere como evidências disponíveis: alteração recente de uma variável de configuração, runbook sem instrução para esse tipo de mudança e alerta sem indicação de rota afetada. Separe fatos de hipóteses. Escreva um resumo do incidente e três ações; depois registre um ADR sobre uma decisão de rollout ou validação de configuração.

**Entrega:** postmortem com impacto (identifique dados ainda desconhecidos), timeline, fatores contribuintes, aspectos que funcionaram e ações com responsável/prazo/critério de conclusão; ADR com contexto, alternativas, decisão e consequências.

**Critérios de aceite:** linguagem sem acusação individual; não inventa impacto ou causa não demonstrados; ações mitigam lacunas distintas (por exemplo, validação, alerta/runbook e prevenção) e têm evidência de conclusão; ADR não repete o postmortem.

**Feedback esperado:** “não sabemos” é melhor que afirmar impacto sem dado; uma ação concluída precisa de evidência e a eficácia deve ser revisada após a mudança.

