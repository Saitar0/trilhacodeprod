---
arquivo_id: "f7-35-1-03-confiabilidade-integracao-falhas-01-teoria-md"
parent_key: "35.1"
tipo_arquivo: "theory"
assunto: "03_confiabilidade_integracao_falhas"
ordem: 3
itens_origem: ["### Microtópico 3 — Confiabilidade da integração e fronteiras de falha"]
---

### Microtópico 3 — Confiabilidade da integração e fronteiras de falha

Cada ligação precisa de política explícita de permissões: API Gateway pode invocar uma função autorizada; uma função assume uma role mínima; produtores/consumidores recebem apenas ações e recursos necessários; serviços podem precisar de policies de recurso para aceitar a chamada. Separe a identidade da execução da função da permissão de invocação. TLS e IAM protegem ligações diferentes; não coloque dados sigilosos em logs ou eventos sem necessidade e controle de acesso.

Retries são específicos à integração. Por exemplo, uma Lambda acionada por SQS usa event source mapping que lê mensagens e pode invocar a função em lote; se a invocação falhar, mensagens do lote podem voltar, inclusive itens que tinham sido processados com sucesso. Resposta parcial de falha permite indicar somente itens falhos quando configurada e implementada corretamente. Isso é diferente de uma função Lambda invocada de forma assíncrona diretamente e diferente da política de retry de entrega do EventBridge. Estude o comportamento do trigger escolhido, não transfira uma regra de retry de outro serviço.

Registre identificador de evento/correlação, idade da mensagem, backlog, falhas, throttling e DLQ; defina alarme e runbook de redrive. Uma DLQ precisa de política de retenção e pessoa responsável. Mensagens sensíveis devem ter payload mínimo e logging sanitizado. Outbox e idempotência da unidade 33.1 reduzem perda/duplicação na aplicação, mas não substituem a configuração do broker nem a observabilidade.

