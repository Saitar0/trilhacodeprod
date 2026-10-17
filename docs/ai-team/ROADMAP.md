# Roadmap técnico

Atualizado em 17/10/2026 a partir de main (27a98964) e evidências dos PRs/CI desta missão. Status distinguem validação local, CI e homologação real.

| Frente | Status | Evidência verificada | Próximo critério |
| --- | --- | --- | --- |
| A — qualidade e confiabilidade | CONCLUÍDA | PR #9 adiciona Mongo descartável com URI local/direct-only e valida Compose sem iniciar serviços. CI #18 passou backend, frontend e Compose. | Revalidar após merge manual. |
| B — testes E2E | EM EXECUÇÃO | PR #12 usa Mongo efêmero e seed de CI. CI #45 passou aluno, admin navigation e checks 360/390 px. A edição admin foi salva e confirmada após reload na CI #50. CI #51 verifica que os deploy jobs também dependem do E2E. | CI #50 verde para a ponta de persistência. |
| C — experiência/responsividade | CONCLUÍDA COM ESCOPO LIMITADO | CI #45 não encontrou overflow horizontal no catálogo, overview e reader em 360 e 390 px. Sem browser desktop local para inspeção visual. | Inspeção visual/teclado e acessibilidade em uma rodada com navegador utilizável. |
| D — desempenho frontend | CONCLUÍDA | PR #10 reduziu chunk do catálogo Lucide de 799.578 B / 147,81 KiB gzip para 213.071 B / 50,78 KiB gzip (~65,7% menos no chunk). CI #19 passou. Build usa cerca de 1.593 chunks sob demanda (~1,35 MB bruto somado). | Monitorar requests e regressões do build após integração. |
| E — backend, segurança e integridade | CONCLUÍDA PARA OS ACHADOS DESTA MISSÃO | PR #11 fecha leituras diretas de trilhas privadas (CI #21). PR #13 valida formato/valores e tamanho BSON de documentos gerados antes do planejamento; 33 testes locais, CI #48 e revisão independente passaram. PR #14 prova promoção/revogação em sessão ativa; CI #46 passou. Auditoria de auth/CORS/proxy não encontrou falha adicional reproduzível. | Ampliar matriz para rotas menos cobertas em novo conjunto de testes de integração. |
| F — homologação funcional | PARCIAL | Fluxos de estudante e navegação/admin testados em Mongo descartável. A edição da descrição persistiu após reload na CI #50. Não foi usado staging nem testada edição de nós, importação persistida ou submissão ponta a ponta no browser. | Expandir para edição de nó, importação, exercício/submissão e histórico em ambiente descartável. |
| G — staging e lançamento | BLOQUEADA POR GATES OPERACIONAIS | Planos G0–G7 lidos. Não há confirmação pública suficiente para reproduzir Host key verification failed; nenhum segredo, SSH, Coolify ou VPS foi alterado/acessado. Nenhum gate G3–G6 foi executado. | Dono da infraestrutura valida host key/configuração e aprova gates individualmente, com CI verde no SHA e plano de rollback. |

## Backlog

- Aguardar CI #51 (dependência E2E nos deploy jobs) e CI #56 (import persistente/idempotente); os testes usam somente Mongo descartável.
- Cobrir editor de nó/blocos, importação persistida e submissão/progresso em browser usando somente QA descartável.
- Avaliar navegação por teclado e axe; fazer inspeção visual real quando houver browser local utilizável.
- Considerar budgets automáticos de bundle após estabilizar e observar a quantidade de chunks/requests.
- Com autorização do responsável, reproduzir erro de host key em contexto seguro e comparar fingerprint pública sem revelar ou trocar credenciais.
- Retomar homologação G0–G7 somente sob aprovações e dados isolados exigidos nos runbooks.

## Salvaguardas

Nenhum acesso ou escrita em Mongo real, migração, seed real, backup/restore, deploy, Coolify, VPS, SSH/firewall, secret ou Dev Forge. PRs permanecem abertos; nenhum merge automático.
