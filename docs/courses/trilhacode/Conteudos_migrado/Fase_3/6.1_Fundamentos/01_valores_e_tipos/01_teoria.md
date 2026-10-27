---
arquivo_id: "f3-6-1-01-valores-e-tipos-01-teoria"
parent_key: "6.1"
tipo_arquivo: "theory"
assunto: "01_valores_e_tipos"
ordem: 1
itens_origem: ["Valores e tipos"]
---

## Teoria

### Valores e tipos
Um programa manipula **valores**. JavaScript é dinamicamente tipada: o valor tem um tipo, mas uma variável pode receber valores de tipos diferentes. Tipos primitivos incluem `number`, `string`, `boolean`, `undefined`, `null`, `bigint` e `symbol`; `object` é outro tipo, e arrays e funções são objetos em sentido técnico. Nesta unidade, concentre-se em `number`, `string`, `boolean`, `undefined`, `null` e arrays.

`typeof` ajuda a inspecionar alguns valores, mas tem particularidades: `typeof null` retorna `"object"` por uma compatibilidade histórica. Portanto, para testar `null`, compare explicitamente com `=== null`. Uma variável declarada sem valor inicial com `let` recebe `undefined`; isso não é igual a `null`, que representa ausência intencional de valor em muitos contextos.

