---
arquivo_id: "f3-6-3-04-spread-rest-copia-rasa-01-teoria"
parent_key: "6.3"
tipo_arquivo: "theory"
assunto: "04_spread_rest_copia_rasa"
ordem: 4
itens_origem: ["Spread e rest"]
---

### Spread e rest
**Spread** (`...`) expande elementos ou propriedades em uma nova composição. **Rest** usa a mesma notação para reunir os itens restantes em um array ou objeto; a posição e o contexto determinam qual papel está sendo usado.

Em objetos e arrays, spread faz cópia rasa: a estrutura externa é nova, mas objetos aninhados continuam compartilhados. Alterar uma propriedade primitiva de topo na cópia não muda a origem; alterar uma propriedade de um objeto interno compartilhado pode mudar os dois. Faça cópia de níveis aninhados explicitamente quando precisar separá-los, e não use spread como sinônimo de imutabilidade.

```js
const tarefa = { id: 7, titulo: "Estudar", ativa: true };
const { titulo, ...dadosRestantes } = tarefa;
const atualizar = (item, patch) => ({ ...item, ...patch });
const mensagem = `Tarefa: ${titulo}`;
```

Use esses recursos quando deixarem o fluxo mais claro; concisão não deve esconder transformação ou mutação.

