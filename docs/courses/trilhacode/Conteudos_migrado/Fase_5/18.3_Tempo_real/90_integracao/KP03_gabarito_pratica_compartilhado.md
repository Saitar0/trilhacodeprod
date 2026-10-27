---
arquivo_id: "f5-18-3-90-integracao-kp03-gabarito-pratica-compartilhado"
parent_key: "18.3"
tipo_arquivo: "answer_key_pratica"
assuntos: ["02_eventos_ordem_e_retomada", "03_seguranca_de_canais", "04_estado_compartilhado_e_concorrencia"]
ordem: 3
itens_origem: ["P3"]
---

**Solução de referência:** reconexão não altera autorização; evento repetido é ignorado ou aplicado idempotentemente; quando o cursor está retido, o servidor continua a partir dele; quando não está, o cliente recupera snapshot atual e ressincroniza. Para edição concorrente, a versão detecta base obsoleta e exige releitura ou resolução explícita. O teste registra que a garantia é pelo menos recuperação dentro da retenção, não entrega exatamente uma vez.

