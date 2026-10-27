---
arquivo_id: "f9-40-2-01-resumo"
parent_key: "40.2"
tipo_arquivo: "resumo"
ordem: 0
itens_origem: ["Resumo"]
---


## Resumo
- Topic contém partições; cada partição tem sua própria ordem e offsets.
- Chave consistente pode manter eventos relacionados na mesma partição, mas não cria ordem global entre partições.
- Um consumer group divide partições entre membros; partições disponíveis limitam o paralelismo ativo daquele grupo.
- Grupos diferentes leem o mesmo tópico de forma independente, cada um com seu progresso.
- Commit de offset não torna atômico o efeito em um sistema externo; replay pode repetir efeitos.
- Retenção é independente do ack/commit do consumer; replay só funciona enquanto os dados ainda estiverem disponíveis.

