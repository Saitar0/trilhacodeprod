---
arquivo_id: "f3-6-3-04-spread-rest-copia-rasa-p02-pratica-independente-copia"
parent_key: "6.3"
tipo_arquivo: "practice"
assunto: "04_spread_rest_copia_rasa"
ordem: 2
itens_origem: ["P2"]
---

### 2. Independente — detecte compartilhamento em uma cópia
Considere:

```js
const original = { titulo: "Aula", meta: { concluida: false } };
const copia = { ...original };
copia.titulo = "Revisão";
copia.meta.concluida = true;
```

Antes de executar, preveja os valores de `original.titulo`, `original.meta.concluida`, `copia.titulo` e `copia.meta.concluida`. Depois explique qual alteração ficou isolada e qual foi compartilhada. Proponha uma cópia que também separe `meta` para este objeto conhecido e raso.

**Dicas graduais:** (1) spread cria outro objeto externo; (2) confira se `meta` também foi recriada; (3) copie explicitamente `meta` ao compor o novo objeto.

