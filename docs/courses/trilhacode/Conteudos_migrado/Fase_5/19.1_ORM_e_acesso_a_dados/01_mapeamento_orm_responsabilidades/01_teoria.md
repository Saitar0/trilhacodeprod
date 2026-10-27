---
arquivo_id: "f5-19-1-01-mapeamento-orm-responsabilidades-01-teoria"
parent_key: "19.1"
tipo_arquivo: "theory"
assunto: "01_mapeamento_orm_responsabilidades"
ordem: 1
itens_origem: ["Microtópico 1 — Mapeamento e responsabilidades"]
---

## Microtópico 1 — Mapeamento e responsabilidades
Um ORM relaciona modelos da aplicação a tabelas, colunas, chaves e relações. O cliente do ORM fornece operações de leitura e escrita; o banco continua responsável por persistência, restrições, índices, concorrência e execução das consultas. Tipos gerados ajudam a detectar alguns erros durante o desenvolvimento, mas não provam que o modelo representa corretamente as regras do domínio nem substituem validações e constraints no banco.

Escolha um ORM para o projeto e siga seu modelo de uso. Prisma define modelos em schema próprio e gera um cliente; TypeORM mapeia entidades e oferece repositórios e QueryBuilder. Os conceitos desta aula se aplicam a ambos, mas exemplos de API e comandos são específicos da ferramenta e da versão escolhidas.

**Exemplo:** uma entidade Pedido pode ter relação muitos-para-um com Cliente. A aplicação navega pela relação, mas a integridade deve ser garantida por uma chave estrangeira no banco. Uma regra como “número do pedido é único por cliente” deve ter constraint adequada, mesmo que a aplicação também verifique antes de inserir.

**Erro comum:** tratar o objeto retornado pelo ORM como se fosse o próprio banco. O objeto é uma representação da aplicação; transações concorrentes ou outro cliente podem alterar os dados depois da leitura.

**Checagem:** onde deve existir a garantia de unicidade quando ela precisa valer para todos os escritores? No banco, por meio de constraint, além de eventual validação amigável na aplicação.

