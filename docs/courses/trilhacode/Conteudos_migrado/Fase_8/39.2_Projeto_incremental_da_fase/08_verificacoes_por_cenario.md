---
arquivo_id: "f8-39-2-08-verificacoes-por-cenario-md"
parent_key: "39.2"
tipo_arquivo: "project_scenarios"
ordem: 0
itens_origem: ["5 cenários"]
---

## Verificações por cenário

Use estes cenários como teste de aceite do projeto, adaptando-os ao tipo escolhido:

1. Uma publicação em teste falha no health check. A pipeline bloqueia/identifica o problema e o serviço não é declarado saudável sem evidência.
2. Uma requisição/execução do fluxo principal produz sinal com nome de serviço, versão e ambiente e não inclui token, payload ou identificador pessoal.
3. Um indicador piora após deploy. O dashboard aponta qual fluxo/rota/job foi afetado e o runbook instrui a consultar o trace/log relevante.
4. O rollback ou a mitigação é iniciada. Há verificação de dependências e dados persistentes antes da ação, e uma checagem do SLI confirma recuperação.
5. Ao final do laboratório, a pessoa consegue explicar quais recursos continuam ativos e como encerrar os temporários sem apagar recursos compartilhados ou dados necessários.

