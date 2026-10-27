---
arquivo_id: "f4-16-2-01-projeto-incremental-m03-marco-03"
parent_key: "16.2"
tipo_arquivo: "milestone"
assunto: "01_projeto_incremental"
ordem: 3
itens_origem: ["M3"]
titulo_marco: "Marco 3 — Medir e adicionar cache Redis"
---

### Marco 3 — Medir e adicionar cache Redis
**Entrega:** medição de referência da consulta, implementação cache-aside da leitura escolhida e nova medição sob condições documentadas.

Selecione uma leitura repetida que possa ser reconstruída a partir do PostgreSQL. Antes do cache, anote consulta, dados, ambiente e método de medição. Depois, use uma chave que represente todos os parâmetros que alteram a resposta e defina TTL coerente com a tolerância a desatualização. Em uma escrita, invalide a cópia após a confirmação na fonte. A aplicação deve tratar miss, hit, falha do cache e ausência de resultado de modo explícito.

Compare resultados com repetições e descreva como as medições foram feitas. Registre latência e leituras à origem; inclua hits/misses se instrumentados. Não misture a inicialização dos serviços com o tempo da consulta, nem conclua ganho universal a partir de uma única execução. Uma melhoria não é obrigatória: se a medição indicar que o cache não compensa, documente isso e apresente a implementação apenas como experimento controlado, ou justifique a decisão de não mantê-lo.

**Evidências sugeridas:** tabela de medições, trecho de código, logs ou roteiro que demonstre hit/miss e invalidação.

