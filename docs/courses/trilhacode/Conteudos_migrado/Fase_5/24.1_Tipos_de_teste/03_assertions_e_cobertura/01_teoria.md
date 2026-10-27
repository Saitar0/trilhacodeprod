---
arquivo_id: "f5-24-1-03-assertions-e-cobertura-01-teoria"
parent_key: "24.1"
tipo_arquivo: "theory"
assunto: "03_assertions_e_cobertura"
ordem: 3
itens_origem: ["Microtópico 5 — Asserções e cobertura medem coisas diferentes"]
---

## Microtópico 5 — Asserções e cobertura medem coisas diferentes

Uma boa asserção descreve um comportamento relevante: valor retornado, erro apropriado, estado persistido, resposta HTTP ou ausência de efeito colateral. Um teste que executa código sem verificar algo importante pode aumentar a cobertura sem aumentar a confiança. Casos normais e de falha devem corresponder a riscos e regras explícitas, não a uma meta de quantidade de testes.

Cobertura de linhas/statement informa quais instruções foram executadas; cobertura de branches informa se caminhos de decisão foram percorridos; métricas de funções também podem estar disponíveis. Nenhuma garante que a asserção esteja correta, que a regra relevante foi incluída ou que o sistema funcione no ambiente real. 100% de cobertura não é prova de ausência de defeitos.

Use o relatório para encontrar código importante sem teste e escolher a próxima pergunta a cobrir. Uma linha pode ser executada apenas no caminho feliz; a condição de erro nunca foi testada. Uma mutação conceitual ajuda a avaliar o teste: se o resultado da regra fosse invertido ou uma condição removida, alguma asserção falharia? Se nada falhasse, o teste talvez esteja apenas executando o código. A métrica é sinal para investigação, não troféu isolado.

