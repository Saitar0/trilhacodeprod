---
arquivo_id: "f7-35-1-01-resumo-md"
parent_key: "35.1"
tipo_arquivo: "resumo"
ordem: 0
itens_origem: ["Resumo"]
---

## Resumo
- API Gateway + Lambda pode atender requisição síncrona; fila transforma contrato em aceitação de trabalho assíncrono.
- SQS retém e distribui trabalho para consumo controlado; SNS faz fan-out; EventBridge roteia eventos por regras.
- Composições como SNS→SQS ou EventBridge→SQS combinam fan-out/roteamento com buffer e consumo independente.
- Retry e DLQ dependem do serviço e do tipo de integração; Lambda com SQS pode repetir lote e precisa de idempotência.
- ElastiCache acelera leituras, mas TTL e invalidação deixam janela de staleness; banco continua fonte durável.
- IAM, observabilidade, dados sensíveis e custo continuam parte da arquitetura gerenciada.

