---
arquivo_id: "f6-26-2-03-context-compartilhamento-01-teoria-md"
parent_key: "26.2"
tipo_arquivo: "theory"
assunto: "03_context_compartilhamento"
ordem: 3
itens_origem: ["## Microtópico 4 — Context alcança descendentes quando props viram ruído"]
---

## Microtópico 4 — Context alcança descendentes quando props viram ruído

Context disponibiliza um valor a componentes descendentes sem passá-lo explicitamente por todos os níveis intermediários. É útil quando muitos pontos da árvore precisam do mesmo dado de ambiente, como tema, idioma ou usuário autenticado. Antes de usar Context, avalie se props explícitas, children ou levantamento de estado já deixam o fluxo simples.

Crie o Context, forneça um valor num ancestral adequado e leia-o com useContext no componente consumidor. O provider deve envolver os consumidores; um componente não consegue ler com useContext um provider que ele próprio retorna abaixo de si. Quando não há provider correspondente, o valor padrão de createContext é usado, então escolha esse padrão conscientemente.

Context não é automaticamente estado global, store remota ou substituto de toda prop. O estado pode continuar local ao provider. Quando o valor fornecido muda, componentes que leem aquele Context são atualizados; Contexts muito amplos com dados que mudam por motivos distintos podem acoplar consumidores e trabalho desnecessários. Separe valores quando isso clarifica quem depende de quê e meça antes de introduzir otimizações.

```jsx
const ThemeContext = createContext("light");

function App() {
  return (
    <ThemeContext.Provider value="dark">
      <Page />
    </ThemeContext.Provider>
  );
}

function ThemeLabel() {
  const theme = useContext(ThemeContext);
  return <p>Tema atual: {theme}</p>;
}
```

O contexto percorre a árvore para consumidores; componentes intermediários não precisam encaminhar theme como prop se não o utilizam.

