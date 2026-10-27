---
arquivo_id: "f6-31-5-m02-fatia-regra-tipo-md"
parent_key: "31.5"
tipo_arquivo: "milestone"
ordem: 2
itens_origem: ["M02"]
titulo_marco: "Marco 2 — Implemente a fatia vertical e a regra do tipo"
---

### Marco 2 — Implemente a fatia vertical e a regra do tipo
**Objetivo:** demonstrar a tarefa principal em React/TypeScript ligado ao ambiente de teste real da API.

**Tarefas comuns:**
1. Configure a origem da API por ambiente e documente valores fictícios; não inclua segredo no bundle cliente.
2. Implemente apenas a tela e a ação necessárias à regra escolhida, com fronteira HTTP identificável e tratamento tipado das respostas externas.
3. Torne reproduzíveis carregamento, erro, vazio, sucesso e recuperação/retry quando seguro. Informe quais estados usam mock e qual fluxo alcança o servidor real.
4. Preserve teclado, foco, labels e mensagens compreensíveis no caminho principal.

**Tarefas específicas, conforme o tipo:**
- **T1:** prevenir duplo envio e comunicar claramente resultado/falha; não reenviar automaticamente uma escrita sem proteção idempotente.
- **T2:** apresentar as ações adequadas ao papel e proteger rotas na experiência; manter cada autorização também na API e descrever a evidência de isolamento do backend.
- **T4:** incluir filtros e paginação na chave de consulta e manter resultados/página coerentes; obter baseline de lista antes de decidir se virtualizar.
- **T5:** exibir estado do job separado de resultado vazio e erro; ligar filtros/paginação aos dados reais do relatório.

**Evidências:** código e fluxo executável; uma chamada observada na API de teste; demonstração dos estados; registro da regra específica e de como é reproduzida.

**Verificação:** execute o caminho feliz com a API real e provoque os demais estados de modo controlado. Confira que configuração não expõe segredo e que uma resposta externa inválida ou inesperada não vira sucesso silencioso.


