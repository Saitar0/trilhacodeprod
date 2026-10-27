---
arquivo_id: "f3-6-2-04-transformacao-mutacao-01-teoria"
parent_key: "6.2"
tipo_arquivo: "theory"
assunto: "04_transformacao_mutacao"
ordem: 4
itens_origem: ["Transformação e mutação"]
---

### Transformação e mutação
Transformar uma coleção e alterar a coleção original são operações diferentes. `filter()` devolve um novo array com os itens que passaram pelo teste; `sort()` reorganiza o array original e devolve uma referência a esse mesmo array. Para ordenar sem alterar a lista recebida, faça uma cópia rasa com `slice()` antes de chamar `sort()`.

```js
function ordenarPorPrioridade(tarefas) {
  return tarefas.slice().sort((a, b) => a.prioridade - b.prioridade);
}
```

O comparador numérico define a ordem crescente. Se duas prioridades forem iguais, retornar `0` indica que o par é equivalente para essa ordenação; em JavaScript moderno, a ordenação estável preserva a ordem relativa desses itens. A cópia do array não duplica os objetos dentro dele; nesta unidade, a função só reorganiza as referências, sem alterar as propriedades das tarefas.

Teste casos comuns e de borda: lista vazia, elemento ausente, valores repetidos e prioridades iguais. Separar transformação da apresentação torna a função mais fácil de reutilizar.

