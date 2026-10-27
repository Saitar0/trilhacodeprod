---
arquivo_id: "f6-27-1-01-contrato-requisicao-resposta-01-teoria-md"
parent_key: "27.1"
tipo_arquivo: "theory"
assunto: "01_contrato_requisicao_resposta"
ordem: 1
itens_origem: ["## Microtópico 1 — Requisição e resposta seguem o contrato da API"]
---

## Microtópico 1 — Requisição e resposta seguem o contrato da API

Antes de chamar o backend, confirme método, rota, parâmetros, headers, formato do corpo, autenticação e esquema da resposta. A interface não deve inventar nomes de campo nem pressupor que todos os endpoints respondem JSON. O contrato também define paginação, códigos de status e formato de erro.

fetch retorna uma Promise com Response quando recebe uma resposta HTTP, mesmo que o status seja 401, 404 ou 500. Verifique response.ok ou response.status antes de tratar o corpo como sucesso. Problemas de rede, bloqueio CORS e cancelamento podem rejeitar a Promise; esses casos não são a mesma coisa que uma resposta HTTP de erro.

Nem toda resposta tem corpo JSON: 204 No Content não deve ser processada com response.json(). Se o contrato retorna JSON, valide o resultado ao decodificar; se retorna erro estruturado, leia com cuidado e converta para uma mensagem/modelo adequado à UI. Evite mostrar stack trace, cabeçalho sensível ou conteúdo interno do servidor à pessoa usuária.

```js
async function loadOrders(url, signal, accessToken) {
  const headers = { Accept: "application/json" };

  if (accessToken) {
    headers.Authorization = "Bearer " + accessToken;
  }

  const response = await fetch(url, { headers, signal });

  if (!response.ok) {
    throw new Error("Falha HTTP: " + response.status);
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}
```

O exemplo é um ponto de partida, não um cliente universal: a API pode não usar bearer, pode exigir Content-Type somente em requisições com corpo ou pode ter esquema de erro próprio. Evite esconder comportamentos diferentes numa função genérica antes de entender os endpoints usados.

