---
arquivo_id: "f5-23-2-03-medicao-e-decisao-de-desempenho-01-teoria"
parent_key: "23.2"
tipo_arquivo: "theory"
assunto: "03_medicao_e_decisao_de_desempenho"
ordem: 3
itens_origem: ["Microtópico 4 — Decida, meça e preserve clareza"]
---

## Microtópico 4 — Decida, meça e preserve clareza

A escolha útil equilibra correção, custo esperado, memória, legibilidade e esforço de manutenção. Documente hipótese de volume e operações que motivaram a estrutura; se mudarem, reavalie. Não otimize uma estimativa abstrata sem verificar se essa etapa é de fato relevante para a aplicação.

Quando houver dúvida de desempenho, primeiro estabeleça uma referência reproduzível: mesma entrada, resultado correto, ambiente comparável e operação cronometrada bem definida. Para comparar busca repetida, separe preparação da estrutura das consultas e declare se construção do índice faz parte do cenário. Medir uma única execução pequena pode refletir ruído, aquecimento do runtime ou custo de preparação.

Uma melhoria local não resolve automaticamente gargalo de rede, banco, serialização ou limite de memória. Faça o algoritmo manter os mesmos resultados e invariantes; uma estrutura mais rápida que altera ordem, igualdade, duplicatas ou tratamento de ausência pode introduzir defeitos.

