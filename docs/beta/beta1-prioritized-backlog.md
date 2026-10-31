# Beta 1 — backlog priorizado

Estimativas abaixo são dias de engenharia (d.e.), faixas de ordem de grandeza; incluem desenvolvimento e testes locais quando explicitado, não espera por decisão, migração, homologação ou calendário. Ver [roadmap](beta1-roadmap-and-estimates.md). P0 bloqueia abertura segura; P1 compõe jornada recomendada; P2 melhora; P3 pós-beta.

| ID/P | Tarefa e problema | Dependências | Aceitação verificável | Testes | Esforço | Paralelo |
|---|---|---|---|---|---|---|
| T-01 P0 | Definir base canônica e reconciliar conteúdo/migração/branches | Owner escolhe base; checkout/worktrees preservados | Commit de plataforma escolhido; diffs por área aprovados; sem trabalho sujo perdido; CI em base limpa | Git ancestry/diff, build e regressões | Grande, 5–10 d.e. de engenharia + revisão | Parcial: inventário de diffs paralelo |
| T-02 P0 | Fixar fonte da formação inicial e contrato de importação | T-01; decisão editorial sobre warnings | Unidade origem→ID→nó/bloco rastreável; quiz/gabarito/rubrica com política; dry-run em banco descartável reproduzível | Unit/schema, round-trip, persistente isolado | Grande, 8–15 d.e. + revisão pedagógica | Conteúdo pode mapear enquanto API é avaliada |
| T-03 P0 | Comprovar jornada de autenticação e acesso | T-01; SMTP de QA | Cadastro, verificação, login, logout, sessão expirada/revogada e acesso negado comportam-se conforme contrato; sem cartão | Unit + API + E2E com usuários sintéticos | Médio, 4–8 d.e. + QA | Sim com T-02 |
| T-04 P0 | Definir e comprovar integridade de conteúdo publicado | Decisão editorial/ADR-008; inventário writers | Nenhum writer concorrente sem autorização confirma dentro do escopo; ou edição/admin efetivamente restringida; publicação e tentativa versionadas | Transação Mongo, corrida, falha e bypass, revisão de roles | Muito grande, 12–25 d.e. + security review | Em paralelo com conteúdo, não ativar mutação antes de cobertura |
| T-05 P0 | Operação segura de dados do aluno | DB/baseline aprovado | Backup restaurado em ambiente isolado; acesso por usuário; logs/retention/incident/support aprovados | Backup/restore, ACL, isolamento, failure drill | Grande, 6–12 d.e. + Ops | Parte paralela com T-03 |
| T-06 P1 | Completar uma fase de ponta a ponta no produto | T-02, T-03, T-04/controle de publicação | 1 fase publicada; aulas, quiz objetivo, exercício manual, feedback e progresso verificados por aluno de teste | Persistente + E2E desktop/mobile + reimport | Grande, 8–16 d.e. + pedagógico | UI e contrato/import podem avançar em paralelo |
| T-07 P1 | Canal de Pioneiros e suporte | Decisão owner sobre inscrição, suporte e privacidade | Acesso controlado sem cartão, coleta mínima, canal/triagem/remoção documentados e simulados | API/UI/manual runbook; privacidade | Pequeno/Médio, 3–6 d.e. | Sim com T-06 |
| T-08 P1 | QA de acessibilidade e mobile | T-01; branch QA revisada | Casos críticos teclado, leitor de tela, contraste, viewport pequeno e submission passam | Vitest/Playwright + revisão humana | Médio, 4–8 d.e. + QA | Sim com T-06 |
| T-09 P2 | Gamificação básica | T-06; regra de XP/anti-abuso aprovada | XP apenas de eventos válidos, replay não duplica; UI e suporte compreensíveis | Unit, concorrência/idempotência, E2E | Médio, 5–10 d.e. | Depois da jornada base |
| T-10 P2 | Tutor IA contextual | Segurança/privacidade/custos aprovados; contexto de curso/progresso | Tutor limitado a explicar/orientar, sem editar código; limite de uso/custo, desligamento e fallback testados | Privacy, abuse, provider contract, E2E | Grande, 8–18 d.e. + operação | Contexto pode ser desenhado junto ao curso |
| T-11 P3 | Laboratório de execução segura | Segurança de execução independente | Sandbox isolada, sem rede por padrão, limites, quotas, limpeza, avaliações e abuse tests aprovados | Threat model, container isolation, adversarial, load cap | Muito grande, 20–40+ d.e. | Projeto separado |
| T-12 P3 | Premium comercial, certificado/comunidade | Produto e compliance/operacional aprovados | Entitlements, pagamento/webhooks/retorno, cancelamento e emissão auditável | E2E pagamento sandbox + reconciliação | Grande/Muito grande, 15–30+ d.e. | Separado da beta grátis |

## Ordem

T-01 desbloqueia decisões sobre base. T-02 e T-03 podem avançar em paralelo após T-01. T-04 e T-05 são condições de segurança para dados/editor; T-06 depende de ambos e do conteúdo. T-07/T-08 complementam a abertura. T-09/T-10 são opcionais posteriores. T-11/T-12 não pertencem à primeira beta.

## Métrica de progresso

Acompanhar por tarefa estados `NOT_STARTED`, `IN_PROGRESS`, `BLOCKED`, `READY_FOR_REVIEW`, `ACCEPTED`; anexar evidência/teste por critério. Não produzir percentual global por linhas de código. Uma beta é “convite autorizado” somente quando todos os P0/P1 marcados como necessários à opção escolhida forem aceitos e owner autorizar a abertura.
