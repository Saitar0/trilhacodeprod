---
arquivo_id: "f9-42-3-02-convencoes-composicao-custo-01-teoria"
parent_key: "42.3"
tipo_arquivo: "theory"
assunto: "02_convencoes_composicao_custo"
ordem: 2
itens_origem: ["### 2. Convenções, composição e custo de equipe"]
---


### 2. Convenções, composição e custo de equipe
| Dimensão | FastAPI | Flask | Django + DRF |
|---|---|---|---|
| Ponto forte | Construção de API com tipos/modelos e schema OpenAPI integrados | Núcleo pequeno, simples de compor e ampliar | Estrutura de aplicação e componentes integrados/convencionados |
| Decisões da equipe | Modelos, dependências, persistência, auth, deployment e divisão do projeto | Mais decisões e extensões: dados, validação, auth, estrutura e schema | Organização de apps, modelos, settings e componentes DRF dentro das convenções |
| Pergunta de custo | A equipe domina contratos e dependências escolhidas? | Há tempo e critério para selecionar e manter extensões? | As convenções integradas atendem ao caso sem impor estrutura excessiva? |

“Microframework” não significa apenas uma aplicação de um arquivo, nem prova que Flask não possa crescer. FastAPI também não fornece automaticamente toda a aplicação de negócio. Em qualquer opção, examine maturidade e manutenção das dependências, suporte de segurança, documentação, migração de dados, logs, autenticação/autorização e deploy.

Compare uma fatia real de trabalho — validar uma entrada, persistir um registro, proteger acesso e publicar — em vez de comparar apenas o código “Hello World”. Registre também experiência da equipe, contratação, bibliotecas existentes e custo de operação.

**Checagem:** menos linhas no exemplo inicial bastam para concluir menor custo total? Não; faltam manutenção, segurança, dependências, deploy e trabalho de integração.

