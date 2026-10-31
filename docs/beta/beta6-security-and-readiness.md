# Beta 6 — segurança, bloqueios e prontidão

## Controles na worktree

* Identity vem de `current_user`; mutações usam permissões existentes e validação de origem.
* Instrutor precisa da permissão estática de correção e escopo experimental ativo por trilha.
* Recurso fora de escopo é negado; acesso do aluno a submissão alheia responde como inexistente.
* Projeções públicas e de avaliador são allowlists fechadas; metadados desconhecidos e contexto interno não atravessam respostas de submissão.
* Entrada de resposta/correção é estrita e limitada; quiz continua sendo corrigido no backend existente.
* Claim/correção/salvamento usam revisão condicional; idempotência e eventos de progresso usam chaves estáveis.
* Testes persistentes falham fechados e não recorrem a uma instância local.

## Bloqueios

1. Banco descartável Beta 6 não passou a prova de binding de porta e, por isso, a integração HTTP não foi executada.
2. Não há grants operacionais por trilha para avaliadores; `learning_review_scopes` é política de laboratório sem ciclo IAM de concessão/revogação.
3. C16 continua demonstrando bypass possível por escritores com escrita direta nas coleções de conteúdo. Beta 6 não altera esse problema e não promove conteúdo.
4. Frontend e API não foram exercitados juntos em browser; aparência, mobile e acessibilidade visual não homologados.
5. Reconciliação de progresso é multi-etapa, não transação única; requer teste persistente/falhas e decisão de operação de retry.
6. Explicações pós-quiz e critérios pedagógicos ambíguos não receberam nova política.
7. Projeto 3.5 continua sem fluxo de submissão/avaliação e sem liberação geral dos 11 artefatos.
8. Gates históricos e ADR-008 permanecem bloqueados/parciais conforme baseline.

## Estado

Implementação isolada presente; testes offline e frontend aprovados conforme relatório final. O objetivo de jornada integrada não foi demonstrado. Não ativar para Pioneiros nem conectar a banco com alunos até concluir prova de HTTP/persistência, E2E, revisão de IAM, privacidade e homologação.
