---
arquivo_id: "f9-43-1-90-integracao-p01-pratica"
parent_key: "43.1"
tipo_arquivo: "practice"
assuntos: ["01_php_composer_versoes", "02_ciclo_requisicao_laravel"]
ordem: 1
itens_origem: ["P01"]
---


### Atividade 1 — Trace uma requisição Laravel
**Contexto:** considere `GET /api/orders/{order}` que usa middleware `auth`, `OrderController`, model `Order` e retorna JSON.

**Instruções:** siga o percurso rota → middleware → controller → model/consulta → policy → resposta. Para cada etapa, indique onde procuraria no projeto, qual responsabilidade esperaria e como esse papel se compara aproximadamente a uma API Node. Liste também um risco de versão/dependência que verificaria ao abrir um repositório legado.

**Entrega:** tabela de seis ou mais etapas e uma nota curta com duas semelhanças e uma diferença de convenção.

**Dica:** procure primeiro `routes/`, depois controller, model, policy, `composer.json` e migrations; não conclua que `auth` é autorização de propriedade.

