---
arquivo_id: "f3-6-1-90-integracao-p01-pratica-guiada-acumulador"
parent_key: "6.1"
tipo_arquivo: "practice"
assuntos: ["02_variaveis_e_reatribuicao", "03_operadores_e_conversao", "04_decisoes_e_repeticoes"]
ordem: 1
itens_origem: ["P1"]
---

## Práticas

### 1. Guiada — depure um acumulador
Preveja o resultado antes de alterar o código. Depois localize o erro e corrija-o.

```js
const valores = [8, 6, 9];
let total = 0;

for (let indice = 0; indice <= valores.length; indice++) {
  total += valores[indice];
}

const media = total / valores.length;
console.log(total, media);
```

**Tarefa:** explique por que o resultado não é o total e a média esperados; corrija o limite do laço; depois substitua a inicialização por `const valores = []`, descreva o resultado e acrescente o tratamento necessário.

**Dicas graduais:** (1) liste os índices existentes no array; (2) observe o valor acessado quando `indice` é igual a `valores.length`; (3) antes de dividir, verifique se há elementos.

