---
arquivo_id: "f8-38-1-01-resumo-md"
parent_key: "38.1"
tipo_arquivo: "resumo"
ordem: 0
itens_origem: ["Resumo"]
---

## Resumo
- Logs registram eventos, métricas agregam medições e traces mostram o percurso de operações distribuídas.
- O sinal certo depende da pergunta; a correlação ajuda a investigar, mas não demonstra causa sozinha.
- Logs precisam de esquema estável; métricas precisam de dimensões controladas para evitar cardinalidade excessiva.
- Trace context relaciona spans entre serviços; baggage deve transportar apenas contexto necessário e seguro.
- OpenTelemetry padroniza instrumentação e transporte; Collector processa/encaminha sinais, enquanto o backend fornece consulta e armazenamento.
- Instrumentação precisa considerar minimização, acesso, retenção, custo e amostragem.

