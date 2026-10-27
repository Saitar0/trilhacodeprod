---
arquivo_id: "f10-53-4-p01"
parent_key: "53.4"
tipo_arquivo: "practice"
assuntos: ["01_entender_problema_antes_codificar", "02_estruturas_e_padroes"]
ordem: 1
itens_origem: ["P01"]
---


### Atividade 1 — Frequências e primeira duplicata (guiada)
**Contexto e objetivo:** praticar mapa hash, percurso único e explicação de complexidade.

**Dados iniciais:** entrada `[4, 2, 4, 3, 2, 4]`. Tarefa A: retornar a frequência de cada valor. Tarefa B: retornar o primeiro valor que se repete ao percorrer a lista da esquerda para a direita (neste exemplo, `4`). Se não houver repetido, retornar “nenhum”.

**Instruções:** para A, percorra a entrada e atualize um mapa `valor → frequência`. Para B, percorra novamente mantendo um conjunto de valores vistos; antes de inserir, verifique se o valor já existe. Explique por que a ordem do percurso define a resposta da tarefa B.

**Entrega:** pseudocódigo ou implementação na linguagem escolhida, mapa final `{4: 3, 2: 2, 3: 1}`, resposta B (`4`), complexidade temporal/espacial e testes adicionais para lista vazia e lista sem repetição.

**Dica gradual:** comece com o estado vazio; anote como mapa/conjunto muda em cada item. Para B, a verificação acontece antes da inserção.

