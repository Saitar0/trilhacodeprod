---
arquivo_id: "f5-19-1-04-migrations-sql-explicito-01-teoria"
parent_key: "19.1"
tipo_arquivo: "theory"
assunto: "04_migrations_sql_explicito"
ordem: 4
itens_origem: ["Microtópico 4 — Migrations e SQL explícito"]
---

## Microtópico 4 — Migrations e SQL explícito
Migrations registram mudanças do schema como uma sequência revisável e reproduzível. Gere ou escreva a migration, examine o SQL/DDL, aplique em banco de desenvolvimento e confira o estado resultante. Mantenha a migration junto ao código e verifique se uma base vazia consegue chegar ao schema esperado. A estratégia de produção deve usar o fluxo indicado pelo ORM; não trate sincronização automática de schema como substituta de migrations em um ambiente com dados.

A API do ORM costuma ser apropriada para CRUD e consultas comuns. Se ela não expressa bem uma operação ou medições justificam outra forma, use QueryBuilder ou SQL explícito e parametrizado. Vincule valores como parâmetros, nunca concatene entrada não confiável no texto SQL. Parâmetros representam valores, não nomes de tabela ou coluna; identificadores dinâmicos exigem uma lista permitida controlada.

**Exemplo:** uma agregação específica pode ficar mais clara em SQL. Compare o resultado e o plano com a consulta do ORM, documente por que a alternativa foi escolhida e preserve parâmetros vinculados.

**Erro comum:** presumir que uma consulta escrita em API tipada é automaticamente eficiente, ou que SQL bruto é automaticamente mais rápido. Ambos precisam ser medidos e revisados.

**Checagem:** que evidências deixam uma migration confiável? Histórico versionado, SQL revisado, aplicação reproduzível e verificação do schema resultante.

