---
arquivo_id: "f5-17-1-03-streams-backpressure-csv-p02-pratica"
parent_key: "17.1"
tipo_arquivo: "practice"
assunto: "03_streams_backpressure_csv"
ordem: 2
itens_origem: ["P2"]
---

### Atividade 2 — Processar arquivo grande com stream
Implemente um programa que leia um arquivo de texto grande por stream, conte linhas sem guardar o arquivo completo e reporte erros de leitura. Defina o comportamento para arquivo vazio, linha final sem quebra de linha e finais de linha CRLF. Registre como verificou o resultado com um arquivo pequeno conhecido e como confirmou que a solução não acumula todo o conteúdo.

**Dica:** o byte LF pode ser contado mesmo quando chunks terminam em qualquer ponto; acrescente uma última linha somente se houver conteúdo após a última quebra. Para CSV real, use parser em stream e confira seus registros com um arquivo de exemplo pequeno.

