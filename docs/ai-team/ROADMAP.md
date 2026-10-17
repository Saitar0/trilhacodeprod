# Roadmap técnico

Atualizado em 17/10/2026 a partir de main (27a98964) e evidências dos PRs/CI desta missão. Status distinguem validação local, CI e homologação real.

| Frente | Status | Evidência verificada | Próximo critério |
| --- | --- | --- | --- |
| A — qualidade e confiabilidade | CONCLUÍDA | PR #9 adiciona Mongo descartável com URI local/direct-only e valida Compose sem iniciar serviços. CI #18 passou backend, frontend e Compose. | Revalidar após merge manual. |
| B — testes E2E | CONCLUÍDA NO ESCOPO SELECIONADO | PR #12 usa Mongo efêmero e seed de CI. CI #45 passou aluno, navegação admin e checks 360/390 px; #50 confirmou persistência da edição admin e #51 passou as dependências dos deploy jobs, que foram pulados. CI #60 passou submissão/persistência do aluno; CI #70 passou prévia sem mutação, importação persistida e edição de nó após reload. Revisor independente aprovou o fluxo de edição. | Ampliar cobertura para histórico/fluxos secundários em futura missão. |
| C — experiência/responsividade | CONCLUÍDA COM ESCOPO LIMITADO | CI #45 não encontrou overflow horizontal no catálogo, overview e reader em 360 e 390 px. Sem browser desktop local para inspeção visual. | Inspeção visual/teclado e acessibilidade em uma rodada com navegador utilizável. |
| D — desempenho frontend | CONCLUÍDA | PR #10 reduziu chunk do catálogo Lucide de 799.578 B / 147,81 KiB gzip para 213.071 B / 50,78 KiB gzip (~65,7% menos no chunk). CI #19 passou. Build usa cerca de 1.593 chunks sob demanda (~1,35 MB bruto somado). | Monitorar requests e regressões do build após integração. |
| E — backend, segurança e integridade | CONCLUÍDA PARA OS ACHADOS DESTA MISSÃO | PR #11 fecha leituras diretas de trilhas privadas (CI #21). PR #13 valida formato/valores e tamanho BSON de documentos gerados antes do planejamento; 33 testes locais, CI #48 e revisão independente passaram. PR #14 prova promoção/revogação em sessão ativa; CI #46 passou. Auditoria de auth/CORS/proxy não encontrou falha adicional reproduzível. | Ampliar matriz para rotas menos cobertas em novo conjunto de testes de integração. |
| F — homologação funcional | PARCIAL | Edição de descrição em browser persistiu após reload na CI #50. PR #15 cobre dry-run sem mutação, import persistente e reimport idempotente; CI #59 passou. PR #12 cobre envio de exercício na UI e persistência (CI #60), além de prévia/importação e edição de nó com reload (CI #70). Não foi usado staging. | Cobrir histórico e executar homologação mais ampla somente em QA descartável. |
| G — staging e lançamento | BLOQUEADA POR GATES OPERACIONAIS | Planos G0–G7 lidos. Não há confirmação pública suficiente para reproduzir Host key verification failed; nenhum segredo, SSH, Coolify ou VPS foi alterado/acessado. Nenhum gate G3–G6 foi executado. | Dono da infraestrutura valida host key/configuração e aprova gates individualmente, com CI verde no SHA e plano de rollback. |

## Backlog

- Concluído nesta missão: E2E de submissão e edição de nó/bloco via importação, em PR #12/CI #70.
- Cobrir histórico usando apenas banco QA descartável.
- Avaliar navegação por teclado e axe; fazer inspeção visual real quando houver browser local utilizável.
- Considerar budgets automáticos de bundle após estabilizar e observar a quantidade de chunks/requests.
- Com autorização do responsável, reproduzir erro de host key em contexto seguro e comparar fingerprint pública sem revelar ou trocar credenciais.
- Retomar homologação G0–G7 somente sob aprovações e dados isolados exigidos nos runbooks.

## Salvaguardas

Nenhum acesso ou escrita em Mongo real, migração, seed real, backup/restore, deploy, Coolify, VPS, SSH/firewall, secret ou Dev Forge. PRs permanecem abertos; nenhum merge automático.
