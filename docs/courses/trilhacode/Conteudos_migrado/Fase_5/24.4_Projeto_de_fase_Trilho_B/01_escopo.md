---
arquivo_id: "f5-24-4-01-escopo"
parent_key: "24.4"
tipo_arquivo: "project_scope"
ordem: 0
itens_origem: ["Regras de escolha e escopo", "Escopo mínimo por tipo"]
---

## Regras de escolha e escopo
Antes de começar, consulte o [Guia de Projetos e Rotação](../../../Guia_Projetos_e_Rotacao_de_Tipos.md). Gere as três opções da Fase 5 conforme os tipos T1–T5 disponíveis, estado de cobertura, regra de rotação e tipos pendentes. Escolha um tipo pendente entre as opções; uma repetição pode aparecer como opcional, mas não conta novamente para a cobertura. Registre escolha, estado da tabela de cobertura e motivo.

A versão da Fase 5 é autocontida e inclui base mínima: esquema PostgreSQL com migrations (em geral, 2–4 tabelas), API simples, autenticação, testes e README. A camada do tipo precisa ser demonstrada além de um CRUD genérico. Construa uma fatia pequena; telas, estilo, pagamento real, integrações pagas e funcionalidades laterais estão fora do escopo. Use dados sintéticos e ambiente de teste isolado; não use credenciais, dados pessoais reais ou serviços de produção.

## Escopo mínimo por tipo
- **T1 — Transacional / venda de ingressos:** endpoint de pedido reserva estoque limitado e simula confirmação de pagamento. Use chave de idempotência para repetição da mesma operação. Evidência central: sob requisições concorrentes, estoque não fica negativo/não vende acima do limite; repetir a chave não cria um segundo efeito. Não integre pagamento financeiro real nem prometa “exactly once”.
- **T2 — SaaS multiempresa / agendamento de clínicas:** modele tenant, usuário/papel e um recurso de agenda. A autorização é aplicada em cada leitura e escrita sobre o objeto. Evidência central: usuários autenticados de dois tenants; testes mostram acesso permitido ao próprio recurso e negado ao recurso alheio, inclusive ao alterar o identificador enviado pelo cliente.
- **T3 — Tempo real / colaboração ou votação:** envie atualização via WebSocket ou SSE para pelo menos dois clientes autenticados. Defina um evento e o estado persistido mínimo. Evidência central: cliente recebe a atualização do outro, cliente não autenticado não entra no fluxo protegido, desconexão/reconexão tem comportamento explícito e reproduzível.
- **T4 — Conteúdo, feed e busca / catálogo:** implemente endpoints paginados, filtrados e ordenados, contrato documentado em OpenAPI e índices justificados pelas consultas. Evidência central: filtros e ordem estáveis, limites de página aplicados, entradas inválidas rejeitadas e teste que detecta itens repetidos/omitidos entre páginas segundo a estratégia escolhida.
- **T5 — Dados e processamento assíncrono / importador:** receba arquivo de exemplo com tamanho/formato limitados, processe por stream/job e disponibilize estado consultável. Evidência central: fluxo de sucesso e erro, status persistido, limites aplicados antes/de durante o processamento e reprocessamento seguro definido. Arquivo deve ser sintético; explique descarte e não exponha conteúdo em logs.

