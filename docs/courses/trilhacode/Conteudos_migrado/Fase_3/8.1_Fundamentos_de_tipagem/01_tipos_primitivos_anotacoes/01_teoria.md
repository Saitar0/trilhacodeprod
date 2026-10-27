---
arquivo_id: "f3-8-1-01-tipos-primitivos-anotacoes-01-teoria"
parent_key: "8.1"
tipo_arquivo: "theory"
assunto: "01_tipos_primitivos_anotacoes"
ordem: 1
itens_origem: ["1. Tipos primitivos e anotações"]
---

## Teoria

### 1. Tipos primitivos e anotações
TypeScript acrescenta verificação estática de tipos ao JavaScript. Um tipo descreve quais valores e operações o compilador aceita em determinado ponto do programa. Para valores primitivos, use `string`, `number` e `boolean` em minúsculas; `String` e `Number` nomeiam objetos wrapper e normalmente não são os tipos desejados. Arrays podem ser escritos, por exemplo, como `string[]`.

Uma anotação explícita comunica um contrato:

```ts
let nome: string = "Lia";
let tentativas: number = 0;
const nomes: string[] = ["Lia", "Caio"];
```

O compilador usa essas informações para apontar usos incompatíveis durante a checagem. As anotações de tipo não transformam os valores nem validam automaticamente dados recebidos de usuário, arquivo ou API em tempo de execução.

**Erro comum:** supor que declarar `nome: string` converte um número em texto. A anotação só descreve o valor esperado e permite ao verificador encontrar incompatibilidades.

