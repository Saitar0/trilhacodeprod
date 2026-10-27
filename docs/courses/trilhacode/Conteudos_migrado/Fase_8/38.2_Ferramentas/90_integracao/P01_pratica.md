---
arquivo_id: "f8-38-2-90-integracao-p01-pratica-md"
parent_key: "38.2"
tipo_arquivo: "practice"
assuntos: ["01_fluxo_otel_prometheus_promql", "02_grafana_dashboards_operacao"]
ordem: 1
itens_origem: ["P01"]
---

### Atividade 1 — Desenhar e revisar o pipeline
Desenhe a rota de métricas entre uma aplicação web, OpenTelemetry Collector (se usado), Prometheus e Grafana. Marque o protocolo/formato em cada fronteira, quem inicia a coleta/transmissão, onde dados são guardados e onde são consultados. Depois analise três falhas: Prometheus não alcança o endpoint; Collector recebe, mas não exporta; Grafana aponta para data source incorreto.

**Entrega:** diagrama e checklist com pelo menos duas verificações observáveis por falha, incluindo alvo/status, logs ou métricas do componente e caminho de rede.

**Critérios de aceite:** distingue receiver, processor e exporter do Collector; aponta backend e data source; não presume que configurar OTel cria automaticamente scrape ou persistência.

**Feedback esperado:** comece pelo último ponto em que há evidência de dado, depois investigue o próximo salto; “a aplicação está rodando” não comprova ingestão.

