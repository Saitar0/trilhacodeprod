---
arquivo_id: "f9-43-1-90-integracao-p02-pratica"
parent_key: "43.1"
tipo_arquivo: "practice"
assuntos: ["02_ciclo_requisicao_laravel", "03_filas_decisao_stack"]
ordem: 2
itens_origem: ["P02"]
---


### Atividade 2 — Revisão de risco em Eloquent e fila
**Contexto:** um endpoint lista 100 pedidos e cada item exibe o nome do cliente. O código busca o cliente dentro do loop. Ao criar um pedido, a aplicação despacha `SendReceipt`; o job envia o recibo e cai antes de registrar sucesso, levando a retry.

**Instruções:** identifique o possível N+1 e sugira como investigar/evitar consultas repetidas; diga que evidência usar para validar a consulta; explique o risco de o recibo ser enviado duas vezes e proponha chave idempotente ou deduplicação. Para um sistema que atende apenas leitura, descreva como verificaria que a policy e o escopo impedem acesso a pedido de outra conta.

**Entrega:** nota de revisão com três riscos, mudanças propostas e critérios de aceite observáveis. Não é necessário executar aplicação Laravel.

**Dica:** relacione previamente a relação Eloquent, compare número de consultas da listagem, e trate `job enviado` e `job confirmado no worker` como eventos diferentes.

