---
arquivo_id: "f8-39-2-04-teoria-construir-dashboard-regra-de-alerta-e-runbook-md"
parent_key: "39.2"
tipo_arquivo: "theory"
ordem: 3
itens_origem: ["MT03"]
---


### Microtópico 3 — Construir dashboard, regra de alerta e runbook

O dashboard deve refletir a pergunta “a pessoa consegue completar o fluxo?” e o sinal específico do projeto. Inclua uma visão de tráfego/execuções, erros, distribuição de duração e saturação ou capacidade apropriada; acrescente o painel especializado da tabela anterior. Rotas devem ser normalizadas; agregações e janelas devem ser explícitas. Para distribuições, prefira histogramas que permitam agregação compatível e identifique quantis como estimativas quando aplicável.

Adicione uma regra de alerta com condição, janela, limiar justificável, impacto ou SLI relacionado, destinatário e próximo passo. Um valor alto isolado sem impacto/ação tende a gerar ruído. O runbook vinculado precisa indicar como confirmar o alerta, quais consultas e traces examinar, como mitigar com segurança, como validar recuperação e quando escalar. Anote limites conhecidos: amostragem, atraso de coleta, falta de instrumentação ou impossibilidade de verificar determinada dependência.

**Entrega 3 — Observabilidade acionável.** Entregue dashboard, regra de alerta (pode ser descrita se a ferramenta local não suportar alerting) e runbook curto. Faça uma revisão em que outra pessoa consiga encontrar a rota/operação afetada a partir de um sintoma, sem instruções orais do autor.

**Critérios de aceite:** painéis têm título, unidade, período e agrupamento; cada alerta orienta uma ação; consultas não dependem de valores pessoais ou labels ilimitadas; runbook tem verificação, mitigação, validação e escalonamento; ao menos uma execução conecta o sintoma agregado a um trace/log relacionado.

