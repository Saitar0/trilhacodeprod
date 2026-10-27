---
arquivo_id: "f9-40-2-90-integracao-p01-pratica"
parent_key: "40.2"
tipo_arquivo: "practice"
assuntos: ["01_log_particionado_ordem", "02_grupos_particoes_consumidores"]
ordem: 1
itens_origem: ["P01"]
---


### Atividade 1 — Distribuir partições e prever ordenação
Um tópico `orders` tem partições P0, P1 e P2. Para este exercício, considere que o grupo `billing` tem membros C1 e C2, com atribuição C1 → P0/P1 e C2 → P2. O grupo independente `analytics` tem membro A1 com P0/P1/P2. Eventos com chave `customer-A` são gravados em P1 com offsets 10 e 11; eventos de `customer-B` são gravados em P2 com offsets 4 e 5.

Desenhe quais membros leem cada registro em cada grupo. Depois adicione C3 ao grupo `billing` e explique o limite de paralelismo; por fim adicione C4 e indique o que pode acontecer. Identifique em quais sequências existe ordem observável e por quê.

**Entrega:** tabela grupo/membro/partição/registros e duas conclusões: alcance de ordem e efeito de adicionar consumers.

**Critérios de aceite:** os dois grupos leem de forma independente; C1/C2 dividem partições apenas no grupo `billing`; a ordem dos offsets 10→11 e 4→5 é local a cada partição; um membro a mais que partições não cria partição nova.

