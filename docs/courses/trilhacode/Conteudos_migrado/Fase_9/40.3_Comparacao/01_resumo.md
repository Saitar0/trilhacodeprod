---
arquivo_id: "f9-40-3-01-resumo"
parent_key: "40.3"
tipo_arquivo: "resumo"
ordem: 0
itens_origem: ["Resumo"]
---


## Resumo
- Escolha pelo padrão de uso: fila de trabalho, log retido ou publicação/assinatura.
- Ack, commit e efeito de negócio são pontos distintos; duplicatas devem ser tratadas explicitamente.
- Ordem tem escopo e custo: partição, fila/grupo ou ordering key; replay depende de retenção e progresso do consumidor.
- Compare operação total e drivers de custo com tráfego/região reais, registrando limites e hipótese de validação.

