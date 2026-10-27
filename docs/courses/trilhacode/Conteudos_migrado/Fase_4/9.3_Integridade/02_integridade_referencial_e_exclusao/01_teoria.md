---
arquivo_id: "f4-9-3-02-integridade-referencial-e-exclusao-01-teoria"
parent_key: "9.3"
tipo_arquivo: "theory"
assunto: "02_integridade_referencial_e_exclusao"
ordem: 2
itens_origem: ["3. Proteja relações e escolha o efeito de exclusão"]
---

### 3. Proteja relações e escolha o efeito de exclusão
Uma FK expressa a existência da linha referenciada. Em Pedido e ItemPedido, cada item pode exigir um pedido existente e um produto existente. Uma FK não impede, por si só, repetições na tabela filha; use UNIQUE ou uma chave composta se a regra proibir, por exemplo, duas linhas do mesmo produto no mesmo pedido.

A ação referencial define o que ocorre ao atualizar ou apagar a chave referenciada. RESTRICT ou NO ACTION impedem a operação enquanto houver dependentes (NO ACTION pode ser verificada no momento de checagem da constraint quando ela for adiável). CASCADE propaga a operação para linhas dependentes. SET NULL remove a referência e só é adequado se a relação for opcional e as colunas aceitarem NULL. SET DEFAULT usa o padrão e ainda precisa satisfazer a FK.

Escolha a ação a partir do ciclo de vida dos dados. Excluir um carrinho e suas linhas pode justificar CASCADE; apagar um cliente com pedidos fiscais pode exigir bloqueio, anonimização ou outro fluxo de domínio. A ação não é uma decisão puramente técnica.

**Erro comum:** usar CASCADE por conveniência sem desenhar a cadeia de linhas que poderá ser removida.

