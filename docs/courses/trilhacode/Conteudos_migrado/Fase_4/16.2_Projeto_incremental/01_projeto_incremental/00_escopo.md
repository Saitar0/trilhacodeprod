---
arquivo_id: "f4-16-2-01-projeto-incremental-00-escopo"
parent_key: "16.2"
tipo_arquivo: "project_scope"
assunto: "01_projeto_incremental"
ordem: 0
itens_origem: ["escopo"]
---

## Escopo e decisões
Continue o Trilho A escolhido em 3.5 (gestor de tarefas, loja virtual ou base de conhecimento). Não crie um produto novo para este projeto. PostgreSQL permanece a fonte transacional principal. Redis entra somente quando uma consulta repetida tiver um motivo demonstrável para cache. MongoDB entra somente se o domínio tiver um agregado documental e um padrão de leitura/escrita que justifiquem essa representação.

Antes de implementar, defina como cada dado é criado, lido, atualizado e removido; qual serviço é a autoridade; e como dados derivados são atualizados. Se não houver um caso documental real, registre essa conclusão e proponha uma coleção pequena e coerente com o domínio, sem duplicar todo o banco relacional por variedade. O objetivo é justificar limites e papéis, não usar tecnologias sem necessidade.

