---
arquivo_id: "f5-17-1-03-streams-backpressure-csv-01-teoria"
parent_key: "17.1"
tipo_arquivo: "theory"
assunto: "03_streams_backpressure_csv"
ordem: 3
itens_origem: ["5. Streams e backpressure"]
---

### 5. Streams e backpressure
Uma stream representa dados que chegam ou são produzidos em partes. Streams legíveis, graváveis e de transformação podem ser encadeadas. Esse padrão evita manter o arquivo inteiro em memória. Quando a parte consumidora fica mais lenta que a produtora, backpressure regula o fluxo para limitar o buffer em trânsito; ignorá-la pode fazer a memória crescer.

A função pipeline conecta as etapas e ajuda a propagar erros e conclusão; a API de Promises de node:stream permite aguardá-la com await. Uma cópia em fluxo transfere bytes, mas não valida nem interpreta CSV. Ler chunks não equivale a receber linhas ou registros completos: uma linha pode atravessar dois chunks. CSV também permite aspas, delimitadores dentro de campos e quebras de linha em campos citados; use parser adequado em modo stream em vez de dividir ingenuamente por vírgula ou quebra de linha. [Node.js — Streams](https://nodejs.org/api/stream.html).

