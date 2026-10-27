---
arquivo_id: "f9-40-2-01-log-particionado-ordem-01-teoria"
parent_key: "40.2"
tipo_arquivo: "theory"
assunto: "01_log_particionado_ordem"
ordem: 1
itens_origem: ["### Microtópico 1 — Ler um tópico como log particionado"]
---


### Microtópico 1 — Ler um tópico como log particionado

Um **producer** grava registros em um **topic**. O topic é dividido em **partitions**; cada partition é um log ordenado de registros acrescentados ao longo do tempo. Cada registro tem um **offset** que identifica sua posição dentro daquela partição. Não existe um offset único que ordene o topic inteiro.

A ordem garantida é local à partição. Uma chave de evento consistente, processada pelo mesmo particionador e com a mesma configuração de partições, costuma encaminhar eventos relacionados à mesma partição, permitindo preservar a ordem daquele fluxo de chave. Isso não cria ordem entre chaves diferentes. Alterar o número de partições pode mudar o destino de futuras mensagens de uma chave e exige cuidado se a ordem por chave for requisito.

Partições são também a unidade de distribuição e paralelismo para consumo em grupo. Mais partições podem permitir mais leitura paralela, mas aumentam o custo operacional, a distribuição de armazenamento e as decisões de ordenação. Não escolha um número alto sem considerar o fluxo, a taxa, a retenção e as necessidades de ordenação.

