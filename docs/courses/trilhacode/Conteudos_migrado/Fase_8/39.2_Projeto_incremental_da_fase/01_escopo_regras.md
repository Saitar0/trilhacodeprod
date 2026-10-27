---
arquivo_id: "f8-39-2-01-escopo-regras-md"
parent_key: "39.2"
tipo_arquivo: "project_scope"
ordem: 0
itens_origem: ["Escopo e regras"]
---

## Escopo e regras

- Continue o mesmo projeto do Trilho A; não crie um novo projeto nem substitua o Projeto de Fase do Trilho B (39.3).
- Parta do deploy e da infraestrutura como código existentes. Esta etapa integra e verifica o trabalho de 32.2, 36.1, 38.1, 38.2 e 39.1; não é necessário reconstruir toda a pipeline ou reimplementar fases anteriores.
- Use ambiente local ou de teste/staging. Não injete falha, tráfego artificial ou carga de teste em produção, nem use dados reais de pessoas.
- Planeje custos e limite recursos de laboratório. Ao terminar, confirme o estado dos recursos e destrua os recursos temporários conforme o procedimento da Fase 7.
- Segredos não vão para o repositório, artefatos de build, logs ou traces. Um plano/arquivo de Terraform pode carregar valores sensíveis mesmo quando uma variável é marcada como sensível; proteja esses artefatos e não os publique no Git.
- A carga indicada no cabeçalho é a estimativa global atual da unidade; este material não divide o trabalho em previsões por marco.

