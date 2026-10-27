---
arquivo_id: "f6-25-2-03-colecoes-imutaveis-identidade-01-teoria-md"
parent_key: "25.2"
tipo_arquivo: "theory"
assunto: "03_colecoes_imutaveis_identidade"
ordem: 3
itens_origem: ["## Microtópico 3 — Atualize arrays e objetos sem mutar o estado"]
---

## Microtópico 3 — Atualize arrays e objetos sem mutar o estado

Arrays e objetos guardados em estado devem ser tratados como somente leitura. Não use push, splice ou atribuição a uma propriedade do objeto existente e depois passe a mesma referência ao setter. Crie uma nova coleção e, quando um item mudar, também crie um novo objeto para esse item.

- Adicionar: criar array novo com spread ou concat.
- Remover: criar array novo com filter.
- Atualizar um item: mapear e retornar cópia com os campos alterados.
- Ordenar: copiar a lista primeiro e ordenar a cópia, pois sort altera o array.

A cópia de um array é superficial. Copiar a lista não autoriza alterar um objeto que continua compartilhado dentro dela. Copie o item que muda também.

```jsx
function toggleTask(id) {
  setTasks((current) =>
    current.map((task) =>
      task.id === id
        ? { ...task, completed: !task.completed }
        : task
    )
  );
}
```

Cada elemento diretamente renderizado por map precisa de key única entre irmãos e estável ao longo das renderizações. Use ID associado aos dados. Não gere key aleatória durante renderização; ela muda a cada chamada e impede React de reconhecer a continuidade do item. O índice só é adequado em listas estáticas que nunca reordenam, inserem ou removem itens; prefira identidade do dado para tarefas editáveis. Key é uma pista para React, não uma prop recebida automaticamente pelo componente filho.

