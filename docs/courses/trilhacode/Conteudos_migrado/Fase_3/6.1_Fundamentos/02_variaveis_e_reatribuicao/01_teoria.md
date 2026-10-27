---
arquivo_id: "f3-6-1-02-variaveis-e-reatribuicao-01-teoria"
parent_key: "6.1"
tipo_arquivo: "theory"
assunto: "02_variaveis_e_reatribuicao"
ordem: 2
itens_origem: ["Variáveis e reatribuição"]
---

### Variáveis e reatribuição
Use `const` por padrão quando a associação não será reatribuída; use `let` quando o valor associado precisar mudar, como um acumulador. `const` não torna um objeto imutável: suas propriedades ainda podem mudar. Escolha nomes que expliquem o papel do valor e mantenha variáveis próximas ao trecho que as usa.

```js
const nome = "Lia";
let tentativas = 0;
tentativas = tentativas + 1;
```

