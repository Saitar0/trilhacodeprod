---
arquivo_id: "f3-7-3-01-formato-e-contrato-json-01-teoria"
parent_key: "7.3"
tipo_arquivo: "theory"
assunto: "01_formato_e_contrato_json"
ordem: 1
itens_origem: ["1. Dados JSON e contrato da API"]
---

## Teoria

### 1. Dados JSON e contrato da API
JSON é um formato textual de intercâmbio de dados. Embora objetos e arrays JSON se pareçam com literais JavaScript, JSON tem sintaxe própria: chaves e strings usam aspas duplas, não há funções nem valores como `undefined`, e uma vírgula final torna o texto inválido. `JSON.parse(texto)` converte texto JSON válido em valores JavaScript; `JSON.stringify(valor)` cria texto JSON a partir de valores compatíveis.

Uma API também define um **contrato**: quais campos envia, quais campos espera e que tipo de resultado representa sucesso ou falha. Receber JSON válido não garante que a estrutura é a esperada. Se o código precisa de `produto.nome`, confirme que cada item contém esse campo antes de usá-lo ou mostrá-lo.

```js
const texto = '[{"nome":"Caderno","preco":18}]';
const produtos = JSON.parse(texto);
console.log(produtos[0].nome); // "Caderno"
```

**Erro comum:** tratar “o corpo foi convertido em JSON” como prova de que os dados têm os campos e tipos necessários. Sintaxe válida e formato esperado são verificações diferentes.

