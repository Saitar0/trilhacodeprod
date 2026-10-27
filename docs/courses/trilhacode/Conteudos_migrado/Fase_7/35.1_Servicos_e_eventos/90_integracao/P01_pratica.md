---
arquivo_id: "f7-35-1-90-integracao-p01-pratica-md"
parent_key: "35.1"
tipo_arquivo: "practice"
assuntos: ["01_contrato_sincrono_assincrono", "02_filas_pubsub_event_routing"]
ordem: 1
itens_origem: ["P01"]
---

### Atividade 1 — Compare serviços por requisito

**Desafio:** selecione serviços gerenciados para três fluxos e justifique a escolha com requisitos explícitos.

**Cenários:** (a) chamada HTTP que precisa responder em tempo real; (b) gerar relatório que pode levar minutos e deve tolerar pico; (c) avisar faturamento, auditoria e notificações quando um pedido muda de estado.

**Passos:**
1. Descreva produtor, consumidor(es), resposta esperada, volume/picos, necessidade de buffer, fan-out, filtro, ordenação e latência.
2. Escolha entre API Gateway/Lambda, SQS, SNS, EventBridge ou combinação; inclua alternativas consideradas e motivo para descartá-las.
3. Desenhe contrato síncrono ou assíncrono, incluindo códigos/status, id da tarefa/evento e estado final visível.
4. Aponte os componentes que autorizam chamadas e quem mantém cada permissão.
5. Estime quais métricas e dimensões de custo seriam necessárias, sem inventar preço sem região/volume.

**Evidências:** matriz cenário × requisitos × serviço × justificativa; diagramas de sequência; contratos da API/evento.

**Verificação:** compare a escolha com o padrão real do serviço: SQS é pull/buffer, SNS push/fan-out, EventBridge regras de roteamento; serviço gerenciado não elimina contrato nem autorização.

**Aceite:** cada escolha atende às necessidades declaradas; alternativas e trade-offs aparecem; fluxo assíncrono não promete conclusão síncrona.

