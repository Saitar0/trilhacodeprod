---
arquivo_id: "f5-17-1-01-runtime-event-loop-workers-kp01-gabarito-pratica"
parent_key: "17.1"
tipo_arquivo: "answer_key_pratica"
assunto: "01_runtime_event_loop_workers"
ordem: 1
itens_origem: ["P1"]
---

**Solução de referência:** consulta de banco não bloqueia o thread principal se o cliente usa I/O não bloqueante; cálculo síncrono e interpretação síncrona ocupam o thread principal enquanto rodam; APIs de arquivo e compressão assíncronas podem usar o pool conforme a API. Para o custo alto, medir primeiro e considerar otimização, limites de tamanho, streaming quando aplicável ou worker thread para computação CPU-bound.

