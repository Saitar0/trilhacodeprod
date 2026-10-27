---
arquivo_id: "f8-38-2-01-resumo-md"
parent_key: "38.2"
tipo_arquivo: "resumo"
ordem: 0
itens_origem: ["Resumo"]
---

## Resumo
- OTel instrumenta e encaminha sinais; Prometheus coleta e consulta séries temporais; Grafana explora data sources e apresenta painéis/alertas.
- A aplicação e a configuração do pipeline precisam concordar sobre endpoint, nomes de métricas, labels e formato.
- Prometheus coleta alvos configurados; alvos inacessíveis ou caminhos incorretos produzem ausência de dados, mesmo quando a aplicação executa.
- PromQL agrega séries; p95 de histograma é uma estimativa que depende de buckets e agregação corretos.
- Dashboard e alerta devem responder perguntas acionáveis, com unidades, janelas e responsáveis.
- New Relic é um exemplo de backend gerenciado com decisões próprias de ingestão, retenção, preço e segurança.

