---
arquivo_id: "f3-6-2-01-funcoes-retorno-responsabilidade-p01-pratica-guiada-retorno"
parent_key: "6.2"
tipo_arquivo: "practice"
assunto: "01_funcoes_retorno_responsabilidade"
ordem: 1
itens_origem: ["P1"]
---

## Práticas

### 1. Guiada — diferencie exibição de retorno
Leia o código e preveja o valor de `resultado` e o que aparece no console.

```js
function calcularTotal(itens) {
  let total = 0;
  for (const item of itens) {
    total += item.preco;
  }
  console.log(total);
}

const resultado = calcularTotal([{ preco: 4 }, { preco: 7 }]);
console.log("retorno:", resultado);
```

**Tarefa:** ajuste a função para que a chamada devolva o total e não exiba nada por conta própria. Depois explique por que `total` não pode ser acessada diretamente fora da função.

**Dicas graduais:** (1) diferencie o valor impresso do valor devolvido; (2) acompanhe o escopo de `total`; (3) escolha em que ponto a função deve terminar e entregar o cálculo.

