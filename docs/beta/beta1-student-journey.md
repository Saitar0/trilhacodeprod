# Beta 1 — jornada do aluno

Classificação por evidência na árvore C16. Não executamos a interface, banco ou E2E; “código implementado” não significa jornada comprovada.

| Etapa | Frontend | API/backend | Estado | Falta / severidade |
|---|---|---|---|---|
| Cadastro/verificação | `AuthPage`, `ConfirmEmail` | `/auth/register`, verify/resend | `IMPLEMENTED_IN_INSPECTED_CODE` | Teste E2E com email de teste e limites; P0 |
| Login/sessão | `AuthContext`, `ProtectedRoute`, refresh client | `/auth/login`, `/refresh`, `/logout`; JWT e `auth_sessions` | `IMPLEMENTED_IN_INSPECTED_CODE` | Expiração/revogação e cookies em homologação; P0 |
| Onboarding/convite | Nenhuma experiência Pioneiros encontrada | Sem serviço invite/waitlist encontrado | `NOT_FOUND` | Processo manual ou novo contrato aprovado; P1 |
| Catálogo | `Catalog` | `GET /api/tracks`, progresso overview | `IMPLEMENTED_IN_INSPECTED_CODE` | C16 course todo draft; sem publicação observada; bloqueio crítico |
| Acesso/matrícula | Protected route e viewer | Visibilidade da trilha por published/public; sem matrícula específica encontrada | `PARTIALLY_IMPLEMENTED` | Definir acesso gratuito/convite e escopo do piloto; P0 |
| Aula/leitor | `TrackViewer`, `StudentTree`, `NodeReader`, renderers | `/tracks/{id}/tree`, `/nodes/{id}` | `IMPLEMENTED_IN_INSPECTED_CODE` | Conteúdo importado e renderer não verificados; P0 |
| Quiz objetivo | `MultipleChoiceActivity` | `/activities/{id}/attempts`, draft, submit; activity publication | `IMPLEMENTED_IN_INSPECTED_CODE` | Bundled course não tem quiz tipado; E2E não rodado; P1 |
| Exercício escrito | `ExerciseSubmission` | `/submissions/draft`, submit, mine; `submissions` | `IMPLEMENTED_IN_INSPECTED_CODE` | Confirmar persistência/retorno/correção E2E; P1 |
| Feedback | `FeedbackPanel`, tela de correção | `grade_submission`, tentativa avaliada | `IMPLEMENTED_IN_INSPECTED_CODE` | Rubrica do curso e feedback ao aluno; QA de privacidade; P1 |
| Progresso | `useData`, `useStudy`, `MyStudy` | `/progress`, history/overview, notes/reviews | `IMPLEMENTED_IN_INSPECTED_CODE` | Persistência e ligação aos critérios curso; P0 |
| Conclusão | Status concluído e UI | Progresso por nó/bloco | `PARTIALLY_IMPLEMENTED` | Definir critério completo e teste de geração; P1 |
| Suporte/feedback | Sem caixa beta identificada | Sem endpoint de feedback Pioneiros identificado | `NOT_FOUND` | Canal, SLA e triagem definidos antes de convite; P1 |
| Perfil | `Profile` | profile APIs | `IMPLEMENTED_IN_INSPECTED_CODE` | E2E/privacidade não verificados; P2 |

## Fluxo resumido

`App.tsx` liga autenticação → catálogo → trilha/unidade. Catalog e TrackViewer chamam APIs via hooks; componente de atividade usa endpoints de tentativa; exercício chama submissions; hooks de estudo chamam progresso/notas/revisões. O backend possui rotas correspondentes. Essa cadeia de chamadas foi observada estaticamente, não exercitada ponta a ponta.

## Mobile e acessibilidade

`qa-mobile-a11y` é branch separada com ajustes e testes E2E. Sem execução de navegador, não é possível declarar navegação, contraste, teclado, foco, leitura de tela ou layout mobile aprovados. Isso é bloqueador de convite, não uma observação estética opcional.

## Critério mínimo de jornada aprovada

Em ambiente de QA isolado, identidade de teste recebe convite/acesso sem cartão; verifica email, autentica, encontra a fase publicada, abre aula, realiza uma atividade, salva tentativa/submissão, recebe feedback, fecha sessão, volta e vê progresso consistente. Repetir com perda de rede, refresh, sessão revogada, quiz republished, aluno sem acesso e tela estreita. E2E deve comprovar dados no banco de teste sem usar usuário real.
