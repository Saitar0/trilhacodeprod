---
arquivo_id: "f6-26-1-01-regras-de-chamada-01-teoria-md"
parent_key: "26.1"
tipo_arquivo: "theory"
assunto: "01_regras_de_chamada"
ordem: 1
itens_origem: ["## Microtópico 1 — Hooks obedecem a regras de chamada"]
---

## Microtópico 1 — Hooks obedecem a regras de chamada

Hooks permitem que componentes funcionais usem estado, contexto, efeitos e outras capacidades do React. Os Hooks fornecidos pelo React começam com use, como useState e useEffect. Custom Hooks também começam com use e podem compor outros Hooks para reaproveitar lógica com estado.

Chame Hooks somente no nível superior do corpo de um componente funcional ou custom Hook. Não os coloque dentro de condições, loops, funções aninhadas, blocos try ou após uma saída antecipada. React associa estado e efeitos à ordem em que os Hooks são chamados; manter essa ordem igual entre renderizações permite associar cada valor ao Hook correto.

```jsx
function Status({ enabled }) {
  const [count, setCount] = useState(0);

  if (!enabled) {
    return <p>Desativado</p>;
  }

  useEffect(() => {
    document.title = "Contagem: " + count;
  }, [count]);

  return <button onClick={() => setCount((value) => value + 1)}>{count}</button>;
}
```

O exemplo viola a regra porque, quando enabled é false, o componente retorna antes de chamar useEffect. Corrija mantendo todos os Hooks no topo e tornando a lógica condicional dentro do Hook, ou extraindo a parte condicional para outro componente. Uma custom Hook compartilha lógica; cada chamada mantém seu próprio estado. Ela não cria estado compartilhado entre componentes automaticamente.

