---
arquivo_id: "f3-8-1-03-inferencia-contratos-forma-objetos-01-teoria"
parent_key: "8.1"
tipo_arquivo: "theory"
assunto: "03_inferencia_contratos_forma_objetos"
ordem: 3
itens_origem: ["2. Inferência e contratos explícitos", "4. Aliases, interfaces e forma dos objetos"]
---

### 2. Inferência e contratos explícitos
Muitas vezes o TypeScript infere o tipo a partir do valor inicial ou do contexto. Se `const total = 12`, o compilador sabe que `total` é um número sem precisar repetir `: number`. Prefira inferência quando a intenção estiver evidente; anote parâmetros e contratos públicos quando isso ajudar a leitura ou quando a inferência não puder determinar o tipo.

```ts
const quantidade = 3; // inferido como number
const saudacao = (nome: string) => "Olá, " + nome;
// retorno inferido como string
```

Uma variável inicializada como `let estado = "aberto"` pode receber um tipo mais estreito do que `string`, de acordo com o contexto e as atribuições. Quando a intenção é aceitar várias alternativas, declare-as claramente em vez de depender de uma atribuição inicial ambígua.

**Erro comum:** anotar absolutamente toda variável ou, no extremo oposto, deixar parâmetros públicos sem tipo. Escolha anotações que clarificam o contrato; deixe a inferência cuidar do que já está claro.

### 4. Aliases, interfaces e forma dos objetos
Um `type alias` dá um nome a um tipo, seja primitivo, union ou estrutura de objeto. Uma `interface` nomeia principalmente a forma de um objeto e pode ser estendida; declarações compatíveis com o mesmo nome podem ser mescladas. Para muitos objetos simples, ambos podem descrever a mesma forma. Use alias quando precisar nomear uma union, e escolha interface ou alias de objeto conforme a intenção e convenção do projeto.

```ts
type StatusTarefa = "aberta" | "em-andamento" | "concluida";

interface Tarefa {
  id: number;
  titulo: string;
  status: StatusTarefa;
  descricao?: string;
}
```

O `?` indica que uma propriedade pode não existir. Ao lê-la, trate a ausência, por exemplo com `tarefa.descricao ?? "Sem descrição"`. A compatibilidade de objetos é estrutural: importa se o valor tem os campos requeridos com tipos compatíveis, não se foi criado usando exatamente o nome da interface.

**Erro comum:** achar que o nome da interface cria uma classe ou existe em tempo de execução. Interfaces e anotações são parte da checagem estática; não substituem objetos reais nem validação de dados externos.

