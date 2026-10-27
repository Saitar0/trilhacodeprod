---
arquivo_id: "f9-46-2-07-rubrica-final"
parent_key: "46.2"
tipo_arquivo: "rubric"
ordem: 0
itens_origem: ["rubrica"]
escala_rubrica: "0–2 por critério; seis dimensões; total 12; limiares/bloqueadores literais."
---


## Verificação final e rubrica
A entrega final deve permitir que outra pessoa execute localmente, provoque os cenários de falha documentados e observe o comportamento sem depender de conhecimento oral do autor. Dê 0, 1 ou 2 pontos por critério:

| Critério | 0 — ausente | 1 — parcial | 2 — evidência suficiente |
|---|---|---|---|
| Contrato e boundary | evento/ownership indefinidos | definidos, mas ambíguos ou sem compatibilidade | contrato versionado, mínimo e ownership explícito |
| Publicação | perda ou sucesso sem confirmação | fluxo normal funciona, recuperação não demonstrada | outbox/alternativa explicada, recuperação e publisher confirm demonstrados |
| Consumo e idempotência | efeito pode duplicar ou ack antecipado | deduplicação existe sem prova de atomicidade/falha | commit/ack ordenados e redelivery não duplica efeito |
| Retry e DLQ | retry ilimitado ou falha desaparece | política parcial e triagem manual vaga | retry finito, DLQ diagnosticável e redrive auditável |
| Operação e observabilidade | sem instrução nem sinais | README ou sinais incompletos | execução e investigação reprodutíveis, fila/DLQ observáveis |
| Comparação de stack | opiniões genéricas | comparação com algum exemplo | trade-offs ligados a código, testes e execução observados |

**Interpretação:** 10–12 pontos, pronto para revisão final; 7–9, corrigir itens parciais antes de encerrar; 0–6, revisar entregas na ordem. Independentemente da soma, falha de perda silenciosa, duplicação de efeito ou segredo exposto bloqueia a conclusão até ser corrigida.

