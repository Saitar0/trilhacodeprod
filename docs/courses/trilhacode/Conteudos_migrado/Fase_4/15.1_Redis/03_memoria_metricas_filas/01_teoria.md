---
arquivo_id: "f4-15-1-03-memoria-metricas-filas-01-teoria"
parent_key: "15.1"
tipo_arquivo: "theory"
assunto: "03_memoria_metricas_filas"
ordem: 3
itens_origem: ["4. Memória, métricas e filas"]
---

### 4. Memória, métricas e filas
Acompanhe latência, taxa de acerto (hits / (hits + misses)), volume de leituras na origem, erros e memória usada. Uma taxa alta isoladamente não prova benefício: compare latência e carga antes e depois, com tráfego e dados comparáveis. Redis pode remover chaves quando atinge o limite de memória, conforme a política de eviction configurada; um cache deve tolerar que uma chave desapareça e reconstruí-la a partir da fonte. [Redis — políticas de eviction](https://redis.io/docs/latest/develop/reference/eviction/).

Listas permitem operações de inserção e remoção nas extremidades e podem compor filas simples. Um `push` seguido de `pop`, por si só, não resolve confirmação de processamento, recuperação após falha ou repetição segura. Redis Streams oferece grupos de consumidores, mensagens pendentes e confirmação explícita com `XACK`, mas ainda é preciso planejar retentativas, mensagens problemáticas, retenção e idempotência da tarefa. Não prometa entrega exatamente uma vez quando a aplicação pode receber ou executar uma mensagem novamente. [Redis — Streams e grupos de consumidores](https://redis.io/docs/latest/develop/data-types/streams/).

