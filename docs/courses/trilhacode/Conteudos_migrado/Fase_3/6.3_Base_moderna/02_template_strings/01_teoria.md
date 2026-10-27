---
arquivo_id: "f3-6-3-02-template-strings-01-teoria"
parent_key: "6.3"
tipo_arquivo: "theory"
assunto: "02_template_strings"
ordem: 2
itens_origem: ["Template strings"]
---

### Template strings
Template strings usam crases e `${...}` para interpolar expressões e compor texto em várias linhas. A expressão é avaliada e convertida para texto; interpolar um objeto diretamente pode exibir uma representação pouco útil, então escolha a propriedade que comunica o dado desejado.

```js
const mensagem = `Tarefa: ${tarefa.titulo}`;
```

