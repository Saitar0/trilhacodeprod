---
arquivo_id: "f9-40-3-90-integracao-p01-pratica"
parent_key: "40.3"
tipo_arquivo: "practice"
assuntos: ["01_modelar_problema_antes_escolha", "02_entrega_falhas_duplicatas", "03_ordem_escala_replay", "04_operacao_custo_decisao"]
ordem: 1
itens_origem: ["P01"]
---


### Atividade 1 — Matriz de decisão para três cenários
**Contexto:** uma plataforma tem (A) tarefas de e-mail sem necessidade de replay, (B) eventos de pedido relidos por três consumidores independentes por 14 dias e (C) comandos por cliente que precisam manter sequência. Compare RabbitMQ, Kafka, SQS e Pub/Sub em uma tabela.

**Instruções:** para cada cenário, marque requisitos eliminatórios; escolha uma opção principal e uma alternativa; explique entrega/redelivery, ordem, retenção/replay, escala, operação e dois drivers de custo; declare uma limitação e uma hipótese a validar. Não atribua garantias sem apontar configuração e fonte.

**Entrega:** tabela preenchida e recomendação de até 150 palavras por cenário. Fontes devem apontar para a documentação oficial pertinente.

**Dica gradual:** primeiro marque se o cenário é fila ou log; depois determine escopo de ordenação e necessidade de replay; por último compare carga operacional e custos.

