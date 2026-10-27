---
arquivo_id: "f3-8-2-02-generics-composicao-contratos-01-teoria"
parent_key: "8.2"
tipo_arquivo: "theory"
assunto: "02_generics_composicao_contratos"
ordem: 2
itens_origem: ["3. Generics preservam relações", "5. Composição de contratos"]
---

### 3. Generics preservam relações
Um generic permite criar uma operação reutilizável que mantém uma relação entre o tipo de entrada e o resultado. Em `primeiro<T>(itens: T[]): T | undefined`, uma coleção de `Produto` resulta em `Produto | undefined`; uma de strings resulta em `string | undefined`.

```ts
function primeiro<T>(itens: T[]): T | undefined {
  return itens[0];
}

const codigo = primeiro([10, 20]); // number | undefined
const nome = primeiro(["Lia", "Caio"]); // string | undefined
```

Use um parâmetro de tipo quando ele conecta posições do contrato. Uma restrição, como `T extends { id: number }`, expressa uma capacidade necessária sem perder o tipo concreto de `T`.

**Erro comum:** adicionar `<T>` sem preservar nenhuma relação entre entrada, saída ou propriedades. A abstração só ajuda se comunica algo útil.

### 5. Composição de contratos
Tipos compostos podem reutilizar contratos sem duplicar cada alternativa. `Resultado<T>` descreve sucesso e erro para operações diferentes, preservando o tipo concreto dos dados no ramo de sucesso. Não crie uma camada genérica antes que exista uma relação real para representar.

```ts
function buscarProduto(id: number): Resultado<Produto> {
  // implementação omitida
  return { estado: "erro", mensagem: "Não encontrado" };
}
```

O discriminante `estado` distingue os casos; `T` conecta os dados de sucesso ao produto procurado. O compilador ajuda a conferir essa estrutura no código, enquanto dados externos ainda precisam de validação.

