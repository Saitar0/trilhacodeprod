---
arquivo_id: "f6-25-1-02-jsx-transformacao-01-teoria-md"
parent_key: "25.1"
tipo_arquivo: "theory"
assunto: "02_jsx_transformacao"
ordem: 2
itens_origem: ["## Microtópico 3 — JSX é sintaxe para descrever elementos"]
---

## Microtópico 3 — JSX é sintaxe para descrever elementos

JSX permite escrever uma estrutura semelhante a marcação dentro de JavaScript. As ferramentas de build transformam JSX para que o runtime React possa usá-lo; o navegador não recebe JSX como HTML puro. A sintaxe é parecida com HTML, mas segue regras próprias:

- Retorne uma única expressão que envolva a descrição; use um elemento pai ou fragmento quando houver irmãos.
- Feche tags e escreva elementos vazios com fechamento, como img ou input.
- Use convenções JavaScript para alguns atributos, como className.
- Insira valores ou expressões JavaScript entre chaves.
- Passe uma expressão de componente com letra maiúscula; texto literal pode ser escrito diretamente entre elementos.

```jsx
function Greeting({ name }) {
  return (
    <>
      <h1>Olá, {name}</h1>
      <img className="avatar" src="/avatar.png" alt="" />
    </>
  );
}
```

O fragmento reúne elementos sem adicionar um nó de contêiner à estrutura HTML. Aspas representam texto literal em atributos; chaves permitem valores e expressões. Se um título contém caracteres especiais como & ou <, escreva-o como texto vindo de uma prop: React o trata como texto e escapa conteúdo para a saída em vez de interpretar a entrada como JSX.

