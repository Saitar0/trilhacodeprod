---
arquivo_id: "f8-38-2-90-integracao-p02-pratica-md"
parent_key: "38.2"
tipo_arquivo: "practice"
assuntos: ["01_fluxo_otel_prometheus_promql", "02_grafana_dashboards_operacao"]
ordem: 2
itens_origem: ["P02"]
---

### Atividade 2 — Consultar métricas e compor um dashboard
Use o contrato de métricas `http_requests_total{route,status}` e `http_request_duration_seconds_bucket{route,le}` descrito nesta aula. Implemente as consultas de taxa, proporção 5xx e p95, e monte um dashboard com um painel por pergunta. A atividade pode ser feita numa stack local com Compose/Prometheus/Grafana e app instrumentada, ou com dados de exemplo se o ambiente local não estiver disponível.

**Entrega:** consultas, captura ou descrição dos painéis e uma legenda que informe unidade, janela, agrupamento e interpretação do p95. Se usar stack local, inclua configuração de scrape e o resultado de pelo menos uma consulta.

**Critérios de aceite:** taxa e erro usam `rate` no intervalo; denominador do erro é o total no mesmo período; p95 mantém `le` na agregação e agrupa por rota; os painéis deixam clara unidade e janela; labels permanecem de baixa cardinalidade.

**Feedback esperado:** se o p95 não retornar dados, confira se o endpoint expõe os buckets esperados e se a consulta preserva `le`; não substitua por média e mantenha o rótulo p95.

