---
arquivo_id: "f5-17-1-03-streams-backpressure-csv-03-gabarito-quiz"
parent_key: "17.1"
tipo_arquivo: "answer_key"
assunto: "03_streams_backpressure_csv"
ordem: 3
itens_origem: ["Q4", "Q5"]
---

**Resposta:** porque as etapas trabalham com partes dos dados, e backpressure pode limitar os buffers entre produtor e consumidor.  
   **Feedback:** o benefício depende de não acumular os chunks em uma coleção ou string gigante depois.

**Resposta:** um campo entre aspas pode conter vírgulas ou quebras de linha, e um registro pode estar dividido entre chunks; a divisão simples pode corromper a interpretação.  
   **Feedback:** use parser CSV que aceite streams e trate encoding, aspas, erros e limites de registro.

