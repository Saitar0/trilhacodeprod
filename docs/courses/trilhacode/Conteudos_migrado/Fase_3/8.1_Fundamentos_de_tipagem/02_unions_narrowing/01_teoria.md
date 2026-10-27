---
arquivo_id: "f3-8-1-02-unions-narrowing-01-teoria"
parent_key: "8.1"
tipo_arquivo: "theory"
assunto: "02_unions_narrowing"
ordem: 2
itens_origem: ["3. Unions e narrowing"]
---

### 3. Unions e narrowing
Uma union representa um valor que pode pertencer a mais de um tipo, como `string | number`. Antes de usar uma operação disponível somente em uma alternativa, faça uma checagem que permita ao TypeScript estreitar (narrow) o tipo naquele fluxo.

```ts
type Identificador = string | number;

function exibirId(id: Identificador): string {
  if (typeof id === "string") {
    return id.toUpperCase();
  }
  return id.toFixed(0);
}
```

Dentro do primeiro ramo, `id` é reconhecido como texto; no segundo, como número. Verificações como `typeof`, comparações com `null` e checagem de propriedades podem estreitar tipos. A union não significa que toda operação será aceita: fora dos ramos, só use propriedades e operações válidas para todas as alternativas.

**Erro comum:** chamar `toUpperCase()` diretamente em `string | number`. Faça a verificação primeiro; evitar a asserção de tipo indiscriminada deixa o código e sua condição de segurança explícitos.

