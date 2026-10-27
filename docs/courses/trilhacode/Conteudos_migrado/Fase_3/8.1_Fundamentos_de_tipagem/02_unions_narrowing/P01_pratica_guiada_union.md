---
arquivo_id: "f3-8-1-02-unions-narrowing-p01-pratica-guiada-union"
parent_key: "8.1"
tipo_arquivo: "practice"
assunto: "02_unions_narrowing"
ordem: 1
itens_origem: ["P1"]
---

## Práticas

### 1. Guiada — corrija operações inválidas numa union
Analise o código:

```ts
type Identificador = string | number;

function formatar(id: Identificador): string {
  return id.toUpperCase();
}
```

O verificador aponta que `toUpperCase` não existe para todos os valores aceitos. Altere a função para formatar texto em maiúsculas e números como texto sem casas decimais.

**Dica:** use `typeof id === "string"` e trate o outro ramo como número.

