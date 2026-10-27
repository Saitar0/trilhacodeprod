---
arquivo_id: "f3-6-3-01-declaracoes-arrow-retorno-p01-pratica-guiada-retorno-objeto"
parent_key: "6.3"
tipo_arquivo: "practice"
assunto: "01_declaracoes_arrow_retorno"
ordem: 1
itens_origem: ["P1"]
---

## Práticas

### 1. Guiada — corrija retorno e literal de objeto
Analise duas funções e preveja o resultado das chamadas:

```js
const dobrar = (valor) => {
  valor * 2;
};

const criarTarefa = (titulo) => { titulo: titulo };
```

**Tarefa:** ajuste as funções para que `dobrar(4)` resulte em `8` e `criarTarefa("Estudar")` resulte em `{ titulo: "Estudar" }`. Use retorno implícito onde couber e explique por que as versões originais não entregam esses valores.

**Dicas graduais:** (1) observe se o corpo é expressão ou bloco; (2) procure um `return` no bloco; (3) em objeto retornado implicitamente, diferencie as chaves do objeto das chaves do bloco.

