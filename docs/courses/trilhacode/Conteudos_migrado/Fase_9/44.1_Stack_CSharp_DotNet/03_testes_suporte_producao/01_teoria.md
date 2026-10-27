---
arquivo_id: "f9-44-1-03-testes-suporte-producao-01-teoria"
parent_key: "44.1"
tipo_arquivo: "theory"
assunto: "03_testes_suporte_producao"
ordem: 3
itens_origem: ["### 3. Testes, suporte e produção"]
---


### 3. Testes, suporte e produção
xUnit é uma opção comum de testes em .NET. Testes unitários cobrem lógica isolada; integração cobre colaboração real entre API, banco, provider ou autenticação quando essa fronteira importa. Mockar `DbContext` não comprova que uma migration funciona no provider relacional de produção; use banco/provider de teste apropriado para esse risco. Registre qual comportamento cada teste demonstra.

Versão do runtime importa. Em **15/10/2026**, o .NET 10 está em suporte LTS até 15/11/2028. Os ciclos de suporte oficiais indicam encerramento de .NET 8 LTS e .NET 9 em 11/11/2026; planeje novo conteúdo e projetos com a matriz vigente, sem confundir .NET moderno com .NET Framework legado. Atualize esta nota antes da produção efetiva do curso.

**Se esta for a stack escolhida:** reclassifique a unidade como obrigatória/média; estude C#, SDK e NuGet; implemente API com validação, DI, EF Core/migration revisada, teste unitário e integração, deploy sandbox e consulta Dapper apenas se houver razão documentada. Fixe versão suportada e provedores compatíveis.

