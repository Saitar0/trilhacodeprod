---
arquivo_id: "f6-25-2-01-estado-snapshot-formulario-controlado-01-teoria-md"
parent_key: "25.2"
tipo_arquivo: "theory"
assunto: "01_estado_snapshot_formulario_controlado"
ordem: 1
itens_origem: ["## Microtópico 1 — Estado é a memória que muda a interface", "## Microtópico 5 — Formulário controlado mantém uma fonte clara"]
---

## Microtópico 1 — Estado é a memória que muda a interface

Props descrevem dados recebidos do componente pai; **estado** é memória que pertence à interface e pode mudar com o tempo. Em um componente funcional, o Hook useState fornece o valor desta renderização e uma função para pedir a atualização. O estado não é uma variável comum que o componente altera diretamente.

Quando o componente chama o setter, React registra a atualização e pode renderizar o componente novamente com o novo estado. A variável lida pelo handler atual continua sendo a fotografia da renderização em que esse handler foi criado. Por isso, ler a variável imediatamente depois do setter não mostra o valor atualizado nessa mesma execução.

```jsx
const [count, setCount] = useState(0);

function increment() {
  setCount((current) => current + 1);
}
```

A forma funcional usa o estado anterior no momento em que React processa a atualização. É especialmente apropriada quando o novo valor depende do anterior, como incrementar, alternar um booleano ou adicionar item à coleção. Se o próximo valor é independente do anterior — por exemplo, definir o filtro para “concluídas” — passe o valor diretamente.

## Microtópico 5 — Formulário controlado mantém uma fonte clara

Em um campo controlado, value vem do estado e onChange atualiza esse estado no evento de entrada. Atualize de forma síncrona no handler; se o valor fornecido ao campo não acompanhar a digitação, React volta a mostrar o valor antigo. Associe um label ao input e indique o tipo e as instruções necessários.

```jsx
const [title, setTitle] = useState("");

<form onSubmit={handleSubmit}>
  <label htmlFor="task-title">Nova tarefa</label>
  <input
    id="task-title"
    value={title}
    onChange={(event) => setTitle(event.target.value)}
  />
  <button type="submit">Adicionar</button>
</form>
```

O formulário deve tratar submit no onSubmit para aceitar clique no botão e envio pelo teclado. Use preventDefault quando o navegador não deve navegar/recarregar a página. Valide o conteúdo antes de adicionar, apresente mensagens compreensíveis e limpe o campo depois de uma operação bem-sucedida, se esse for o comportamento desejado. Geração de ID acontece uma vez no handler de criação ou na camada de dados, nunca em cada renderização.

Há casos para campos não controlados, mas nesta unidade o controle por estado deixa explícita a sincronização entre dado e tela. Não guarde como estado uma string que pode ser derivada trivialmente de outras fontes sem necessidade.

