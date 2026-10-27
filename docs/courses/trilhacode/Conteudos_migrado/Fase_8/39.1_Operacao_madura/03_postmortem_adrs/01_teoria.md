---
arquivo_id: "f8-39-1-03-postmortem-adrs-01-teoria-md"
parent_key: "39.1"
tipo_arquivo: "theory"
assunto: "03_postmortem_adrs"
ordem: 3
itens_origem: ["### Microtópico 3 — Aprender com postmortem sem culpa", "### Microtópico 4 — Registrar decisões em ADR e fechar o ciclo"]
---

### Microtópico 3 — Aprender com postmortem sem culpa

Um **postmortem** registra o que aconteceu e transforma evidências em prevenção e melhoria. Uma estrutura útil inclui resumo, impacto e duração, detecção, linha do tempo, mitigação, fatores contribuintes, aspectos que funcionaram, lacunas de resposta e ações corretivas/preventivas.

Uma revisão **sem culpa** não omite responsabilidade nem ignora decisões. Ela evita explicar um incidente apenas como “alguém errou” e investiga quais informações, ferramentas, procedimentos, alertas, permissões, prazos e condições de trabalho moldaram as ações. Pessoas tomam decisões com o contexto disponível naquele momento; o processo procura tornar o sistema mais resiliente e a resposta mais clara na próxima vez.

Diferencie **fato, hipótese e conclusão**. Use timestamps, painéis, logs, traces, histórico de deploy e registros de comunicação como evidências. Se os dados não permitem confirmar uma hipótese, anote-a como pendente e proponha como verificá-la. Uma lista de ações útil tem responsável, prazo, prioridade, critério observável de conclusão e método para conferir se a ação reduziu o risco. “Melhorar monitoramento” é vaga até especificar o sinal ausente, quem o implementa e como será validado.

### Microtópico 4 — Registrar decisões em ADR e fechar o ciclo

Um **ADR** (*Architecture Decision Record*) documenta uma decisão técnica no contexto em que foi tomada. Um registro conciso pode conter título e estado, contexto/problema, decisão, alternativas consideradas e consequências — incluindo limitações e custos operacionais. ADR não é postmortem: postmortem aprende com um evento; ADR explica uma escolha arquitetural, que pode ter sido motivada por incidente ou por outro requisito.

Feche o ciclo ligando evidências e mudanças: o SLI identifica a dimensão afetada; o dashboard/trace ajuda a investigar; o runbook orienta uma mitigação; o postmortem captura o aprendizado; as ações entram no backlog com validação; e, quando uma escolha estrutural muda, um ADR registra o porquê. Revise runbooks e alertas depois de exercícios ou incidentes para remover passos obsoletos.

