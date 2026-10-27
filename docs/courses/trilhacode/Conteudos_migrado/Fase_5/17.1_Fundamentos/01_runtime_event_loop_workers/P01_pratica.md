---
arquivo_id: "f5-17-1-01-runtime-event-loop-workers-p01-pratica"
parent_key: "17.1"
tipo_arquivo: "practice"
assunto: "01_runtime_event_loop_workers"
ordem: 1
itens_origem: ["P1"]
---

## Práticas

### Atividade 1 — Classificar caminhos de execução
Para cada operação, indique se tende a aguardar I/O, usar o thread principal para computação síncrona ou exige análise adicional: consulta assíncrona ao banco; cálculo síncrono longo em um array; leitura de arquivo pela API assíncrona; compressão com API assíncrona; interpretação síncrona de um JSON muito grande. Desenhe uma linha do tempo simples mostrando onde o event loop pode atender outra tarefa. Proponha uma ação para reduzir o risco da operação mais custosa.

**Dica:** não classifique apenas pela palavra “assíncrono”. Pergunte qual API foi chamada, que parte executa JavaScript e quanto trabalho síncrono ocorre por callback.

