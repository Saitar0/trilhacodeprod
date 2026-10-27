---
arquivo_id: "f9-42-2-90-integracao-p02-pratica"
parent_key: "42.2"
tipo_arquivo: "practice"
assuntos: ["01_celery_tarefas_fora_requisicao", "02_pytest_fixtures_integracao", "03_poetry_dependencias_distribuicao"]
ordem: 2
itens_origem: ["P02"]
---


### Atividade 2 — Revise retry, teste e dependências
**Contexto:** uma tarefa Celery envia uma cobrança a um provedor. O provedor recebe a requisição, mas a conexão cai antes da resposta. A tarefa faz retry; um teste existente substitui o provedor por mock. O projeto tem `pyproject.toml`, mas a equipe não sabe se o lockfile está versionado.

**Instruções:** identifique o risco de duplicar cobrança e proponha uma chave idempotente/consulta ao provedor; diga o que o teste com mock cobre e o que não cobre; proponha um teste de integração seguro em sandbox; indique qual arquivo revisar e qual ação assegura instalação reproduzível no CI. Se for biblioteca e não aplicativo, explique como muda o papel do lockfile para consumidores.

**Entrega:** nota de revisão com risco, mitigação, dois níveis de teste, evidência esperada e tratamento do lockfile.

**Dica gradual:** a ausência de resposta não revela se a cobrança ocorreu. O mock valida a decisão local do código; não valida protocolo, credencial, configuração ou comportamento real do provedor.

