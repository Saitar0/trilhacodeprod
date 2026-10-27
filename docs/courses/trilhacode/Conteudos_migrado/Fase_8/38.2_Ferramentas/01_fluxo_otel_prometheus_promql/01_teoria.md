---
arquivo_id: "f8-38-2-01-fluxo-otel-prometheus-promql-01-teoria-md"
parent_key: "38.2"
tipo_arquivo: "theory"
assunto: "01_fluxo_otel_prometheus_promql"
ordem: 1
itens_origem: ["### Microtópico 1 — Entender o fluxo e o papel de cada ferramenta", "### Microtópico 2 — Coletar e consultar métricas no Prometheus"]
---

### Microtópico 1 — Entender o fluxo e o papel de cada ferramenta

Um fluxo comum é: **aplicação instrumentada → endpoint/Collector → backend de armazenamento e consulta → dashboard/alerta**. Cada componente resolve uma parte do problema:

- **OpenTelemetry (OTel):** APIs, SDKs, instrumentações, OTLP e Collector para produzir, padronizar, receber, processar e encaminhar traces, métricas e logs. O Collector pode filtrar/enriquecer dados no pipeline, mas não substitui automaticamente o backend onde a equipe consulta e retém os sinais.
- **Prometheus:** coleta principalmente métricas por *scrape* de endpoints configurados, guarda séries temporais e consulta-as com PromQL. Exporters podem expor métricas de sistemas que não produzem o formato esperado. Planeje alcance de rede e descoberta dos alvos.
- **Grafana:** conecta-se a *data sources* e consulta os backends para explorar dados, criar painéis e configurar alertas conforme o recurso escolhido. Um painel não transforma Grafana no armazenamento do Prometheus; a linguagem de consulta também depende da fonte.
- **New Relic:** exemplo de plataforma gerenciada que pode receber OTLP e oferecer armazenamento, consultas, dashboards e alertas. Avalie ingestão, limites, retenção, preço, localização e política de dados antes de enviar telemetria.

Duas integrações comuns não devem ser confundidas: a aplicação pode expor um endpoint de métricas para que Prometheus o colete; ou um Collector pode receber métricas OTLP e expor/exportar métricas para coleta Prometheus. O caminho depende dos componentes habilitados e da versão/distribuição do Collector. Sempre verifique o pipeline real e não suponha que todos os sinais estejam configurados só porque a aplicação inicializou o SDK.

### Microtópico 2 — Coletar e consultar métricas no Prometheus

A configuração de Prometheus define alvos de *scrape* e a frequência da coleta. Se um alvo está indisponível, não basta que a aplicação esteja funcionando: confirme endereço e porta alcançáveis a partir do processo Prometheus, caminho do endpoint, formato exposto e estado do alvo na interface/consulta de targets.

PromQL seleciona e agrega séries. `rate(counter[5m])` estima a taxa por segundo de um contador no intervalo; use uma janela adequada ao intervalo de coleta e à pergunta. Para comparar rotas, mantenha labels controladas como rota normalizada e status. IDs de usuário, URL completa e mensagens de erro livres não devem ser labels.

Para esta prática, considere que a aplicação expõe um contador `http_requests_total{route, status}` e um histograma clássico `http_request_duration_seconds_bucket{route, le}`. Consultas possíveis:

```promql
sum by (route) (rate(http_requests_total[5m]))
```

Taxa de respostas 5xx sobre o total, para o mesmo intervalo:

```promql
sum(rate(http_requests_total{status=~"5.."}[5m]))
/
sum(rate(http_requests_total[5m]))
```

Estimativa de p95 por rota a partir dos buckets do histograma clássico:

```promql
histogram_quantile(
  0.95,
  sum by (route, le) (rate(http_request_duration_seconds_bucket[5m]))
)
```

A consulta de quantil precisa dos buckets compatíveis e estima o valor com base neles; não é o tempo exato de 95% de cada requisição individual. Ao agregar histograma clássico, preserve o label `le`. Nomes e labels do exercício são um contrato de exemplo: bibliotecas e instrumentações OTel podem expor nomes diferentes ou exigir conversão/configuração para esse formato.

