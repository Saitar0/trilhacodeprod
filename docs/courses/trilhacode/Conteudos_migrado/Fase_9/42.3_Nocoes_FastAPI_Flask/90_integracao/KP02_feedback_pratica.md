---
arquivo_id: "f9-42-3-90-integracao-kp02-feedback-pratica"
parent_key: "42.3"
tipo_arquivo: "answer_key_pratica"
assuntos: ["02_convencoes_composicao_custo", "03_sync_async_operacao"]
ordem: 2
itens_origem: ["P02"]
---


**Feedback de referência:** no Flask WSGI, cada requisição continua ocupando um worker durante o ciclo; bibliotecas bloqueantes limitam o benefício; tarefas de fundo que precisam sobreviver ao fim da resposta devem ir a um worker/fila. Avalie concorrência, latência, I/O real, custo de worker e compatibilidade de extensões.

**Erro comum:** confundir concorrência de operações de I/O dentro de uma requisição com aumento automático de throughput ou execução confiável em segundo plano.

