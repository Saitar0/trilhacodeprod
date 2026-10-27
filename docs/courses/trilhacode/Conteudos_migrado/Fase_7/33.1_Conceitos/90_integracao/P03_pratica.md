---
arquivo_id: "f7-33-1-90-integracao-p03-pratica-md"
parent_key: "33.1"
tipo_arquivo: "practice"
assuntos: ["02_retry_backoff_dlq", "03_idempotencia_outbox_consistencia"]
ordem: 3
itens_origem: ["P03"]
---

### Atividade 3 — Defina política de retry e DLQ

**Desafio:** estabeleça uma política operacional para falha transitória e poison message.

**Passos:**
1. Classifique exemplos de falha em transitória, permanente ou desconhecida e defina a ação para cada classe.
2. Escolha máximo de tentativas, backoff, jitter/intervalo, timeout e condição de encaminhamento para DLQ, justificando os valores no contexto fictício.
3. Defina métricas/alertas para backlog, idade da mensagem, taxa de falha, redrive e profundidade/idade da DLQ.
4. Escreva runbook para inspecionar payload sem expor dados, encontrar causa, corrigir consumidor/dados e reprocessar com segurança.
5. Determine como preservar ordem por entidade se houver eventos dependentes.

**Evidências:** tabela erro → política; sequência temporal de tentativas; contrato e retenção da DLQ; alertas e runbook de redrive.

**Verificação:** retry é limitado; falha permanente não gira indefinidamente; redrive considera efeito anterior, versão do schema e idempotência; alerta chega antes de acumular backlog sem dono.

**Aceite:** política diferencia falhas; DLQ tem responsável, retenção e procedimento; reprocessamento não promete correção automática; ordenação e observabilidade foram avaliadas.

