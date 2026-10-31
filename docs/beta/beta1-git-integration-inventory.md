# Beta 1 — inventário Git e integração

## Método

Leitura das refs locais e `git worktree list` em 2026-10-29. Nenhum fetch/pull/merge ou alteração de worktree alheia. Refs `origin/*` são cache sem atualização. Commit isolado não equivale a função integrada; HEAD desta auditoria é base obrigatória, não versão operacional certificada.

## Referências

| Ref | HEAD | Diferença/estado observado |
|---|---|---|
| `main` | `65857f5a4d26b026f7b064862bebc29091713d9a` | Metadado local indica 47 atrás; não eleger automaticamente |
| `origin/main` cached | `22dca64556338a8fa9aaa89ce627a4f4af72317d` | Ancestral da C16; C16 +55 commits; pode estar stale |
| `master` / `origin/master` | `746b9e8bc4d44931079485ec8f8354f3fc1667a3` | Antigo; `origin/HEAD` aponta para ele |
| checkout original | `codex/compose-ci-validation`, `27a98964d55b96003fac70154178c5892da8d453` | 37 status entries sujas; preservadas |
| C16 | `6c227fa6a5ee0940f912d11403747bd9a9c12465` | Base isolada; contém fases editoriais C8–C16 |
| `migracao-estrutura` | `147dc68b81169f66b0ba3802fa2f26e5130923a3` | 12 commits próprios; 2.951 paths no diff; worktree suja |
| `codex/public-email-verification-auth` | `8a1b3467c1d7225f4dcbbe546c9cc264f4acc888` | 20 commits exclusivos; sobreposição com auth C16 |
| `codex/qa-mobile-a11y` | `d26fe097454e75a8f58d564a5fec4c10e57276dc` | 5 commits exclusivos, 9 caminhos |
| `codex/fix-frontend-audit-20261025` | `fa9da554713efe44a2aae4e372a40ea68f969f29` | 2 commits, package/lock/log de release |
| `codex/ci-foundation-validation-only` | `d85154c8ad26bbcd6c6ea3f02bce0ea734e752df` | 1 workflow exclusivo |
| `codex/staging-smtp-required-20261025` | `9ff817d4…` | Ref divergente; não prova staging |
| `origin/staging` cached | `fff85218…` | Somente ref local; nenhum ambiente consultado |

Há worktrees de migração, foundation/runtime, G2, release, atividade e C1–C16. Checkout original e worktrees existentes ficaram intactos. Trabalho não commitado foi observado no original, `fase1-migracao`, `fase1-5-1-runtime` e `trilhacodeprod-main-20261018`; não houve limpeza/cópia. A worktree Beta foi criada isolada e era limpa antes dos entregáveis.

## Integração e sobreposição

### Migração curricular

A branch `migracao-estrutura` tem 12 commits, 2.951 paths de conteúdo/mapeamento/documentação no diff local. Na worktree associada havia mais alterações não commitadas de backend/frontend (import tipado, quiz/atividade, persistência editorial, modelos e testes) e bundle modificado. O contrato modificado visto registra 3.431 blocos tipados, 2.890 arquivos, 214 pendências editoriais, 66 warnings e status draft. O relatório daquela worktree diz que persistência editorial não foi conectada a rotas, importador, publicação, progresso, quizzes operacionais ou frontend. É autorrelato/histórico de trabalho, não validação desta auditoria.

**Risco alto:** mudanças grandes e sobrepostas; contrato novo incompatível com o importador C16. Revisar patch por interface e manter conteúdo privado; não fazer merge/execução por volume.

### Autenticação

A branch isolada altera `routes_auth.py`, `security.py`, `services/auth.py`, telas e E2E; C16 já contém registro, verificação, recuperação, login/logout/refresh. É sobreposição de comportamento com diferenças de implementação e testes; exige diff de regras antes de integração.

### Mobile/acessibilidade

A branch QA altera `ExerciseSubmission`, `NodeReader`, admin e E2E. C16 contém os arquivos-base, não necessariamente as correções. Inspecionar diffs e executar QA de navegador em fase autorizada.

### Frontend/CI/infra

Branch de auditoria frontend altera package/lock e log; confirmar se cada fix está no baseline canônico. Branch CI tem workflow manual. G2/staging têm scripts/documentação, mas não foram executados e não autorizam acesso aos serviços.

## Canonicidade e procedimento futuro

Não é possível escolher uma base operacional canônica a partir de refs locais sem fetch autorizado e decisão humana. C16 é a base obrigatória desta auditoria e a mais avançada da série editorial, não prova de deploy. `origin/main` é cached; `origin/HEAD` aponta para master antigo.

Futuro: (1) owner define commit base; (2) atualizar refs sob autorização; (3) confirmar proprietário de trabalho sujo; (4) quebrar migração em mudanças revisáveis de conteúdo/bundle/backend/frontend; (5) reconciliar contratos e testes; (6) integrar por processo revisado somente em fase autorizada. Não integrar nesta Beta 1.
