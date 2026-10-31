# Beta 1 — relatório final

## A. Resultado executivo

A árvore C16 tem uma base funcional relevante para uma beta pedagógica mínima, mas curso, API e jornada não estão provados como integração operacional ponta a ponta. O pacote commitado no snapshot não contém quizzes tipados e está todo em draft. A migração segmentada e o contrato tipado continuam em branch/worktree distintos, com alterações locais. Backend/frontend têm implementação de quiz e progresso; visual, E2E e estado implantado não foram verificados. Veredito: **AUDITORIA DA BETA PARCIAL — INTEGRAÇÕES E VALIDAÇÕES PENDENTES**.

## B. Git e isolamento

Base obrigatória `6c227fa6a5ee0940f912d11403747bd9a9c12465`, branch `codex/beta1-platform-course-readiness-audit`, worktree `C:\Users\Joao\.codex\worktrees\trilhacode-beta1-readiness\trilhacodeprod`. `main` local e refs cached divergem; sem fetch não se elege base canônica operacional. Worktrees/checkout originais sujos foram preservados. Entregáveis somente em `docs/beta/`; commit local ao fim; sem push/PR/merge/deploy.

## C. Versão canônica e trabalhos paralelos

C16 é base de auditoria, não certificação de runtime. `origin/main` cached pode estar desatualizada e `origin/HEAD` aponta para master antigo. `migracao-estrutura` possui 12 commits exclusivos de migração e alterações adicionais não commitadas; contrato tipado não compatível demonstrado com importador C16. Auth, a11y, frontend audit e CI têm branches divergentes e patches com sobreposição. Nenhuma integração foi feita. Ver [inventário Git](beta1-git-integration-inventory.md).

## D–F. Backend, frontend e curso

Backend versionado inclui auth/session, catálogo/editorial, import, publish/version/restore, quiz versionado, progress, notes/reviews, submission e correção. Frontend tem rotas de auth, catálogo, leitor, estudo e admin; quiz/submission usam endpoints reais no código. Tutor, sandbox, RPG, Premium/payment, certificate/community e convite Pioneiros não foram encontrados nas áreas de produto inspecionadas. Curso C16 tem 159 Markdown + bundle; 10 fases/53 módulos/131 unidades; 1.691 blocos draft, somente teoria/resumo/nota. Outro conteúdo está em worktrees separadas. Ver inventários backend/frontend e auditoria do curso.

## G–H. Integração curricular e jornada

Há mapeamento estrutural potencial para teoria. Quiz, exercício, gabarito, rubrica e projeto precisam transformação explícita para não virar texto sem avaliação nem expor resposta. Importador C16 aceita contrato legacy; contrato tipado migratório não foi integrado. A cadeia cadastro→aula→tentativa/submissão→feedback→progresso existe nos códigos, mas não houve E2E. Quatro links quebrados identificados no Markdown C16. Visual/mobile/a11y `NOT_VERIFIED`.

## I–N. Laboratório, IA, gamificação, monetização e administração

Code block apenas exibe/copia; sem executor seguro. Não consumir/possuir API de tutor de produto observada; dependências de IA são apenas pacotes. XP/níveis/conquistas não encontrados. Stripe em requirements não equivale a pagamento/entitlement. Admin editorial e correção manual existem; escopo de escrita por trilha não foi observado. Beta gratuita não depende de Premium.

## O–P. Segurança e infraestrutura

Auth/session existe no código, não homologada operacionalmente. C16 registra bypass possível de autoridade editorial por writer com DB write direto. Não abrir edição concorrente de conteúdo publicado sem contenção ou bloqueio comprovado. Compose/Docker/CI são configurações versionadas apenas; backup/restore, TLS, DB roles, monitoramento e deploy não foram observados. Nenhum staging/produção/Coolify/GHCR foi acessado.

## Q. Testes

* C16 offline selecionado: **14 passed** (snapshot safety + contratos de prontidão e contenção); zero skips/falhas nessa execução.
* Snapshot: **6 passed**, doubles/monkeypatch, sem Mongo; cobertura limitada a validação do documento/ledger e captura acima do limite antigo.
* C14 histórico: reporta 183 testes/38 subtests e snapshot 6; não é repetição desta Beta.
* Outras suites backend/persistentes: `NOT_RUN` (sem hipótese/infra autorizada necessária nesta fase).
* Frontend build/typecheck/lint/Vitest/Playwright: `NOT_RUN`, `node_modules` ausente e serviços não iniciados.
* Ruff/Mypy: `NOT_APPLICABLE` (nenhum Python novo); compilação Python não foi necessária. Links/JSON/diff serão validados antes do commit.

## R. Escopo beta recomendado

Beta A reforçada: fase única completa após conversão, quiz versionado, exercício com correção humana, progresso, convite manual, feedback e suporte, gratuita/sem cartão. Não convidar antes de E2E, mobile/a11y, política de dados/backup/restore, baseline ADR-008 e proteção editorial.

## S–U. Backlog, roadmap, estimativas

[P0/P1/P2/P3 backlog](beta1-prioritized-backlog.md) define critérios e testes. [Roadmap](beta1-roadmap-and-estimates.md) organiza canon→curso/auth→integridade/dados→jornada→homologação→beta. Segurança editorial e conversão curricular são grandes/muito grandes; executor de código é projeto separado (20–40+ d.e. como faixa preliminar). Estimativas não garantem prazo.

## V. Gates

Preservados: G1 `PARTIAL`; G2 `NOT_VERIFIED`; G3 `NOT_VERIFIED`; G4 `PARTIAL`; G5 `NOT_VERIFIED`; G6 `PARTIAL`; G7 `PARTIAL`; G8 `NOT_VERIFIED`; G9 `BLOCKED`; G10 `BLOCKED`. ADR-008 permanece bloqueado. Nova matriz Beta não promove gate histórico.

## W. Limitações

Sem fetch, runtime, Mongo, staging, deploy, dados de usuário, E2E, browser ou medição visual. Cópia original e migração com alterações locais não são canonicalizadas; seus conteúdos foram lidos em modo leitura e classificados separadamente. Inventários estáticos não provam cobertura dinâmica nem implantação.

## X. Próximo incremento

Autorizar uma etapa de **consolidação Git e compatibilidade curricular**, começando por decisão do owner sobre base canônica e a fonte do curso; fatiar/revisar a migração e testar a importação de uma única fase em banco descartável, com trilha de IDs e tipos de atividade. Manter sem mutação operacional até o baseline ADR-008 e contenção editorial serem resolvidos.

## Y. Veredito

**AUDITORIA DA BETA PARCIAL — INTEGRAÇÕES E VALIDAÇÕES PENDENTES.** Há código útil para uma beta pedagógica mínima, mas ainda não há base canônica operacional demonstrada, curso interativo integrado, jornada E2E homologada ou evidência de infraestrutura. Implementação da beta não foi iniciada; o escopo e backlog aqui não autorizam lançamento.

Matriz estruturada de funcionalidades: [beta1-feature-inventory.json](beta1-feature-inventory.json).
