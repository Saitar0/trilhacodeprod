---
arquivo_id: "f3-6-1-90-integracao-kp01-gabarito-pratica-guiada-acumulador"
parent_key: "6.1"
tipo_arquivo: "answer_key_pratica"
assuntos: ["02_variaveis_e_reatribuicao", "03_operadores_e_conversao", "04_decisoes_e_repeticoes"]
ordem: 1
itens_origem: ["P1"]
---

**Solução comentada:** os índices válidos são `0`, `1` e `2`. Com `<=`, o laço também acessa `valores[3]`, que é `undefined`; somar esse valor ao total produz `NaN`. Troque `<=` por `<`. Para o array vazio, não há valores para somar e a média não deve ser calculada dividindo por zero; trate a lista antes e informe “sem valores” ou adote uma regra explícita, em vez de inventar média zero sem decisão.

**Erro comum:** corrigir o limite do laço e esquecer o caso vazio; ou assumir que `undefined` é ignorado na soma.

