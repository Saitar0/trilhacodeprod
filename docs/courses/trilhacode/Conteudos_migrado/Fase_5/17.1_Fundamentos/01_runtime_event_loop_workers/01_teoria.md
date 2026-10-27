---
arquivo_id: "f5-17-1-01-runtime-event-loop-workers-01-teoria"
parent_key: "17.1"
tipo_arquivo: "theory"
assunto: "01_runtime_event_loop_workers"
ordem: 1
itens_origem: ["theory-container", "1. Runtime Node.js e responsabilidades", "2. Event loop e concorrência de I/O", "4. CPU-bound, I/O e workers"]
---

## Teoria

### 1. Runtime Node.js e responsabilidades
Node.js é um runtime JavaScript construído sobre V8 e componentes como libuv. Em uma execução comum, o código JavaScript roda no thread principal. O runtime integra APIs do sistema operacional e um pool de workers para determinadas operações; por isso, uma chamada assíncrona não significa que todo o trabalho foi transferido a um thread separado. Operações de rede frequentemente usam I/O não bloqueante do sistema; operações de arquivo assíncronas e algumas tarefas custosas podem usar o pool. O comportamento depende da API usada. [Node.js — visão geral de blocking e non-blocking](https://nodejs.org/learn/asynchronous-work/overview-of-blocking-vs-non-blocking).

### 2. Event loop e concorrência de I/O
O event loop coordena callbacks JavaScript e a conclusão de operações assíncronas. Enquanto uma requisição aguarda I/O não bloqueante, o processo pode avançar trabalho de outras requisições. Isso permite concorrência de I/O com poucos threads JavaScript; não significa que várias funções JavaScript síncronas rodem em paralelo no thread principal.

Uma função síncrona longa, um laço custoso ou uma expressão regular problemática pode ocupar o event loop e atrasar outras tarefas. Mantenha pequeno o trabalho síncrono de cada callback e meça a latência sob cargas representativas. O event loop tem fases e regras de agendamento; esta unidade usa o modelo para raciocinar sobre espera e bloqueio sem exigir memorizar cada fase. [Node.js — event loop](https://nodejs.org/learn/asynchronous-work/event-loop-timers-and-nexttick) e [não bloquear o event loop](https://nodejs.org/en/learn/asynchronous-work/dont-block-the-event-loop).

### 4. CPU-bound, I/O e workers
Uma transformação CPU-bound grande — por exemplo, comprimir ou processar matematicamente um conjunto extenso em JavaScript síncrono — bloqueia o thread principal. Primeiro meça e identifique o custo. Para trabalho que realmente precisa de paralelismo, worker_threads permite executar JavaScript em threads separados; há custo de inicialização, comunicação e memória, então workers não são solução automática. Workers ajudam em tarefas CPU-intensive e em geral não são necessários para I/O que as APIs assíncronas do Node já tratam eficientemente. [Node.js — Worker threads](https://nodejs.org/api/worker_threads.html).

