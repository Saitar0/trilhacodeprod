---
arquivo_id: "f8-38-1-03-tracing-contexto-otel-01-teoria-md"
parent_key: "38.1"
tipo_arquivo: "theory"
assunto: "03_tracing_contexto_otel"
ordem: 3
itens_origem: ["### Microtópico 3 — Acompanhar uma operação com traces e contexto", "### Microtópico 4 — Instrumentar com OpenTelemetry sem acoplar o backend"]
---

### Microtópico 3 — Acompanhar uma operação com traces e contexto

Um **span** descreve uma operação, normalmente com início, duração, resultado e atributos pertinentes. Spans podem ser aninhados ou ligados para mostrar dependências. Um trace ID identifica o trace; cada span também tem um span ID. Se um serviço chama outro, o contexto precisa ser propagado para que os spans pertençam ao fluxo correto.

OpenTelemetry usa o contexto de trace, incluindo o formato W3C Trace Context em muitos cenários HTTP, para transportar essa relação entre serviços instrumentados. Se uma fronteira não encaminha o contexto, o trace pode ficar dividido. Logs podem conter trace ID e span ID para facilitar a busca do evento correspondente ao trace. Métricas agregadas normalmente não representam um trace individual; a correlação entre elas depende de dimensões compatíveis, janelas de tempo ou recursos disponíveis no backend.

**Baggage** é contexto adicional que pode ser propagado entre serviços. Não o use como depósito de dados pessoais, segredos ou valores sem limite: informação propagada pode chegar a diversos serviços e aumentar exposição. Propague somente campos necessários e com uma política explícita.

### Microtópico 4 — Instrumentar com OpenTelemetry sem acoplar o backend

OpenTelemetry (OTel) fornece APIs e SDKs de instrumentação, protocolo de transmissão (OTLP), convenções semânticas e o Collector. Ele não é, por si só, o backend de consulta, armazenamento, dashboard ou alertas. A aplicação ou uma instrumentação automática produz sinais; um pipeline pode encaminhá-los para um Collector; o Collector pode receber, processar e exportar os dados para um ou mais destinos.

As **semantic conventions** padronizam atributos para operações comuns, como HTTP e banco de dados, facilitando análise entre linguagens e serviços. Reutilize convenções existentes antes de inventar campos próprios. Instrumentação automática acelera o início, mas deve ser revisada para verificar cobertura, ruído, custo, dados coletados e propagação. Instrumentação manual deve priorizar limites importantes do negócio e dependências que não foram capturadas automaticamente.

Amostragem de traces reduz volume, mas significa que nem todos os traces necessariamente estarão disponíveis. Métricas e logs podem ter regras de coleta diferentes. Para investigação de incidentes, entenda as regras de amostragem e confira se erros ou operações lentas recebem tratamento adequado; não prometa que um trace individual sempre existirá.

