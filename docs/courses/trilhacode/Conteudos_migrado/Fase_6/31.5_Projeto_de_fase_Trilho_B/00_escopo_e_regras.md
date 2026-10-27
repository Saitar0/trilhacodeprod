---
arquivo_id: "f6-31-5-00-escopo-e-regras-md"
parent_key: "31.5"
tipo_arquivo: "project_scope"
ordem: 0
itens_origem: ["Teoria", "Regras de conclusão"]
---

## Teoria
Consulte a cobertura atual, a disponibilidade e a regra de prioridade do [Guia de Projetos e Rotação](../../../Guia_Projetos_e_Rotacao_de_Tipos.md). Na Fase 6, as opções são T1, T2, T4 e T5. Gere três opções elegíveis, priorizando tipos pendentes; uma repetição é opcional e não gera novo crédito de cobertura. Registre as opções consultadas, a escolha e a justificativa.

O projeto é uma fatia vertical mínima sobre API real e autenticação produzidas na Fase 5. Não crie backend fictício, banco novo ou produto completo. Mocks podem reproduzir estados e falhas, mas não comprovam integração real. A autorização continua sob responsabilidade do servidor; esconder um botão na interface não protege uma operação.

**Regra central por tipo:**
- **T1 — Venda de ingressos:** checkout conectado à API, estados compreensíveis e proteção contra envio duplicado conforme o contrato. Uma falha não pode ser apresentada como compra concluída; repetição de escrita exige mecanismo seguro, como idempotência quando disponível.
- **T2 — Agendamento multiempresa:** experiência por papel e rotas protegidas, com autorização validada no backend. O teste da interface demonstra redirecionamento e affordances; não substitui evidência de isolamento entre empresas na API.
- **T4 — Catálogo e busca:** paginação e filtros com TanStack Query, chave de consulta que inclui todos os parâmetros relevantes e estado coerente ao trocar de página. A virtualização só é aceita como decisão medida, com comparação reproduzível antes/depois.
- **T5 — Importador e relatório:** relatório filtrável e paginado que consome status/dados do job da API. Diferencie processamento em andamento, falha, resultado vazio e sucesso com dados.

## Regras de conclusão
- Não há quiz genérico: a avaliação ocorre nos quatro marcos, nas evidências e na rubrica.
- T2 não é aprovado como isolamento multiempresa apenas com controles no frontend ou testes de componente.
- T4 não recebe crédito por virtualização sem medida comparável; se não houver ganho, documentar a decisão de não adotar.
- Nenhuma repetição conta como novo tipo concluído no guia.

