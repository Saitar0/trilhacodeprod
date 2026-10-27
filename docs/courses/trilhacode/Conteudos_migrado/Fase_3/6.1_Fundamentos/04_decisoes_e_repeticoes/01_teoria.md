---
arquivo_id: "f3-6-1-04-decisoes-e-repeticoes-01-teoria"
parent_key: "6.1"
tipo_arquivo: "theory"
assunto: "04_decisoes_e_repeticoes"
ordem: 4
itens_origem: ["Decisões com condicionais", "Repetições e encerramento"]
---

### Decisões com condicionais
`if/else` escolhe um caminho conforme uma expressão que pode ser avaliada como verdadeira ou falsa. Use comparações explícitas para tornar a regra legível e considere os limites: se aprovação ocorre com nota 7, `media >= 7` inclui exatamente 7, enquanto `media > 7` não inclui. Mais de duas faixas podem usar `else if`, cuidando da ordem das condições.

### Repetições e encerramento
Laços repetem operações. `for` é útil quando o controle de início, condição e atualização fica explícito; `while` continua enquanto sua condição for verdadeira; `for...of` percorre valores iteráveis, como elementos de um array, sem expor o índice. Garanta que o laço terá uma condição de parada. Para um array vazio, `for...of` executa zero vezes; qualquer cálculo posterior deve tratar o caso antes de dividir pelo tamanho do array.

```js
const notas = [8, 6, 9];
let total = 0;

for (const nota of notas) {
  total += nota;
}

const media = notas.length === 0 ? 0 : total / notas.length;
if (media >= 7) {
  console.log(`Aprovada: ${media}`);
} else {
  console.log(`Revisar: ${media}`);
}
```

