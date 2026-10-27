---
arquivo_id: "f5-18-2-03-idempotencia-em-retries-kp03-gabarito-pratica"
parent_key: "18.2"
tipo_arquivo: "answer_key_pratica"
assunto: "03_idempotencia_em_retries"
ordem: 3
itens_origem: ["P3"]
---

**Solução de referência:** guardar chave no escopo do cliente/operação com impressão digital do payload; impor unicidade e transicionar estado/resultado de modo atômico com o pedido no banco. A repetição igual retorna o resultado registrado; payload diferente recebe erro documentado; uma chamada concorrente espera o resultado ou recebe resposta temporária/conflictiva conforme o contrato e pode tentar novamente. Para o provedor externo, encaminhar chave idempotente equivalente ou usar outbox/fluxo durável; declarar o que a retenção permite após expiração.

