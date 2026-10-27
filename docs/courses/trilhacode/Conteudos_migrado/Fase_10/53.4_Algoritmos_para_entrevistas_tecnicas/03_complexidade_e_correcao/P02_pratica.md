---
arquivo_id: "f10-53-4-p02"
parent_key: "53.4"
tipo_arquivo: "practice"
assunto: "03_complexidade_e_correcao"
ordem: 2
itens_origem: ["P02"]
---


### Atividade 2 — Maior soma em intervalo contíguo (independente)
**Contexto e objetivo:** resolver um caso em que a solução quadrática simples pode ser substituída por uma varredura linear.

**Dados iniciais:** lista não vazia `[-2, 3, -1, 4, -5]`. Encontre a maior soma de um intervalo contíguo e retorne também os índices inicial e final. Para este exemplo, uma resposta válida é soma `6`, intervalo de índice `1` a `3` (`[3, -1, 4]`).

**Instruções:** primeiro descreva a força bruta que calcula cada intervalo e seu custo. Em seguida, proponha uma varredura que mantém a melhor soma de intervalo terminando na posição atual e a melhor soma global. Defina como desempatar se vários intervalos tiverem a mesma soma. Teste também lista de um elemento negativo e lista com todos os números negativos.

**Entrega:** pseudocódigo/implementação, breve justificativa da propriedade mantida, resultado e índices dos testes, complexidades e regra de desempate.

**Dica gradual:** ao chegar ao próximo número, compare começar um novo intervalo ali ou estender o intervalo anterior. Não inicialize a melhor soma em zero se a tarefa exige intervalo não vazio e todos os valores podem ser negativos.

