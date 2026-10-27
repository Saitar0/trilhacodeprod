---
arquivo_id: "f9-40-3-90-integracao-p02-pratica"
parent_key: "40.3"
tipo_arquivo: "practice"
assuntos: ["02_entrega_falhas_duplicatas", "03_ordem_escala_replay", "04_operacao_custo_decisao"]
ordem: 2
itens_origem: ["P02"]
---


### Atividade 2 — Rastreie a falha e proponha recuperação
**Contexto:** examine quatro eventos de falha: (1) RabbitMQ consumidor grava no banco e cai antes do ack; (2) produtor Kafka repete envio após timeout sem saber se o primeiro foi persistido; (3) worker SQS excede visibility timeout enquanto processa; (4) assinante Pub/Sub não confirma antes do ack deadline. Para cada caso, desenhe estados da mensagem e do efeito de negócio.

**Instruções:** marque se pode ocorrer redelivery, duplicação do efeito ou perda lógica; proponha proteção idempotente; indique configuração/telemetria de retry e DLQ; descreva como testar em ambiente local ou simulado. Não suponha que dois produtos compartilham a mesma semântica.

**Entrega:** quatro linhas de tabela (falha, estado do broker, risco no destino, mitigação, evidência do teste) e uma sequência de redrive seguro.

**Dica gradual:** pergunte em qual instante o efeito persistiu; em seguida, se a confirmação chegou ao broker; por fim, imagine uma repetição integral da operação.

