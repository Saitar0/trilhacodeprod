---
arquivo_id: "f6-28-2-02-identidade-de-consultas-01-teoria-md"
parent_key: "28.2"
tipo_arquivo: "theory"
assunto: "02_identidade_de_consultas"
ordem: 2
itens_origem: ["## Microtópico 2 — Dê identidade estável às consultas"]
---

## Microtópico 2 — Dê identidade estável às consultas
Uma consulta precisa de uma chave que identifique exatamente o resultado que está buscando. No TanStack Query, a query key é uma estrutura serializável, normalmente um array. Inclua os parâmetros que alteram a resposta: recurso, identificador, página, filtro, ordenação ou escopo de conta quando aplicável. Assim, resultados de consultas diferentes não são tratados como se fossem o mesmo dado.

Uma regra prática: se mudar uma variável usada pela função de consulta e isso puder mudar os dados retornados, essa variável deve fazer parte da chave. Não inclua valores voláteis sem necessidade, pois isso fragmenta o cache. Não use a chave como depósito de segredos: chaves podem aparecer em ferramentas de depuração, logs ou telemetria. Use identificadores não sensíveis e proteja o acesso à própria aplicação no servidor.

Chaves hierárquicas facilitam encontrar famílias de consultas para invalidar. Por exemplo, `['orders']` pode identificar a família e `['orders', { page, status }]` uma lista com parâmetros específicos. Mantenha uma convenção consistente e evite objetos ou funções não serializáveis como parte da identidade.

