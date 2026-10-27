---
arquivo_id: "f8-39-1-02-resposta-incidente-runbooks-01-teoria-md"
parent_key: "39.1"
tipo_arquivo: "theory"
assunto: "02_resposta_incidente_runbooks"
ordem: 2
itens_origem: ["### Microtópico 2 — Responder ao incidente: restaurar, coordenar e usar runbook"]
---

### Microtópico 2 — Responder ao incidente: restaurar, coordenar e usar runbook

Durante um incidente, primeiro reconheça o impacto, estabeleça coordenação e priorize mitigação segura. Em situações que envolvem mais pessoas ou equipes, papéis claros reduzem colisões: uma pessoa pode coordenar a resposta, outra executar mudanças técnicas e outra manter comunicação e registro. Em equipes pequenas, alguém pode acumular papéis, mas deve ficar claro quem está fazendo o quê e quando ocorre uma transferência de responsabilidade.

Um **runbook** é um guia operacional para sintomas ou tarefas recorrentes. Deve ajudar a responder: como confirmar o sintoma; quais painéis e consultas consultar; quais hipóteses são seguras de verificar; que ações podem mitigar; como validar a recuperação; quando interromper uma ação e escalar; e onde registrar os eventos. Procedimentos potencialmente destrutivos precisam de pré-condições, verificação de impacto e caminho de reversão. Um runbook não substitui julgamento nem autorização operacional.

Num incidente após deploy, uma reversão pode ser apropriada se o estado anterior for conhecido e a mudança puder ser revertida com segurança. Antes de agir, confira se houve migração de banco, mudança irreversível de formato ou dependência que torne rollback perigoso. Aplique uma mudança por vez, monitore o SLI afetado e preserve horário, sinais e decisões para análise posterior. Restaurar o serviço e entender a causa são trabalhos relacionados, mas distintos.

