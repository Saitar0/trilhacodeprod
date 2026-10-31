# Beta 6 — jornada ponta a ponta

## Cenário implementado como teste, mas bloqueado

`backend/tests/test_beta6_learning_journey.py` descreve um fluxo HTTP com aluno sintético e avaliador com escopo de trilha: fixture isolada, leitura de unidade, quiz e resposta sem gabarito, submissão manual, idempotência, bloqueio de autoaprovação, negação de editor sem escopo, fila/claim/correção, feedback, isolamento de outro aluno e progresso persistido. A suíte não iniciou por causa do binding de porta Docker não verificável descrito no relatório persistente. Não há resultado observado desse fluxo.

## Frontend

Há evidência de Vitest: 29 testes aprovados em nove arquivos, incluindo teste do componente de resposta de exercício. TypeScript `typecheck` e ESLint passaram. Build Vite concluiu, emitindo aviso de chunk de entrada acima de 500 kB. Esses resultados não constituem E2E, não iniciaram API e não comprovaram a interface real sobre MongoDB.

Não foi possível automatizar navegador; portanto a interface visual, responsividade e interação real com backend continuam NOT_VERIFIED. Não declarar jornada completa.

## Condição de repetição

Reexecutar somente em executor descartável que forneça rede interna/saída bloqueada e binding de loopback verificável, sem compartilhar rede, porta, volume ou banco. Antes do fluxo completo, validar o alvo pelo harness e confirmar ownership; falha de identidade deve encerrar antes de inicializar app, migrações ou seed.
