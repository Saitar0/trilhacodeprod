---
arquivo_id: "f3-6-3-90-integracao-p03-pratica-transferencia-refatoracao"
parent_key: "6.3"
tipo_arquivo: "practice"
assuntos: ["01_declaracoes_arrow_retorno", "02_template_strings", "03_destructuring", "04_spread_rest_copia_rasa"]
ordem: 3
itens_origem: ["P3"]
---

### 3. Transferência — refatore sem alterar o comportamento
Refatore o trecho legado abaixo. Use `const`/`let`, arrow functions onde forem adequadas, template string, destructuring e spread/rest. Preserve os textos e valores produzidos.

```js
var tarefa = { id: 12, titulo: "Estudar", ativa: true, meta: { categoria: "JS" } };

function descrever(item) {
  return "Tarefa " + item.id + ": " + item.titulo;
}

function atualizar(item, novoTitulo) {
  var copia = Object.assign({}, item);
  copia.titulo = novoTitulo;
  return copia;
}

function separarId(item) {
  var id = item.id;
  var titulo = item.titulo;
  return { id: id, titulo: titulo };
}
```

**Entregue:** código refatorado, saída de `descrever(tarefa)`, comparação da tarefa original antes/depois de `atualizar`, resultado de `separarId` e uma nota sobre a propriedade aninhada `meta`. Crie também um helper `semId(item)` que use rest para reunir e devolver as propriedades restantes; para `tarefa`, o resultado contém `titulo`, `ativa` e `meta`. Não converta mecanicamente funções que precisem de `this` próprio.

**Dicas graduais:** (1) `descrever` pode usar retorno de expressão; (2) o novo objeto pode ser criado com spread e sobrescrita de `titulo`; (3) em `separarId`, extraia `id` e `titulo` e reúna o resto; (4) uma cópia rasa ainda compartilha `meta`.

