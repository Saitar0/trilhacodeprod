---
arquivo_id: "f4-9-2-03-normalizacao-esquema-revisao-01-teoria"
parent_key: "9.2"
tipo_arquivo: "theory"
assunto: "03_normalizacao_esquema_revisao"
ordem: 3
itens_origem: ["4. Normalize para reduzir anomalias", "5. Passe do modelo conceitual ao esquema e revise"]
---

### 4. Normalize para reduzir anomalias
Use a normalização para organizar fatos e reduzir problemas de inclusão, atualização e exclusão. Na 1FN, cada coluna armazena um valor do domínio por linha, sem grupos repetidos ou listas de valores que precisariam ser tratados individualmente. Uma lista de produtos em uma única coluna dificulta consultar, validar e atualizar cada produto.

Na 2FN, a tabela já está na 1FN e cada atributo não-chave depende da chave candidata inteira, não apenas de uma parte dela. Isso importa principalmente quando uma chave candidata tem mais de uma coluna. Se uma linha de item de pedido é identificada por (pedido_id, produto_id), o nome do produto depende apenas de produto_id e deve ficar associado ao Produto, não ser repetido como fato independente em cada item.

Na 3FN, a tabela está na 2FN e atributos não-chave não dependem transitivamente da chave por meio de outro atributo não-chave. Se cada cliente tem um CEP e o CEP determina uma cidade, repetir a cidade em cada pedido pode criar divergências. A decomposição precisa preservar os fatos e as relações, e não apenas multiplicar tabelas.

**Exemplo de anomalias:** guardar cliente, pedido e itens em uma única tabela pode repetir o endereço em várias linhas. Alterar só algumas linhas produz inconsistência; apagar o último pedido pode apagar também a única cópia dos dados do cliente.

**Erro comum:** decorar “1FN, 2FN e 3FN” sem declarar a chave e explicar de quais dependências os atributos dependem. A forma normal deve ser avaliada a partir das regras do domínio.

### 5. Passe do modelo conceitual ao esquema e revise
Um diagrama ER comunica entidades, relações, cardinalidades e participação. O esquema relacional concretiza essa visão em tabelas, colunas, PKs, FKs, restrições e tipos. Faça a conversão relação por relação e confira se os atributos da associação ficaram na tabela associativa. Depois valide o modelo com exemplos de dados e consultas que o sistema precisa responder.

Normalizar não significa otimizar tudo para leitura nem eliminar qualquer repetição legítima. Primeiro preserve as regras e a integridade; só considere desnormalização quando uma necessidade de leitura estiver identificada, medida e acompanhada de uma estratégia para manter os dados consistentes. O DDL implementa escolhas físicas no SGBD, mas não substitui a justificativa do modelo.

**Checklist de revisão:**
- Cada atributo está no conceito ou relação a que pertence?
- As chaves representam identidade e preservam unicidade do domínio?
- Os mínimos e máximos de cada relação foram declarados?
- Uma relação N:N foi resolvida por uma associação com atributos próprios?
- As dependências justificam as formas normais alegadas?
- Exemplos e consultas esperadas funcionam com o esquema proposto?

