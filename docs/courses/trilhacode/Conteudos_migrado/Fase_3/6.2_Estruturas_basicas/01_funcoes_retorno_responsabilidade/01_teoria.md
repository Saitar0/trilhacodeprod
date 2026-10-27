---
arquivo_id: "f3-6-2-01-funcoes-retorno-responsabilidade-01-teoria"
parent_key: "6.2"
tipo_arquivo: "theory"
assunto: "01_funcoes_retorno_responsabilidade"
ordem: 1
itens_origem: ["Funções, parâmetros e argumentos", "Retorno e responsabilidade"]
---

## Teoria

### Funções, parâmetros e argumentos
Uma **função** reúne uma tarefa que pode ser chamada com entradas. **Parâmetros** são nomes usados na definição; **argumentos** são valores passados na chamada. Definir uma função não executa seu corpo: a execução ocorre quando ela é chamada. Uma função deve ter responsabilidade compreensível e nome que indique seu propósito.

```js
function somar(a, b) {
  return a + b;
}

const resultado = somar(3, 4); // 3 e 4 são argumentos; a e b são parâmetros
```

### Retorno e responsabilidade
`return` encerra a execução da função e devolve um resultado; sem retorno explícito, a chamada produz `undefined`. `console.log` exibe um valor, mas não o devolve ao código que chamou a função. Separe cálculo de apresentação quando isso tornar a função reutilizável: retorne o resultado e deixe a chamada decidir como mostrá-lo.

