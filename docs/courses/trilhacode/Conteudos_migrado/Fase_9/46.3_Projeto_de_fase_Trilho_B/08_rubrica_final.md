---
arquivo_id: "f9-46-3-08-rubrica-final"
parent_key: "46.3"
tipo_arquivo: "rubric"
ordem: 0
itens_origem: ["rubrica"]
escala_rubrica: "0–2 por critério; seis dimensões; total 12; limiares/bloqueadores literais."
---


## Rubrica final
Atribua 0, 1 ou 2 por critério. Os critérios específicos do tipo escolhido também precisam passar; a soma não substitui o teste central.

| Critério | 0 — ausente | 1 — parcial | 2 — evidência suficiente |
|---|---|---|---|
| Rotação e hipótese | escolha não segue cobertura ou não há problema definido | escolha registrada, motivo pouco verificável | opções/cobertura registradas e cenário técnico claro |
| Base e execução | ambiente não inicia ou fluxo não é reproduzível | execução depende de passos não documentados | Compose, migrations e fluxo local reproduzíveis |
| Contrato e segurança | identidade, ownership ou auth ausentes | definidos parcialmente ou sem teste | contrato versionado, mínimo, autenticação/autorização demonstradas |
| Resiliência | efeito se perde/duplica, retry infinito ou sem DLQ | mecanismos existem sem cenários de falha completos | redelivery idempotente, retry limitado, DLQ e redrive evidenciados |
| Regra central do tipo | cenário técnico específico ausente | cenário executado sem evidência convincente | regra do tipo demonstrada pelo cenário da tabela |
| ADR e documentação | decisão e execução não explicadas | há documentos, mas faltam trade-offs ou limites | README/ADR reproduzíveis, alternativas e limites explícitos |

**Interpretação:** 10–12 pontos e todos os critérios de segurança, resiliência e tipo específico em nível 2: pronto para aceite; 7–9 pontos: corrigir itens parciais; 0–6: revisar entregas. Exposição de segredo, acesso entre tenants, perda silenciosa ou duplicação de efeito bloqueia a conclusão até ser corrigida.

