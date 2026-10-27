---
arquivo_id: "f3-8-1-02-unions-narrowing-kp01-gabarito-union"
parent_key: "8.1"
tipo_arquivo: "answer_key_pratica"
assunto: "02_unions_narrowing"
ordem: 1
itens_origem: ["P1"]
---

**Solução esperada:**
```ts
function formatar(id: Identificador): string {
  if (typeof id === "string") {
    return id.toUpperCase();
  }
  return id.toFixed(0);
}
```

