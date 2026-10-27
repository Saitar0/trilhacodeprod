---
arquivo_id: "f9-40-2-03-offsets-retencao-replay-f03-flashcards"
parent_key: "40.2"
tipo_arquivo: "flashcards"
assunto: "03_offsets_retencao_replay"
ordem: 3
itens_origem: ["FC03"]
---


- **Commit de offset apaga a mensagem ou evita duplicar efeito no banco?** Não. Retenção controla remoção, e uma falha entre efeito externo e commit pode causar replay; use idempotência/coordenação no destino.

