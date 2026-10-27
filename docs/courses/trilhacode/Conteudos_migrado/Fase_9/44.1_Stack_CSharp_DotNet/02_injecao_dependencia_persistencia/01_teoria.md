---
arquivo_id: "f9-44-1-02-injecao-dependencia-persistencia-01-teoria"
parent_key: "44.1"
tipo_arquivo: "theory"
assunto: "02_injecao_dependencia_persistencia"
ordem: 2
itens_origem: ["### 2. Injeção de dependência e persistência"]
---


### 2. Injeção de dependência e persistência
ASP.NET Core tem container de injeção de dependências. Três ciclos comuns:
- **Transient:** instância nova a cada resolução;
- **Scoped:** instância compartilhada dentro do escopo, normalmente uma requisição web;
- **Singleton:** uma instância durante a vida da aplicação, potencialmente usada por várias requisições.

Não capture um serviço scoped, como `DbContext`, dentro de um singleton: o serviço mais curto passa a ser retido por tempo maior e pode quebrar escopo de dados ou segurança concorrente. Um singleton com estado compartilhado também precisa ser thread-safe. Configure e valide os ciclos de vida deliberadamente.

**EF Core** mapeia modelos via `DbContext`, usa LINQ e oferece migrations para registrar mudanças de schema. Migrations geradas precisam de revisão: uma propriedade renomeada pode ser interpretada como excluir uma coluna e criar outra, perdendo dados. Para produção, escolha estratégia de deployment, credenciais de migração, revisão de SQL/script ou bundle e plano de rollback; não entregue alterações de banco a cada réplica da aplicação ao iniciar sem avaliar o risco.

**Dapper** é um micro-ORM sobre ADO.NET que executa SQL e mapeia resultados para objetos. A consulta permanece explícita; use parâmetros, não concatene entrada do usuário. EF Core e Dapper podem coexistir em partes diferentes do sistema. Escolha pelo tipo de consulta, manutenção e necessidade de controle, não por um ranking geral.

