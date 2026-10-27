---
arquivo_id: "f3-6-3-01-declaracoes-arrow-retorno-kp01-gabarito-retorno-objeto"
parent_key: "6.3"
tipo_arquivo: "answer_key_pratica"
assunto: "01_declaracoes_arrow_retorno"
ordem: 1
itens_origem: ["P1"]
---

**Solução comentada:** `const dobrar = valor => valor * 2;` usa corpo de expressão e retorna implicitamente. `const criarTarefa = titulo => ({ titulo });` usa parênteses para que as chaves sejam interpretadas como literal do objeto; a propriedade shorthand `titulo` usa o valor do parâmetro de mesmo nome. Nas versões iniciais, a primeira descarta o resultado da expressão dentro do bloco e a segunda interpreta `titulo:` como rótulo de instrução, sem devolver objeto.

**Erro comum:** remover chaves de um corpo com várias instruções sem revisar o fluxo, ou presumir que qualquer bloco de arrow function retorna a última expressão.

