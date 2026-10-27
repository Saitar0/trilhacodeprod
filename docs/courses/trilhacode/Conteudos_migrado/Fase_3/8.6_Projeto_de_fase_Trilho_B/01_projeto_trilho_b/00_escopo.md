---
arquivo_id: "f3-8-6-01-projeto-trilho-b-00-escopo"
parent_key: "8.6"
tipo_arquivo: "project_scope"
assunto: "01_projeto_trilho_b"
ordem: 0
itens_origem: ["escopo"]
---

## Escopo e opções
O Trilho B complementa o projeto acumulado ao isolar um tipo de problema. Nesta fase, as opções são **T1 — venda de ingressos com estoque limitado**, **T2 — agendamento para várias clínicas** e **T4 — catálogo de receitas com busca e feed**. Consulte a tabela de cobertura do guia antes de escolher. Um tipo já concluído pode ser repetido, mas a repetição é opcional e não aumenta a cobertura.

A entrega usa HTML, CSS, JavaScript/TypeScript e JSON local. O projeto não inclui banco de dados nem API persistente. Construa somente a fatia mínima necessária para demonstrar a regra difícil do tipo:

- **T1:** carrinho e checkout simulados, com formulário validado e total calculado. Não alegue reserva real de estoque nem pagamento.
- **T2:** painel com clínicas e papéis simulados (administrador e atendente), mostrando ações de interface conforme o papel. Isso demonstra apresentação, não autorização ou segurança.
- **T4:** catálogo de receitas em JSON local com filtros, ordenação e paginação acessíveis. Declare os limites do conjunto local.

A versão precisa ser compreensível e terminável. Evite telas, estilos e funcionalidades laterais que não contribuam para o problema do tipo. Escreva explicitamente o que é simulado, o que não persiste e quais regras não são segurança real.

