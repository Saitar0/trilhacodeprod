---
arquivo_id: "f3-7-3-02-requisicao-async-resposta-erros-01-teoria"
parent_key: "7.3"
tipo_arquivo: "theory"
assunto: "02_requisicao_async_resposta_erros"
ordem: 2
itens_origem: ["2. Requisição HTTP e fluxo assíncrono", "3. Resposta HTTP, corpo e parsing", "4. Estados da interface, rede e CORS"]
---

### 2. Requisição HTTP e fluxo assíncrono
Métodos HTTP comunicam a intenção da operação. `GET` costuma consultar; `POST` costuma enviar dados para criação ou processamento; `PUT` substitui uma representação; `PATCH` pede uma alteração parcial; `DELETE` solicita remoção. O comportamento concreto depende do contrato da API. Headers carregam metadados: `Accept` indica formatos que o cliente pode receber; `Content-Type` descreve o formato do corpo enviado.

Uma Promise representa um resultado futuro que pode ser cumprido ou rejeitado. Uma função `async` sempre devolve uma Promise. `await` permite esperar por uma Promise e continuar o fluxo da função quando ela se resolver; não bloqueia toda a interface. Uma rejeição esperada deve ser tratada com `try/catch` ou com `.catch()`.

```js
async function buscarProdutos(url) {
  const resposta = await fetch(url, {
    headers: { Accept: "application/json" },
  });
  return resposta;
}
```

A chamada `fetch` inicia uma operação assíncrona. O `await` anterior a ela pausa essa função até que haja uma resposta disponível, enquanto o navegador pode continuar processando outras interações.

**Erro comum:** esquecer `await` e tentar ler `response.ok` do próprio objeto Promise, antes de receber o objeto Response.

### 3. Resposta HTTP, corpo e parsing
`fetch` normalmente resolve sua Promise quando recebe uma resposta HTTP, mesmo que o status seja `404` ou `500`. Por isso, verifique `response.ok` (verdadeiro para status de sucesso 2xx) ou `response.status` explicitamente. Só depois leia o corpo. `response.json()` também é assíncrono e rejeita se o corpo não puder ser interpretado como JSON.

```js
async function carregarProdutos() {
  const resposta = await fetch("/api/produtos", {
    headers: { Accept: "application/json" },
  });

  if (!resposta.ok) {
    throw new Error(`HTTP ${resposta.status}`);
  }

  return await resposta.json();
}
```

Neste exemplo, falha ao obter a resposta e resposta HTTP não bem-sucedida são situações distintas. Uma resposta 404 não dispara sozinha o `catch`: o código a converte em erro ao verificar `ok`. Se o servidor responder com HTML de erro ou JSON malformado, a leitura com `json()` também pode falhar.

**Erro comum:** mostrar “erro de rede” para todo problema. Registre status quando uma resposta HTTP existe; diferencie a falha de transporte da falha de status e da falha de parsing.

### 4. Estados da interface, rede e CORS
Uma interface que carrega dados deve representar os estados relevantes: carregando, sucesso (inclusive resultado vazio, se a API o permitir) e falha. Garanta que o estado de carregamento termine tanto no sucesso quanto no erro; `finally` é útil para uma limpeza comum. Exiba dados externos como texto, por exemplo com `textContent`, e não como HTML interpretável sem necessidade.

Uma falha de rede pode ocorrer antes que o JavaScript receba uma resposta, por exemplo quando a conexão falha. Já HTTP 500 significa que uma resposta chegou com status de erro. Um erro de parsing significa que o corpo não corresponde ao formato JSON esperado pelo leitor.

CORS (Cross-Origin Resource Sharing) controla, por meio de headers HTTP, se o navegador permite que uma página leia uma resposta de outra origem. A origem inclui esquema, host e porta. Para certas requisições, o navegador envia um preflight `OPTIONS` para verificar permissões antes da operação. A autorização necessária é configurada no servidor/API. `mode: "no-cors"` não é solução para obter dados: a resposta se torna opaca e o JavaScript não consegue ler seu corpo ou status.

**Erro comum:** tentar contornar CORS desligando proteções do navegador ou usar `no-cors` esperando receber JSON legível. Verifique a mensagem do console e, quando for CORS, ajuste a configuração do servidor que controla a API.

