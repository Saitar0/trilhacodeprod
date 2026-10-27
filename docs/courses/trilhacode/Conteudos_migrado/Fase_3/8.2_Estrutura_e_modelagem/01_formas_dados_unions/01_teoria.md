---
arquivo_id: "f3-8-2-01-formas-dados-unions-01-teoria"
parent_key: "8.2"
tipo_arquivo: "theory"
assunto: "01_formas_dados_unions"
ordem: 1
itens_origem: ["1. Formas de dados e ausência", "2. Unions discriminadas e narrowing"]
---

## Teoria

### 1. Formas de dados e ausência
Uma interface ou alias de objeto descreve propriedades e seus tipos. Uma propriedade opcional pode não existir; um campo que aceita `null` existe, mas pode conter esse valor. Com `strictNullChecks`, trate explicitamente as possibilidades.

```ts
interface Produto {
  id: number;
  nome: string;
  preco: number;
  descricao?: string;
}

function rotulo(produto: Produto): string {
  return produto.descricao ?? produto.nome;
}
```

`?` não cria valor padrão nem garante presença em runtime. Modele apenas os campos que o contrato realmente permite.

**Erro comum:** usar `as Produto` para eliminar um aviso de campo opcional. A asserção não cria o campo nem comprova que o dado o contém.

### 2. Unions discriminadas e narrowing
Quando um valor pode representar alternativas com dados diferentes, modele cada alternativa como objeto e use um campo literal comum para distingui-las. A checagem desse discriminante estreita a union e permite acessar os campos daquela forma.

```ts
type Resultado<T> =
  | { estado: "sucesso"; dados: T }
  | { estado: "erro"; mensagem: string };

function descrever<T>(resultado: Resultado<T>): string {
  if (resultado.estado === "sucesso") {
    return "Dados recebidos";
  }
  return resultado.mensagem;
}
```

Antes da checagem, não é seguro acessar `mensagem` ou `dados`: cada campo pertence a uma alternativa. Esse padrão evita combinações contraditórias de propriedades opcionais.

**Erro comum:** representar carregamento, sucesso e erro por campos opcionais independentes, permitindo um estado de erro sem mensagem.

