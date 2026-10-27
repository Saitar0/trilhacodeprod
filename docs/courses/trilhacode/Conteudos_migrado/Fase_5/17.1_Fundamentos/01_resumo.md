---
arquivo_id: "f5-17-1-01-resumo"
parent_key: "17.1"
tipo_arquivo: "resumo"
ordem: 0
itens_origem: ["Resumo"]
---

## Resumo
- Node combina JavaScript no thread principal com APIs de I/O e workers internos; o caminho depende da API.
- I/O assíncrono permite concorrência; JavaScript síncrono longo bloqueia o event loop.
- async/await organiza Promises, mas não cria paralelismo.
- worker_threads são opção para CPU-bound medido; streams e backpressure controlam o volume de dados em trânsito.
- pipeline ajuda a compor etapas e propagar erros; CSV deve ser processado por parser consciente do formato.
- package.json e a configuração ESM/CommonJS tornam execução e scripts explícitos.

