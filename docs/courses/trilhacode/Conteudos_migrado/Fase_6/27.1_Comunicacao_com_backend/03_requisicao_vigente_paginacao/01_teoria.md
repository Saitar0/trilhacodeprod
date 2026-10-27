---
arquivo_id: "f6-27-1-03-requisicao-vigente-paginacao-01-teoria-md"
parent_key: "27.1"
tipo_arquivo: "theory"
assunto: "03_requisicao_vigente_paginacao"
ordem: 3
itens_origem: ["## Microtópico 3 — Integração React acompanha a requisição vigente", "## Microtópico 4 — Paginação, filtros e ordem dos resultados"]
---

## Microtópico 3 — Integração React acompanha a requisição vigente

Ao iniciar uma requisição, a interface pode precisar indicar carregamento, resultado e erro. Mantenha esses estados coerentes com a intenção atual: se a pessoa muda o filtro de “abertas” para “concluídas”, uma resposta lenta do filtro anterior não deve substituir a nova lista.

Se a requisição é sincronização declarada a partir de props/estado, um Effect pode iniciar a chamada com AbortController e abortá-la na limpeza quando a dependência mudar ou o componente sair. A aplicação deve distinguir cancelamento esperado de falha visível. Também é possível ignorar o resultado antigo com um marcador; cancelar economiza trabalho quando o serviço suporta signal, mas não garante que o servidor não tenha processado a operação.

Se a chamada acontece por ação explícita de envio, o handler do formulário/botão normalmente inicia a operação; não use Effect apenas para reagir a um booleano de clique duplicado. Para fluxos com cache, deduplicação, invalidação ou muitas requisições concorrentes, siga a camada de dados já adotada pelo projeto em vez de improvisar outra.

Cuidado com mutações: cancelar uma requisição de leitura costuma ser seguro; cancelar no navegador não desfaz um POST que o servidor já recebeu. Para ações de escrita, previna envio duplicado com estado e contrato apropriados, e use idempotency key se a API oferecer suporte.

## Microtópico 4 — Paginação, filtros e ordem dos resultados

Siga o formato de paginação do backend. Paginação por página pode receber page e limit e retornar total; cursor pode retornar próximo cursor e hasMore. Cursor é opaco se o contrato o define assim: repasse o valor recebido sem inventar cálculo a partir dele.

A URL deve refletir filtros que precisam ser compartilhados ou restaurados ao voltar à página; codifique parâmetros corretamente. Defina limite máximo aceito pela API e trate lista vazia, primeira/última página e resultado que encolhe após exclusão. Se o total muda enquanto a pessoa navega, a página atual pode ficar fora do intervalo; ajuste com base nos metadados do servidor.

Filtro, ordenação, página e resultados são relacionados. Quando o filtro muda, normalmente recomece da primeira página e inicie requisição para o novo conjunto. Mantenha a resposta associada aos parâmetros que a produziram; descarte resultado atrasado de uma combinação anterior. Não derive número de páginas de uma estimativa quando o contrato fornece metadados oficiais.

