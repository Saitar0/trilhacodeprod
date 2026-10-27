---
arquivo_id: "f3-7-2-01-modulos-exportacoes-p01-pratica-guiada-ligacao-modulos"
parent_key: "7.2"
tipo_arquivo: "practice"
assunto: "01_modulos_exportacoes"
ordem: 1
itens_origem: ["P1"]
---

## Práticas

### 1. Guiada — corrija a ligação entre módulos
Considere:

```js
// calculos.js
export function calcularMedia(valores) {
  const total = valores.reduce((soma, valor) => soma + valor, 0);
  return valores.length === 0 ? 0 : total / valores.length;
}
```

```js
// app.js
import { calcularMediaNotas } from "./calculos.js";

const media = calcularMediaNotas([7, 9, 8]);
console.log(media);
```

**Tarefa:** encontre as divergências, corrija o import e explique por que a função não precisa ser uma variável global.

**Dica:** compare o nome entre chaves ao nome declarado depois de `export function`; depois confira o caminho.

