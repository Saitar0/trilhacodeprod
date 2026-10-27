---
arquivo_id: "f6-29-1-04-isolamento-assertions-01-teoria-md"
parent_key: "29.1"
tipo_arquivo: "theory"
assunto: "04_isolamento_assertions"
ordem: 4
itens_origem: ["## Microtópico 4 — Isole dependências sem esconder defeitos"]
---

## Microtópico 4 — Isole dependências sem esconder defeitos
Mock é útil para controlar uma dependência externa ou uma resposta imprevisível, como API, relógio ou serviço de terceiros. Use a menor fronteira necessária: teste a interface com sucesso e falha controlados, sem substituir justamente o comportamento que quer verificar. Se todo o componente, incluindo sua regra principal, foi mockado, o teste pode passar sem testar o produto.

Cada teste deve preparar seus próprios dados e não depender da ordem de execução. Limpe mocks e estado compartilhado conforme a ferramenta e o setup do projeto. Prefira fixtures pequenas e legíveis, com diferenças importantes explícitas. Para consultas assíncronas, resolva ou rejeite a Promise de forma controlada e aguarde a interface chegar ao estado esperado.

Cobertura informa quais partes foram executadas, mas não mede se as assertions detectariam um defeito. Uma suíte pode ter alta cobertura e apenas confirmar que elementos existem, sem testar a regra. Uma verificação útil é introduzir temporariamente uma falha plausível — por exemplo, remover uma validação — e observar se o teste relacionado falha. Depois restaure o código e mantenha a assertion que detecta o comportamento quebrado.

