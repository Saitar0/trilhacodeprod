---
arquivo_id: "f4-12-3-01-modelo-vendas-historico-01-teoria"
parent_key: "12.3"
tipo_arquivo: "theory"
assunto: "01_modelo_vendas_historico"
ordem: 1
itens_origem: ["1. Transforme regras de venda em entidades e relações", "2. Preserve o histórico comercial e defina chaves"]
---

## Teoria

### 1. Transforme regras de venda em entidades e relações
Comece registrando as regras e os casos que o sistema precisa representar. Um modelo de referência pode ter Cliente, Produto ou Variante, Pedido, ItemPedido, TentativaPagamento, Estoque e MovimentoEstoque. Esse conjunto é uma hipótese inicial; requisitos determinam o modelo final.

Uma relação comum é: um Cliente pode ter zero ou muitos Pedidos; cada Pedido pertence a um Cliente. Um Pedido contém linhas de itens; cada ItemPedido pertence a um Pedido e aponta para um Produto/Variante. Um Pedido pode ter várias tentativas de pagamento. Cada regra deve indicar mínimo e máximo, além de quando o registro passa a existir: por exemplo, um pedido em rascunho pode ainda não ter itens, enquanto um pedido confirmado precisa ter ao menos um.

Documente decisões e perguntas abertas: o produto vendido é uma variante? É permitido repetir o mesmo produto em duas linhas? Um pedido pode ser dividido em mais de uma moeda? Existem pagamentos parciais? Essas respostas afetam chaves, cardinalidade e relatórios.

**Erro comum:** começar pelas tabelas sem distinguir regras obrigatórias, estados temporários e decisões que ainda precisam ser respondidas.

### 2. Preserve o histórico comercial e defina chaves
O preço atual do catálogo pode mudar; o preço acordado no momento da compra precisa ser guardado no ItemPedido. Também registre quantidade e, conforme o domínio, descrição/SKU de venda como snapshot para recibos e auditoria. Use tipo numérico adequado para valores monetários e declare a moeda; não use ponto flutuante para valores que exigem precisão decimal.

Uma linha pode ser identificada por (pedido_id, numero_linha), o que permite o mesmo produto em linhas diferentes. Se a regra proibir repetição de produto por pedido, uma constraint UNIQUE(pedido_id, produto_id) pode expressar isso. Não escolha a chave composta automaticamente sem conferir a regra do negócio.

Tentativas de pagamento precisam de identificador local e estado. Uma chave de idempotência fornecida ao provedor pode ser registrada com o provedor e protegida por unicidade local, para evitar processar a mesma solicitação mais de uma vez dentro do sistema. Isso não substitui o mecanismo de idempotência do provedor nem reconciliação de resultados incertos. Nunca armazene número completo ou código de segurança de cartão neste modelo.

**Erro comum:** recalcular o histórico com o preço atual ou assumir que um id gerado impede duplicidade de negócio.

