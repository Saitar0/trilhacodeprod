---
arquivo_id: "f3-6-2-01-funcoes-retorno-responsabilidade-kp01-gabarito-retorno"
parent_key: "6.2"
tipo_arquivo: "answer_key_pratica"
assunto: "01_funcoes_retorno_responsabilidade"
ordem: 1
itens_origem: ["P1"]
---

**Solução comentada:** substitua `console.log(total)` por `return total`. Assim, `resultado` recebe `11`; a segunda chamada de `console.log` exibe `retorno: 11`. `total` foi declarada dentro da função e seu nome só existe naquele escopo. A função pode devolver o valor calculado sem expor a variável local.

**Erro comum:** achar que `console.log(total)` faz a função retornar `total`; `console.log` tem o efeito de exibir, mas não entrega esse resultado ao chamador.

