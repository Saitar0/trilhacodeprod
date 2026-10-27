---
arquivo_id: "f9-40-2-03-offsets-retencao-replay-p02-pratica"
parent_key: "40.2"
tipo_arquivo: "practice"
assunto: "03_offsets_retencao_replay"
ordem: 2
itens_origem: ["P02"]
---


### Atividade 2 — Analisar commit, replay e retenção
Use este fluxo: o consumer lê o offset 25, grava uma cobrança no sistema externo e depois commita o offset. Simule conceitualmente uma queda (a) antes da gravação; (b) depois da gravação e antes do commit; (c) após o commit. Para cada caso, preveja retomar/repetir/pular, proponha uma chave de idempotência e explique o que muda se o registro já tiver expirado da retenção.

**Entrega:** linha do tempo dos três casos, regra para deduplicar a cobrança e uma política de retenção/replay coerente com a janela de recuperação desejada.

**Critérios de aceite:** distingue posição de consumo de efeito no banco; reconhece a duplicação potencial em (b); não propõe commit antecipado como solução completa; relaciona o período de replay à retenção configurada.

