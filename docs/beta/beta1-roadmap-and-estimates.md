# Beta 1 — roadmap e estimativas

Estimativas em dias de engenharia (d.e.), baseadas somente no retrato C16 e branches lidas; faixas são planejamento, não prazo. Não incluem espera de decisões, acesso operacional, revisão pedagógica, fila de infraestrutura nem retrabalho de integração. Volumes de código não representam percentual de produto pronto.

## Sequência recomendada

| Onda futura | Escopo e dependências | Saída/critério | Estimativa |
|---|---|---|---|
| R0 — Canon Git e decisões de produto | Owner define SHA canônico; branch migratória é fatiada; escopo Pioneiros e primeira fase são aprovados | Base limpa identificada; diffs proprietários revisados; nenhuma worktree suja descartada | 5–10 d.e. + revisão |
| R1 — Contrato curso/import/auth | Origem curricular, IDs, mapping quiz/gabarito/submission; fluxo convite/auth; decisões de privacidade | Fixture de uma fase compatível; dry-run repetível em banco descartável; sessão/acesso E2E | 8–15 d.e. + revisão pedagógica |
| R2 — Integridade editorial e dados | Baseline autorizado ADR-008; revisar e conter writers concorrentes, roles DB e publicação; backup/restore | Testes persistentes/falha/bypass; controles de dados aprovados; conteúdo congelável com enforcement | 12–25 d.e. editoriais + 6–12 d.e. de dados/ops, parte paralela |
| R3 — Jornada aluno | Uma fase publicada, leitor, quiz, submission/correção, progresso e canal feedback | E2E de ponta a ponta e regressões; mobile/a11y crítico aprovado | 8–16 d.e. + 4–8 d.e. QA, parcialmente paralelos |
| R4 — Homologação Pioneiros | Monitoramento, suporte, backup, incident, capacidade, convite gradual; decisões humanas | Readiness review assinada e teste de rollback/restore; aprovação de beta | 4–8 d.e. + Ops e suporte |
| R5 — Opcional pós-beta | Gamificação, tutor contextual, lab seguro, Premium/certificação | Projetos separados com contratos/ameaças e custos próprios | Gamificação 5–10; tutor 8–18; lab 20–40+; Premium 15–30+ d.e. |

## Faixas por área

| Área | Esforço restante | Motivo |
|---|---|---|
| Base Git e reconciliação | Grande | Muitos commits locais/branches, worktrees sujas, pacote curricular incompatível |
| Curso + importação | Grande | 131 unidades, muitos blocos/arquivos, transformação, respostas privadas e pendências |
| Backend aluno | Médio | Endpoints existem; fechar contrato, E2E e casos de falha |
| Frontend aluno | Médio | Fluxos existem; executar build/test/QA mobile/a11y e alinhar import |
| Segurança editorial | Muito grande | Escritores multi-coleção, bypass direto, IAM e baseline pendente |
| Operação/backup/observabilidade | Grande | Apenas config versionada; execução autorizada ausente |
| Tutor IA | Grande | Custo, dados, prompt/contexto, limites e indisponibilidade ainda sem contrato |
| Laboratório seguro | Muito grande | Isolamento de código hostil é projeto de segurança separado |

## Paralelização segura

* Migração de conteúdo e revisão pedagógica podem ser analisadas paralelamente, mas compartilham IDs/manifest; freeze de interfaces antes de integração.
* Frontend do aluno e contrato de API podem evoluir em paralelo com mocks/schema agreed, mas teste final requer integração em mesma base.
* Auth E2E e backup/operabilidade podem avançar em paralelo após ambiente QA designado.
* Segurança editorial pode estudar writers, publicação e IAM em paralelo; não ativar novo writer até eliminar bypasses no escopo.
* Tutor/lab/monetização não devem bloquear a Beta A e ficam fora do caminho crítico.

## Métricas de lançamento

Contar critérios aceitos, não commits: cobertura do conteúdo aprovado (unidades com mapa rastreável e teste), etapas E2E verdes, requisitos de segurança satisfeitos, bugs P0/P1 abertos, restore ensaiado, issues de a11y críticas, e capacidade de suporte. Sem denominadores e owner approval não publicar percentual de “beta pronta”.
