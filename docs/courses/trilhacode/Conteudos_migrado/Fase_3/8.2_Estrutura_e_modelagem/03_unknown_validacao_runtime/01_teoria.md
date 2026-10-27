---
arquivo_id: "f3-8-2-03-unknown-validacao-runtime-01-teoria"
parent_key: "8.2"
tipo_arquivo: "theory"
assunto: "03_unknown_validacao_runtime"
ordem: 3
itens_origem: ["4. unknown e validação em runtime"]
---

### 4. unknown e validação em runtime
TypeScript remove os tipos ao gerar JavaScript. Portanto, o tipo estático `Produto` não verifica JSON recebido em runtime. Comece dados externos como `unknown`, confira sua forma e só então os aceite como dados do domínio. `unknown` exige verificações antes do uso; `any` permite quase qualquer operação sem essa proteção.

```ts
function ehProduto(valor: unknown): valor is Produto {
  if (typeof valor !== "object" || valor === null) return false;

  const candidato = valor as {
    id?: unknown;
    nome?: unknown;
    preco?: unknown;
  };

  return typeof candidato.id === "number"
    && typeof candidato.nome === "string"
    && typeof candidato.preco === "number";
}
```

A asserção que dá forma a `candidato` não valida o valor por si só: as verificações `typeof` são que conferem os campos. Em um sistema real, defina também regras de domínio, como preço não negativo.

**Erro comum:** confiar em `resposta.json() as Produto`. JSON sintaticamente válido ainda pode conter campos ausentes ou tipos errados.

