---
arquivo_id: "f6-27-3-90-integracao-p02-pratica-md"
parent_key: "27.3"
tipo_arquivo: "practice"
assuntos: ["01_fronteira_contrato_validacao_runtime", "02_presenca_nulidade_variacoes"]
ordem: 2
itens_origem: ["P02"]
---

### Atividade 2 — Validar JSON externo e adaptar para a UI
**Contexto e objetivo:** impedir que resposta inesperada chegue à interface como se fosse confiável.

**Dados iniciais válidos:** o exemplo da Atividade 1. Teste também estas respostas inválidas: `{"items":[{"id":12,"title":false}],"page":0,"pageSize":20,"total":1}` e `{"items":null,"page":1,"pageSize":20,"total":0}`.

**Instruções:** implemente, na linguagem/stack da unidade, uma função que receba `unknown` e retorne resultado discriminado (sucesso com dados validados ou erro controlado). Valide tipos, `page >= 1`, `pageSize` dentro do limite decidido, `total >= 0`, `id` e `title`; preserve `dueDate: null`. Converta o valor validado para modelo da UI, sem afirmação `as` na fronteira. Mostre tratamento distinto para falha HTTP, JSON inválido e payload com schema inválido.

**Entrega:** função/guard/schema, três testes com os dados indicados e um exemplo de como a UI representa erro sem crash.

**Dica gradual:** comece verificando que o valor é objeto não nulo; depois valide cada propriedade antes de usá-la. Um tipo de resultado como `{ ok: true, data } | { ok: false, reason }` ajuda o consumidor a tratar os dois caminhos.

**Feedback e erro comum:** resposta válida deve ser estreitada sem coerção insegura; ambas as inválidas devem ser rejeitadas com motivo seguro. Erro comum: validar só se o corpo é objeto e depois presumir que todos os campos internos estão corretos.

