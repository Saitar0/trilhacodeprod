---
arquivo_id: "f3-7-2-01-modulos-exportacoes-01-teoria"
parent_key: "7.2"
tipo_arquivo: "theory"
assunto: "01_modulos_exportacoes"
ordem: 1
itens_origem: ["1. Módulo, escopo e interface", "2. Exportações e imports"]
---

## Teoria

### 1. Módulo, escopo e interface
Um módulo ECMAScript (ESM) é um arquivo que pode expor parte de seu trabalho por `export` e consumir declarações de outros arquivos por `import`. As exportações formam a interface pública: quem usa o módulo conhece o que ele oferece, sem depender dos detalhes internos. Declarações de um módulo têm escopo próprio; importar uma função não a transforma em variável global.

```js
// tarefas.js
export function filtrarAtivas(tarefas) {
  return tarefas.filter((tarefa) => tarefa.ativa);
}

// app.js
import { filtrarAtivas } from "./tarefas.js";
```

**Erro comum:** esperar que uma função exportada fique automaticamente disponível em todos os arquivos. Cada consumidor precisa importá-la explicitamente.

### 2. Exportações e imports
Uma exportação nomeada associa um nome à declaração. O import nomeado usa chaves e precisa corresponder ao nome exportado:

```js
// formatos.js
export function formatarNome(nome) {
  return nome.trim();
}

// perfil.js
import { formatarNome } from "./formatos.js";
```

O caminho identifica o módulo de origem; `./` significa “a partir da pasta deste arquivo”. No navegador, sem um import map, use um caminho relativo ou URL resolvível, normalmente com a extensão, como `./formatos.js`. Também existe `export default`, importado sem chaves. Nesta unidade, priorize exportações nomeadas para deixar evidente o nome consumido nos dois arquivos.

**Erro comum:** renomear uma exportação sem atualizar seu import. Confira o nome e o caminho quando o carregamento falhar.

