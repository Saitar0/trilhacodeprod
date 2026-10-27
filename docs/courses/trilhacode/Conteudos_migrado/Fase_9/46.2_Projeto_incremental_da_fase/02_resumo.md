---
arquivo_id: "f9-46-2-02-resumo"
parent_key: "46.2"
tipo_arquivo: "resumo"
ordem: 0
itens_origem: ["Resumo"]
---


## Resumo
- O projeto avança em quatro marcos: contrato/ambiente, publicação, consumo resiliente e serviço adicional/operação.
- Outbox protege a fronteira banco/publicação; publisher confirm protege a confirmação do broker ao produtor. Podem ocorrer duplicatas.
- Ack manual após o efeito persistido, com idempotência, trata redelivery sem duplicar a regra de negócio.
- Retry deve ser limitado; DLQ exige diagnóstico e redrive controlado.
- Serviço adicional precisa justificar seu boundary; comparação de stack deve apoiar-se em evidências do projeto.

