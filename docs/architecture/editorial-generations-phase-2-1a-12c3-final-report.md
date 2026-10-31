# Fase 2.1A.12C.3 — Relatório final

## A. Resultado

O adaptador persistente da Fase 12C.2 foi exercitado em MongoDB 7.0.43 real, em replica set local descartável de nó único. Duas execuções finais passaram com **27/27 testes cada**, incluindo os 24 cenários MongoDB e três verificações da URI, sem skips no processo principal. A reexecução interna de T24 também passou; cada suíte filha teve um skip intencional para evitar recursão.

O teste real demonstrou CAS, transações no MongoDB usado, fencing, idempotência, histórico/recibos persistidos, conflitos e concorrência entre processos para essa topologia. Não demonstra failover, alta disponibilidade, integração com writers da aplicação ou prontidão de produção.

**Veredito:** `VALIDAÇÃO PERSISTENTE ISOLADA APROVADA — INTEGRAÇÃO NÃO AUTORIZADA`.

## B. Git e isolamento

- Base: `563b47bf1435b473043e4d3f7f82f7ff14d87164`.
- Branch: `codex/fase2-1a-12c3-mongodb-persistent-validation`.
- Worktree: `C:\Users\Joao\.codex\worktrees\trilhacode-fase2-1a-12c3-mongodb-persistent-validation\trilhacodeprod`.
- A worktree foi criada com `--no-checkout`; sparse-checkout foi configurado antes do checkout. `backend/services` foi incluído posteriormente apenas para executar a regressão unitária da PoC.
- `docs/courses/trilhacode/` e `docs/migracao/` não foram materializados.
- O checkout original e outras worktrees não foram alterados.

## C. Ambiente e segurança

Docker Desktop/Engine 29.8.2 iniciou pelo fluxo normal. O MongoDB usou imagem oficial `mongo:7.0.43`, digest `sha256:1f995ad6fdb93244a1addab1b58f934a0bc2f5643c38e02f5e9d7f0c7d227a7b`, rede Docker interna sem porta publicada e volume de dados exclusivo. O runner Python 3.11.17 compartilhou apenas a namespace de rede do container MongoDB; o checkout foi montado somente para leitura. PyMongo 4.18.2 e dnspython 2.9.0 ficaram em volume temporário da fase.

O servidor confirmou replica set `rs12c3`, primário, sessões lógicas e WiredTiger. O adaptador usou transações com read concern `snapshot`, write concern `majority` mais journal e preferência `primary`. O replica set de nó único não equivale a tolerância a falhas de um cluster.

As URIs incompatíveis com loopback, sem credenciais, replica set e base sintética foram recusadas pelos testes. Nenhuma rota ativa importa ou usa o adaptador. Não houve acesso a produção, staging, Coolify, GHCR, MongoDB da aplicação ou dados de alunos.

## D. Testes e defeitos

- Integração MongoDB: duas invocações de 27/27, sem falhas ou skips principais; duração 32,164 s e 42,027 s. T4, T6, T9, T11, T22 e T23 executaram processos Python separados.
- T24 executou novamente a suíte em subprocesso. Cada filha passou em 26 casos e ignorou somente T24 para impedir recursão.
- Protocolo 12C.1, contratos offline 12C.2 e PoC com fakes: 52/52 aprovados.
- Ruff e mypy: aprovados.

As primeiras tentativas encontraram dois defeitos na fixture de T24: importação pelo pacote errado e descarte de `PYTHONPATH` na suíte filha. Ambos foram corrigidos no teste; duas execuções completas posteriores passaram. Não foi encontrado defeito demonstrado no adaptador.

## E. Evidências por propriedade

| Propriedade | Evidência | Resultado/limite |
|---|---|---|
| Revisão monotônica e CAS | T1–T4, T23 em MongoDB | Aprovados; threads e processos separados |
| Fencing e fence sem nova revisão | T6, T7, T20, T22 | Writer antigo rejeitado; a corrida foi ordenada/rejeitada |
| Idempotência e colisão | T8–T11, T15–T16 | Recibo recuperado, payload divergente conflita e repetição não duplica revisão |
| Atomicidade | T17 | Falha dentro da transação deixou estado, histórico e recibo sem confirmação parcial |
| Histórico e recuperação | T2, T9, T16, T23 | Persistem após novas instâncias/processos |
| Isolamento | T12 e fixture | Trilhas isoladas; bancos sintéticos removidos após cada teste |
| URI | Três testes | Hosts remotos, credenciais, SRV e nome fora do padrão recusados |

T15 simula perda de resposta no cliente após commit já confirmado. Não simula interrupção de rede durante o commit nem `UnknownTransactionCommitResult`. Não houve reinício do servidor MongoDB; “reinício” exercitado refere-se ao processo/adaptador cliente.

## F. Recursos e limpeza

Recursos criados com labels da fase: container MongoDB, rede bridge interna, volume de dados, volume temporário de dependências e volume anônimo de configuração associado ao container. Após a suíte, a listagem confirmou zero bancos `editorial_revision_test_*`. O container foi parado/removido; a rede e os volumes rotulados foram removidos; o volume anônimo foi removido com o container. A consulta final encontrou zero containers, redes ou volumes com a label da fase. Imagens oficiais que já existiam antes da execução foram preservadas. O Docker Desktop global permaneceu em execução.

## G. Gates e limites

As evidências contribuem para G2, mas não o satisfazem: falta validar topologia operacional pertinente, cobrir writers reais e aprovar a integração. G1 permanece `PARTIAL`, G9 `BLOCKED` e G10 `BLOCKED`; nenhum gate histórico foi promovido.

Não foram alterados adaptador funcional, APIs, schemas, dados reais, writers ativos, publicadores, feature flags, infraestrutura compartilhada ou documentação histórica. A única alteração de código desta fase corrige o harness T24; os outros arquivos são este relatório e a matriz de validação.

## H. Arquivos da fase

- `backend/integration_tests/test_mongodb_editorial_revision_integration.py` — correção de pacote e propagação condicional de `PYTHONPATH` no subprocesso T24.
- `docs/architecture/editorial-generations-phase-2-1a-12c3-persistent-validation.md` — ambiente, resultados, propriedades e limitações.
- `docs/architecture/editorial-generations-phase-2-1a-12c3-final-report.md` — este relatório.

## I. Próximo incremento

Submeter a evidência de G2 para revisão arquitetural. Qualquer adaptação de writers, uso compartilhado, migração ou implantação requer autorização separada; esta fase não autoriza integração.
