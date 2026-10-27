---
arquivo_id: "f8-38-1-90-integracao-p02-pratica-md"
parent_key: "38.1"
tipo_arquivo: "practice"
assuntos: ["01_escolha_dos_sinais", "03_tracing_contexto_otel"]
ordem: 2
itens_origem: ["P02"]
---

### Atividade 2 — Montar o caminho de uma requisição
Considere um fluxo fictício **Navegador → API → serviço de pedidos → serviço de pagamento → banco**. Faça um diagrama simples de spans e marque onde o trace context precisa ser encaminhado. Para cada falha, indique o sinal inicial e a próxima evidência a consultar: aumento geral de latência; uma chamada de pagamento lenta; timeout do banco em uma única requisição.

**Entrega:** diagrama, campos mínimos de correlação nos logs e uma sequência de investigação para cada sintoma.

**Critérios de aceite:** trace ID/span ID são usados para correlacionar sem serem rótulos de métrica; os três sintomas começam com sinais adequados; a resposta diferencia sintoma de causa confirmada.

**Feedback esperado:** se o trace parar na API, verifique instrumentação e propagação na fronteira seguinte; não conclua que o pagamento causou o incidente apenas porque está no caminho.

