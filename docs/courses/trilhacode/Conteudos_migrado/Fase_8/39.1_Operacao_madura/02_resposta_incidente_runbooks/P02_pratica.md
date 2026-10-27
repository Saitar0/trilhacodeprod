---
arquivo_id: "f8-39-1-02-resposta-incidente-runbooks-p02-pratica-md"
parent_key: "39.1"
tipo_arquivo: "practice"
assunto: "02_resposta_incidente_runbooks"
ordem: 2
itens_origem: ["P02"]
---

### Atividade 2 — Escrever e executar mentalmente um runbook
Cenário simulado: após uma publicação, a taxa de respostas 5xx cresce, uma parte dos usuários não conclui o checkout e o painel de latência também piora. Escreva um runbook curto que inclua confirmação do incidente, impacto, papéis de coordenação/operação/comunicação, consultas a usar, condições para rollback, riscos a verificar antes da reversão, validação da recuperação e escalonamento.

**Entrega:** passos numerados com decisão “se/então”, sinais a consultar, cuidados de segurança e mensagem de atualização para as partes afetadas.

**Critérios de aceite:** restauração e investigação aparecem como etapas distintas; nenhuma reversão é automática sem verificar compatibilidade/irreversibilidade; há responsável, gatilho de escalonamento e evidência de recuperação no SLI.

**Feedback esperado:** se o runbook só disser “fazer rollback”, especifique pré-condições e como saber se a mitigação funcionou; não declare resolvido apenas porque o deploy terminou.

