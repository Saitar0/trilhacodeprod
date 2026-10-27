---
arquivo_id: "f6-25-1-01-componentes-modelo-declarativo-props-01-teoria-md"
parent_key: "25.1"
tipo_arquivo: "theory"
assunto: "01_componentes_modelo_declarativo_props"
ordem: 1
itens_origem: ["## Microtópico 1 — React descreve a interface a partir dos dados", "## Microtópico 2 — Componentes são funções que compõem a UI", "## Microtópico 4 — Props são entradas de leitura do componente", "## Microtópico 5 — Renderização precisa ser previsível"]
---

## Microtópico 1 — React descreve a interface a partir dos dados

Em uma interface imperativa, o código pode localizar nós do DOM e alterar texto, classes e atributos em várias partes do programa. Conforme estados e telas aumentam, fica difícil saber qual código deve prevalecer e se todas as alterações foram aplicadas.

Com React, a aplicação descreve qual interface deve aparecer para os dados atuais. Componentes expressam partes da interface; o React executa essa descrição, compara a árvore resultante com a anterior e atualiza o DOM quando necessário. Em geral, quem desenvolve declara o resultado esperado, em vez de coordenar manualmente cada alteração no DOM.

A descrição segue entradas como props e estado. Nesta primeira unidade, concentre-se em dados recebidos por props; estado e resposta a eventos serão aprofundados em 25.2. React é uma biblioteca para interfaces; não substitui por si só todas as decisões de roteamento, chamadas de rede ou organização da aplicação.

## Microtópico 2 — Componentes são funções que compõem a UI

Um componente funcional é uma função JavaScript que recebe props e retorna elementos React, normalmente escritos com JSX. Nomes de componente começam com letra maiúscula para que JSX os reconheça como componentes; nomes de elementos HTML, como article e button, começam com letra minúscula.

Componentes podem ser compostos: um componente de página pode renderizar uma lista de cartões; cada cartão apresenta um item. A extração é útil quando uma parte tem significado e responsabilidade reconhecíveis, ou quando a mesma estrutura aparece em vários dados. Não é necessário criar um componente para cada tag ou linha isolada.

```jsx
function TaskCard({ title, owner, completed }) {
  return (
    <article>
      <h2>{title}</h2>
      <p>Responsável: {owner}</p>
      <p>{completed ? "Concluída" : "Pendente"}</p>
    </article>
  );
}

function TaskList() {
  const tasks = [
    { id: 1, title: "Revisar acessibilidade", owner: "Lia", completed: false },
    { id: 2, title: "Corrigir formulário", owner: "Caio", completed: true },
  ];

  return (
    <section>
      {tasks.map((task) => (
        <TaskCard
          key={task.id}
          title={task.title}
          owner={task.owner}
          completed={task.completed}
        />
      ))}
    </section>
  );
}
```

O exemplo mostra composição e dados variados. O atributo key identifica cada item entre irmãos quando uma coleção é renderizada; ele é usado pelo React para acompanhar itens e não funciona como uma prop comum que o cartão possa ler. A unidade não exige memorizar casos complexos de reconciliação; basta manter a identidade estável dos itens.

## Microtópico 4 — Props são entradas de leitura do componente

Props são informações que um componente pai passa ao filho. Podem ser texto, números, booleanos, objetos, arrays, funções ou elementos. O componente lê esses valores e escolhe o que descrever. Props devem ser tratadas como imutáveis durante a renderização: se o filho precisa de uma entrada diferente, o pai envia novos dados; o filho não altera o objeto recebido para forçar uma atualização.

```jsx
<TaskCard title="Revisar testes" owner="João" completed={false} />
```

Nesse uso, strings são passadas entre aspas, booleanos e expressões entre chaves. No componente, desestruturar o objeto de props nos parâmetros pode tornar as entradas explícitas. O nome e o formato das props são parte do contrato entre pai e filho; prefira nomes ligados ao significado do domínio e evite uma prop genérica sem propósito.

Uma condição pode alterar a descrição para os mesmos dados, como mostrar “Concluída” quando completed é true. Isso continua sendo uma renderização baseada em dados, não uma alteração imperativa no DOM. Uma prop não é automaticamente estado interno: o filho recebe uma fotografia das entradas daquela renderização.

## Microtópico 5 — Renderização precisa ser previsível

Renderizar é executar componentes para calcular a descrição da UI. Depois, React pode confirmar alterações necessárias no DOM. Uma renderização não significa que o navegador vai recriar tudo a cada chamada. Além disso, uma renderização pode ocorrer sem que haja mudança no DOM.

Mantenha a função de renderização pura: com as mesmas props, estado e contexto, calcule a mesma descrição e não altere valores que existiam antes da chamada nem faça efeitos externos. React pode chamar uma função de componente mais de uma vez, interromper um trabalho ou repetir cálculos em desenvolvimento para revelar problemas. Por isso, não envie requisições, escreva no DOM nem incremente variável global durante a renderização.

```jsx
function TaskCard({ task }) {
  // Leia task; não altere task.title nem task.completed aqui.
  return <h2>{task.title}</h2>;
}
```

Mais tarde, eventos de usuário serão tratados fora do cálculo da renderização, e estado será atualizado pela API própria do React. Por ora, lembre a separação: props descrevem entradas, o componente calcula a UI e React decide como aplicar a descrição.

