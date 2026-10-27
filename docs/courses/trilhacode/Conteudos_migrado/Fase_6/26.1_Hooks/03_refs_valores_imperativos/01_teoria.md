---
arquivo_id: "f6-26-1-03-refs-valores-imperativos-01-teoria-md"
parent_key: "26.1"
tipo_arquivo: "theory"
assunto: "03_refs_valores_imperativos"
ordem: 3
itens_origem: ["## Microtópico 3 — useRef mantém um valor que não desenha a tela"]
---

## Microtópico 3 — useRef mantém um valor que não desenha a tela

useRef guarda um objeto cuja propriedade current persiste entre renderizações. Alterar current não pede uma renderização. Essa característica serve para referência a elemento DOM ou informação imperativa cuja mudança não precisa aparecer na UI, como o identificador de um timer.

```jsx
const inputRef = useRef(null);

function focusInput() {
  inputRef.current?.focus();
}

return (
  <>
    <input ref={inputRef} aria-label="Buscar" />
    <button onClick={focusInput}>Focar busca</button>
  </>
);
```

Se a mudança deve aparecer na tela, use estado, não ref. Não leia ou altere current durante a renderização para produzir JSX; isso faz a descrição depender de uma mutação que React não acompanha. Para atualizar um objeto/array visível, use o setter de estado com um valor novo.

