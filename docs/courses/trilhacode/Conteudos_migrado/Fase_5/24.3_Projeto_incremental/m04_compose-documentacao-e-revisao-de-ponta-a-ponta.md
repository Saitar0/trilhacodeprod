---
arquivo_id: "f5-24-3-m04-compose-documentacao-e-revisao-de-ponta-a-ponta"
parent_key: "24.3"
tipo_arquivo: "milestone"
ordem: 4
itens_origem: ["M4"]
titulo_marco: "Marco 4 — Compose, documentação e revisão de ponta a ponta"
---

### Marco 4 — Compose, documentação e revisão de ponta a ponta
**Objetivo:** tornar a entrega fácil de executar e revisar do zero.

**Tarefas:** inclua Dockerfile da API e integre API, PostgreSQL e Redis usado pela aplicação ao Compose local; configure health/readiness e ordem por condição de saúde quando necessário. Mantenha segredo em variável local ignorada pelo Git e forneça `.env.example` sem valores sensíveis. Documente inicialização, migrations, seed sintético, testes, rotas, erros conhecidos e limpeza do ambiente.

**Evidência:** README, arquivos Docker/Compose, `.env.example`, logs de inicialização e resultados dos testes executados no ambiente documentado.

**Dica:** faça o ensaio final como ambiente novo: remova somente os volumes descartáveis deste projeto, aplique migrations desde zero e siga as instruções sem comandos implícitos que existam apenas na sua máquina.

