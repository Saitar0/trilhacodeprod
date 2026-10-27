---
arquivo_id: "f5-17-1-03-streams-backpressure-csv-kp02-gabarito-pratica"
parent_key: "17.1"
tipo_arquivo: "answer_key_pratica"
assunto: "03_streams_backpressure_csv"
ordem: 2
itens_origem: ["P2"]
---

**Solução de referência:** abrir uma stream de leitura e percorrer os chunks mantendo apenas o contador, se houve algum byte e o último byte; somar cada byte LF encontrado; ao final, somar uma linha se o arquivo não for vazio e o último byte não for LF. Usar tratamento de erro ou pipeline com uma etapa de transformação e destino de contagem. CRLF conta como uma quebra porque o par contém LF; uma linha final sem terminador conta uma vez.

