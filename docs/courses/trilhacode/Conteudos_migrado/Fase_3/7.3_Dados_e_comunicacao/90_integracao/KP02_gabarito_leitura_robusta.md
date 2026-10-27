---
arquivo_id: "f3-7-3-90-integracao-kp02-gabarito-leitura-robusta"
parent_key: "7.3"
tipo_arquivo: "answer_key_pratica"
assuntos: ["01_formato_e_contrato_json", "02_requisicao_async_resposta_erros"]
ordem: 2
itens_origem: ["P2"]
---

**Solução de referência:**
```js
async function carregarCatalogo(url) {
  const resposta = await fetch(url, {
    headers: { Accept: "application/json" },
  });

  if (!resposta.ok) {
    throw new Error(`HTTP ${resposta.status}`);
  }

  let dados;
  try {
    dados = await resposta.json();
  } catch {
    throw new Error("Corpo da resposta não é JSON válido");
  }

  if (dados === null || typeof dados !== "object" || !Array.isArray(dados.items)) {
    throw new Error("Formato inesperado: items deve ser um array");
  }

  return dados.items;
}
```

A chamada pode tratar falha de rede/CORS no componente que a utiliza, pois essas falhas rejeitam a operação antes de uma resposta legível. Aceite mensagens equivalentes que indiquem a etapa e preservem o status HTTP.

