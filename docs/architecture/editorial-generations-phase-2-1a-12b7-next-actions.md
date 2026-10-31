# Fase 2.1A.12B.7 — Próximas ações por nível de autorização

Esta seção recomenda o menor próximo trabalho que reduz incerteza. Ela não concede autorização para executá-lo.

## A. Trabalho documental/de especificação

1. Preservar este registro como trilha das deliberações posteriores sem editar ADRs originais.
2. Obter do responsável de infraestrutura a resposta sanitizada ao pedido já existente de 12B.4B para fechar G10/ADR-008.
3. Para ADR-002, obter decisões de produto sobre expiração, revogação de sessões existentes, retomada, clientes legados e progresso legado.
4. Para ADR-003, pedir classificação campo/consumidor aos responsáveis de produto/frontend; a fase não deve inventar semântica.
5. Para ADR-004, obter inventário de referências e revisão de privacidade/jurídico antes de qualquer prazo ou GC.
6. Após os itens aplicáveis, revisar os contratos específicos com backend/segurança e registrar aprovação técnica separada.

Não iniciar outra auditoria genérica; cada atividade acima tem uma lacuna nomeada e critério definido.

## B. Implementação isolada futura

Ainda não autorizada. Após selecionar baseline (G10), definir escopo limitado e obter autorização independente, a primeira mudança candidata de menor risco é instrumentação passiva dos writers, sem alterar respostas, persistência, publicação ou leitura. Condições antes de propor:

- G10 e base/commit da implementação aprovados.
- Escopo e inventário inicial de writers identificados.
- Instrumentação sem conteúdo pedagógico, PII ou payload em logs.
- Falha da telemetria não altera o comportamento de escrita.
- Testes locais demonstram ausência de side effects.
- Nenhuma flag/cutover; commit e revisão isolados.

Se instrumentar exigir alteração de comportamento, parar e solicitar escopo/decisão adicional.

## C. Trabalho em staging

Não autorizado nesta fase. Depende de baseline de staging comprovado, artefato imutável, G1–G8 conforme o escopo, plano de parada/rollback, dados exclusivamente descartáveis, owner e autorização operacional específica. Nada nesta consolidação concede deployment ou acesso.

## D. Trabalho em produção

Não autorizado. Depende da identificação comprovada de produção, G1–G10 aplicáveis, revisão de segurança/privacidade, compatibilidade, observabilidade, plano de rollback que não reabra readers/writers legados, janela/owner e autorização específica de deployment/cutover. G9 e qualquer exclusão exigem policy aprovada separadamente.

## Menor próximo passo recomendado

Solicitar o retorno sanitizado do administrador conforme [handoff ADR-008](./editorial-generations-phase-2-1a-12b7-adr008-evidence-handoff.md) e deliberar as pendências de produto/privacidade listadas em [decisões pendentes](./editorial-generations-phase-2-1a-12b7-pending-decisions.md). Até então, permanecer em documentação.
