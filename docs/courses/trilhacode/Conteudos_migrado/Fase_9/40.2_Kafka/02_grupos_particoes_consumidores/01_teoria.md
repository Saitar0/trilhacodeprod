---
arquivo_id: "f9-40-2-02-grupos-particoes-consumidores-01-teoria"
parent_key: "40.2"
tipo_arquivo: "theory"
assunto: "02_grupos_particoes_consumidores"
ordem: 2
itens_origem: ["### Microtópico 2 — Distribuir consumidores por grupos"]
---


### Microtópico 2 — Distribuir consumidores por grupos

Um **consumer group** representa uma aplicação lógica que lê um tópico. Dentro de um grupo, as partições são atribuídas aos membros para dividir o trabalho; numa atribuição normal, uma partição fica com no máximo um membro ativo daquele grupo de cada vez. Por isso, com três partições, um grupo pode ter no máximo três membros lendo partições desse tópico em paralelo. Um quarto membro não aumenta esse paralelismo e pode ficar sem partição atribuída.

Outro grupo é um leitor lógico independente: pode receber todos os registros por meio de sua própria atribuição e manter seus próprios offsets. Isso permite que, por exemplo, faturamento e análise leiam o mesmo tópico sem competir entre si. Já aumentar os membros dentro do mesmo grupo divide as partições existentes. Mudança de membros pode provocar **rebalanceamento**, quando atribuições são revistas; a aplicação deve lidar com essa transição.

O número de consumers não garante o mesmo número de tarefas simultâneas: limitações de partições, capacidade da aplicação, dependências e rebalanceamento influenciam o processamento real.

