---
arquivo_id: "f4-9-3-90-integracao-kp02-gabarito-pratica"
parent_key: "9.3"
tipo_arquivo: "answer_key_pratica"
assuntos: ["01_constraints_de_coluna", "02_integridade_referencial_e_exclusao"]
ordem: 2
itens_origem: ["P2"]
---

**Solução de referência:** ItemPedido pode usar PK composta (pedido_id, produto_id), FKs obrigatórias para Pedido e Produto e CHECK (quantidade >= 1). Essa chave impede o mesmo produto repetido no mesmo pedido; se repetição por linha for permitida, use item_id e numero_linha único por pedido. Se linhas não têm sentido sem seu pedido, ON DELETE CASCADE pode ser adequado para rascunhos ou para exclusão lógica do agregado conforme a política. Para pedidos confirmados, a política do domínio deve impedir exclusão física ou preservar/anonimizar o cliente sem apagar o histórico. Não se deve escolher CASCADE entre Cliente e Pedido confirmado sem revisar a obrigação de retenção. Inserir quantidade 0 viola CHECK; repetir a combinação viola PK/UNIQUE; referenciar pedido inexistente viola FK.

