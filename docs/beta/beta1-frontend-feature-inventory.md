# Beta 1 — inventário frontend

Leitura da árvore React/TypeScript C16. `frontend/node_modules` está ausente na worktree; não houve install, build, browser, QA visual/mobile ou performance. Responsividade/a11y ficam `NOT_VERIFIED` mesmo havendo classes e `data-testid`.

| Área | Estado | Componentes/calls vistos | Necessidade/lacuna |
|---|---|---|---|
| Login/cadastro | `IMPLEMENTED_IN_INSPECTED_CODE` | `AuthPage`, `AuthContext`, `/auth/*` | E2E da conta completa |
| Confirmar email/reset | `IMPLEMENTED_IN_INSPECTED_CODE` | `ConfirmEmail`, `PasswordRecovery`, `PasswordReset` | Verificar SMTP/UX de erro em QA |
| Catálogo | `IMPLEMENTED_IN_INSPECTED_CODE` | `Catalog` consulta `/tracks`, `/progress/overview` | Necessário; depende de conteúdo publicado |
| Leitor/unidade | `IMPLEMENTED_IN_INSPECTED_CODE` | `TrackViewer`, `StudentTree`, `NodeReader`, `BlockRenderer` | Necessário; jornada não executada |
| Teoria/resumo | `IMPLEMENTED_IN_INSPECTED_CODE` | `theory_text`/`summary` → Markdown | Compatível estruturalmente |
| Quiz estático | `PARTIALLY_IMPLEMENTED` | `QuizBlock` mostra opções e mensagem sem avaliação publicada | Não registra tentativa/nota |
| Quiz versionado | `IMPLEMENTED_IN_INSPECTED_CODE` | `ActivityRenderer`, `MultipleChoiceActivity`, `FeedbackPanel` | Necessita definition importada/publicada |
| Exercício escrito | `IMPLEMENTED_IN_INSPECTED_CODE` | `ExerciseSubmission` chama `/submissions/draft` e `/submit` | Correção humana; E2E não executado |
| Código de exemplo | `PARTIALLY_IMPLEMENTED` | `CodeBlock` com copiar para clipboard | Sem editor ou execução |
| Progresso/estudo | `IMPLEMENTED_IN_INSPECTED_CODE` | `useData`, `useStudy`, `MyStudy` | E2E e consistência após falhas |
| Admin/editorial | `IMPLEMENTED_IN_INSPECTED_CODE` | `AdminTracks`, `TrackEditor`, `ImportTrack`, `Versions`, `Taxonomies`, `Grading`, `Users` | Não abrir escrita a editores sem proteção editorial |
| Tutor IA | `NOT_FOUND` | Sem tela ou client encontrado | Adiar |
| XP/RPG/conquistas | `NOT_FOUND` | Sem tela/estado encontrado | Adiar |
| Premium/checkout | `NOT_FOUND` | Sem páginas/entitlements | Não necessário para beta grátis |
| Pioneiros/convites | `NOT_FOUND` | Sem fluxo específico encontrado | Operação manual temporária, aprovada pelo owner |
| Certificados/comunidade | `NOT_FOUND` | Sem páginas/API no escopo inspecionado | Posterior |
| Mobile/a11y | `NOT_VERIFIED` | Branch `qa-mobile-a11y` contém patches isolados | Revisar patch e executar browser depois |

`frontend/src/App.tsx` roteia auth, catálogo, estudos, perfil, trilha e admin. `frontend/src/lib/api.ts` implementa refresh em 401. Isso não prova que toda API/estado de erro funcione em browser.

### QA pendente

Primeiro acesso vazio, rede lenta/erro, expiração de sessão, permissão negada, foco/teclado/leitor de tela, viewport estreito, erro/conflict de tentativa, mudança de publicação com tentativa aberta, Markdown/links/iframe e preservação de resposta precisam ser verificados visualmente e em E2E. As branches `qa-mobile-a11y`, `public-email-verification-auth` e `fix-frontend-audit` são divergentes e sobrepõem arquivos C16; revisar diffs antes de decidir integração.

`package.json` declara build, typecheck, lint, Vitest e Playwright. Como dependências frontend não estão instaladas e serviços não podem ser iniciados, nenhum comando foi executado nesta fase.
