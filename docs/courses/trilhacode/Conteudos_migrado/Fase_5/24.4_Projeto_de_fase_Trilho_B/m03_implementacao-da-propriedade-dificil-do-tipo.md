---
arquivo_id: "f5-24-4-m03-implementacao-da-propriedade-dificil-do-tipo"
parent_key: "24.4"
tipo_arquivo: "milestone"
ordem: 3
itens_origem: ["M3"]
titulo_marco: "Marco 3 — Implementação da propriedade difícil do tipo"
---

### Marco 3 — Implementação da propriedade difícil do tipo
**Objetivo:** implementar e demonstrar o comportamento que diferencia o tipo escolhido.

**Tarefas:** conclua a camada específica do tipo descrita na seção “Escopo mínimo por tipo”. Mantenha o teste junto à regra: concorrência/idempotência para T1; fronteira entre tenants para T2; eventos e reconexão para T3; paginação/filtros/contrato para T4; limites/estados/stream e falha para T5. Documente hipóteses e garantias que não são cobertas.

**Evidência:** teste automatizado ou cenário reproduzível com entrada, passos, saída esperada/obtida e logs sanitizados. Inclua ao menos um caso negativo ou de falha relevante ao tipo.

**Dica:** se o teste não falharia quando a regra fosse removida, ele ainda não prova o requisito. Introduza deliberadamente uma repetição, tenant diferente, desconexão, página-limite ou arquivo inválido e confirme que a evidência acusa o problema.

