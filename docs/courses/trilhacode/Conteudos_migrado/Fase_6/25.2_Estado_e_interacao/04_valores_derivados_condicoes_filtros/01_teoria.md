---
arquivo_id: "f6-25-2-04-valores-derivados-condicoes-filtros-01-teoria-md"
parent_key: "25.2"
tipo_arquivo: "theory"
assunto: "04_valores_derivados_condicoes_filtros"
ordem: 4
itens_origem: ["## Microtópico 4 — Derive condições e filtros do estado essencial"]
---

## Microtópico 4 — Derive condições e filtros do estado essencial

A interface condicional escolhe o que apresentar a partir dos dados atuais. Uma lista vazia pode exibir orientação; uma lista preenchida pode mostrar resultados. Se o filtro muda, derive a coleção visível de tasks e filter em vez de armazenar também visibleTasks como estado separado.

```jsx
const visibleTasks = tasks.filter((task) => {
  if (filter === "active") return !task.completed;
  if (filter === "completed") return task.completed;
  return true;
});

const completedCount = tasks.filter((task) => task.completed).length;
```

Armazenar tarefas e também uma cópia atualizada de tarefas visíveis ou de contadores cria duas fontes de verdade. Se uma mudança atualiza uma delas e esquece outra, a UI diverge. Guarde a entrada que muda e calcule valores simples derivados durante a renderização. Use estado separado quando representar uma informação realmente independente que muda — por exemplo, qual filtro foi selecionado.

Considere os estados visuais importantes: lista vazia, lista com itens, filtro sem resultados e item concluído. Expressões condicionais no JSX tornam o resultado de cada estado explícito; não esconda nem mostre elementos alterando manualmente o DOM.

