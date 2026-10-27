---
arquivo_id: "f8-39-2-05-teoria-simular-falha-fazer-rollback-e-aprender-md"
parent_key: "39.2"
tipo_arquivo: "theory"
ordem: 4
itens_origem: ["MT04"]
---


### Microtópico 4 — Simular falha, fazer rollback e aprender

Planeje um exercício de *game day* de baixo risco em teste/staging: por exemplo, publicar uma configuração inválida, criar uma lentidão limitada em endpoint de teste ou interromper uma dependência não crítica. Defina antes o alvo, limite, condição de parada, observador e procedimento de recuperação. Não injete falha em produção. Se uma falha for insegura ou difícil de reverter, use uma timeline/dados sintéticos e execute o tabletop sem alterar serviços.

Durante o exercício, registre quando a mudança foi aplicada, quando o sinal apareceu, quem coordenou e executou, como o impacto foi avaliado, qual mitigação foi adotada e como a recuperação foi confirmada no SLI. Se ocorrer rollback, confira migrations, estado, eventos, dependências e plano de infraestrutura antes de restaurar uma versão. Preserve a evidência necessária para entender o evento.

Feche com postmortem: fatos separados de hipóteses; impacto conhecido e desconhecido; timeline; fatores contribuintes; resposta; o que funcionou; lacunas; ações com responsável, prazo e evidência de conclusão/eficácia. Registre em ADR decisões arquiteturais que mudaram e as consequências/alternativas relevantes; não transforme o ADR em cópia do postmortem.

**Entrega 4 — Exercício, rollback e aprendizado.** Execute a simulação segura ou tabletop, produza relatório de evidências e postmortem, atualize runbook/alerta quando necessário e registre um ADR se houve decisão arquitetural relevante.

**Critérios de aceite:** escopo e condição de parada foram definidos antes; exercício não atinge produção nem dado real; resposta usa sinais existentes; recuperação é comprovada; postmortem não atribui a causa a uma pessoa; ações têm responsável, prazo e verificação.

