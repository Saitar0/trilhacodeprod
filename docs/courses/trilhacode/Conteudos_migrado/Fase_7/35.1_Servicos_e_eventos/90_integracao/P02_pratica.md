---
arquivo_id: "f7-35-1-90-integracao-p02-pratica-md"
parent_key: "35.1"
tipo_arquivo: "practice"
assuntos: ["02_filas_pubsub_event_routing", "03_confiabilidade_integracao_falhas"]
ordem: 2
itens_origem: ["P02"]
---

### Atividade 2 — Projete o fluxo com falhas e redrive

**Desafio:** desenhe API Gateway → Lambda produtora → SQS → Lambda consumidora e acrescente um assinante de evento por SNS ou EventBridge.

**Passos:**
1. Defina evento versionado, ids/correlação, quem publica e que papel pode chamar cada destino.
2. Trace cenário feliz e falhas: invocação da API, envio à fila, erro do consumidor, redelivery, falha do target e indisponibilidade prolongada.
3. Configure conceitualmente timeout/visibilidade, tamanho de lote, retry, DLQ, retenção e estratégia de redrive; explique que regras mudam por trigger.
4. Para lote SQS/Lambda, determine como evitar reprocessar itens já concluídos e como consumidor idempotente protege efeito de negócio.
5. Defina alarme para backlog/idade, falha de invocação e DLQ, além de procedimento seguro para inspecionar e reprocessar sem expor dados.

**Evidências:** diagrama; matriz de falhas e recuperação; policy IAM por chamada; configuração de retry/DLQ; lista de métricas/alarme/runbook.

**Verificação:** para cada confirmação, diga o que ela garante; confirme que mensagens podem duplicar e que evento não roteado ou target permanentemente indisponível não some sem observabilidade.

**Aceite:** falhas e garantias são específicas à integração; autorização é mínima; duplicatas não duplicam efeito; DLQ tem dono, alerta e processo de reprocessamento.

