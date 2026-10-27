---
arquivo_id: "f6-25-2-02-eventos-atualizadores-01-teoria-md"
parent_key: "25.2"
tipo_arquivo: "theory"
assunto: "02_eventos_atualizadores"
ordem: 2
itens_origem: ["## Microtópico 2 — Eventos pedem mudanças; renderização descreve o resultado"]
---

## Microtópico 2 — Eventos pedem mudanças; renderização descreve o resultado

Passe uma função ao evento, como onClick={handleClick}; não execute handleClick() durante a renderização. A função do evento representa uma ação que acontecerá quando a pessoa interagir. Dentro dela, faça a alteração de estado apropriada; React calculará a UI de acordo com o novo estado.

React pode agrupar atualizações feitas durante um evento. Se três atualizações dependem de um valor anterior e todas usam o mesmo snapshot, definir repetidamente valor + 1 pode produzir uma única elevação, em vez de somar três. Usar a forma funcional permite que cada atualização receba o resultado da anterior.

```jsx
function addThree() {
  setCount((current) => current + 1);
  setCount((current) => current + 1);
  setCount((current) => current + 1);
}

return <button onClick={addThree}>Somar três</button>;
```

Use uma expressão inline somente quando ela continuar clara, como onClick={() => removeTask(task.id)}. Evite chamar o handler ao montar o JSX, porque isso executaria a lógica durante a renderização e o resultado da chamada poderia ser passado ao evento por engano.

