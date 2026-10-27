---
arquivo_id: "f9-44-1-90-integracao-p01-pratica"
parent_key: "44.1"
tipo_arquivo: "practice"
assuntos: ["01_csharp_sdk_pipeline_api", "02_injecao_dependencia_persistencia"]
ordem: 1
itens_origem: ["P01"]
---


### Atividade 1 — Trace endpoint e ciclo de vida
**Contexto:** uma API tem `GET /orders/{id}`, controller `OrdersController`, serviço `OrderService` e `AppDbContext`. O DbContext está registrado como scoped; `OrderService` foi registrado como singleton.

**Instruções:** desenhe a requisição desde rota até resposta; marque em que ponto cada dependência é resolvida; explique o problema potencial no lifetime atual; proponha registro coerente e indique qual consulta/verificação faria. Compare esse caminho a uma rota Node com middleware/controller/service.

**Entrega:** diagrama curto, ciclo de vida proposto e justificativa de até 120 palavras.

**Dica gradual:** acompanhe a árvore de dependências. O serviço singleton retém suas dependências por mais tempo do que o escopo de uma requisição.

