---
arquivo_id: "f3-6-3-01-declaracoes-arrow-retorno-01-teoria"
parent_key: "6.3"
tipo_arquivo: "theory"
assunto: "01_declaracoes_arrow_retorno"
ordem: 1
itens_origem: ["Declarações modernas e escopo", "Arrow functions e retorno"]
---

## Teoria

### Declarações modernas e escopo
`let` e `const` têm escopo de bloco e tornam a intenção mais clara que `var`, cujo escopo é de função e comportamento de hoisting costuma surpreender iniciantes. Prefira `const` quando a associação não será reatribuída; use `let` quando for. Trocar `var` por `let`/`const` exige observar se o código depende do alcance da variável fora do bloco em que foi criada; não é uma substituição puramente mecânica.

### Arrow functions e retorno
Uma **arrow function** é uma forma concisa de criar função. Uma expressão pode retornar implicitamente; com corpo em bloco `{}`, use `return` explícito. Para retornar um literal de objeto com retorno implícito, envolva o objeto entre parênteses: `const criar = titulo => ({ titulo });`. Sem os parênteses, as chaves são interpretadas como corpo da função.

Arrow functions não criam seu próprio `this`, `arguments` ou contexto de construtor como funções tradicionais. Elas são úteis em callbacks que não dependem de `this` próprio; não as substitua mecanicamente em métodos de objeto ou funções construtoras.

