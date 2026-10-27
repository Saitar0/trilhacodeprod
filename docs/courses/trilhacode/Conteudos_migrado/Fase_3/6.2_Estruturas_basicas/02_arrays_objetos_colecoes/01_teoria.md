---
arquivo_id: "f3-6-2-02-arrays-objetos-colecoes-01-teoria"
parent_key: "6.2"
tipo_arquivo: "theory"
assunto: "02_arrays_objetos_colecoes"
ordem: 2
itens_origem: ["Arrays, objetos e coleção de entidades"]
---

### Arrays, objetos e coleção de entidades
Um **array** é uma sequência ordenada de valores acessada por índice, começando em zero. Um **objeto** reúne propriedades nomeadas, útil para representar uma entidade com campos relacionados. Escolha array para coleção ordenada e objeto para descrever uma coisa; uma lista de entidades costuma ser um array de objetos.

```js
const tarefa = { id: 1, titulo: "Revisar aula", ativa: true };
const tarefas = [tarefa, { id: 2, titulo: "Publicar", ativa: false }];
```

