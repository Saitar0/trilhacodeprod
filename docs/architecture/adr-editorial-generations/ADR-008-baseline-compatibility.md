# ADR-008 — Seleção do baseline técnico e compatibilidade de branches

**Status:** Proposed
**Tipo:** gate para implementação; baseline ainda não escolhido.
**Referências lidas em 2026-10-28:** main 22dca64556338a8fa9aaa89ce627a4f4af72317d; staging fff85218fd71b164dc7465ca72d22b4a53232f49; snapshot auditado e5bf3147a7f9a5ee02e1a011ffcbf1fb7e0cc636; auditoria documental 4805e3caab18f183c37375d23af1b2e12a425d1b.

## 1. Contexto

O B.2 auditou e5bf… porque contém a PoC e integrações técnicas. Esse commit tem base main 22d… e inclui uma série de mudanças de backend/frontend não presentes em main/staging. Leitura local dos refs confirmou que os caminhos backend/frontend selecionados diferem entre main e staging apenas em backend/settings.py; e5bf… difere amplamente, incluindo activities, sessions, imports/progress, PoC, immutable publications e consumidores frontend. O compare remoto do commit e5 retornou 404; não há evidência de que e5 esteja implantado. Evidência: B.2 audit lines 4-7 e comparação local de blobs/paths; confiança alta para refs locais/remotos consultados em 2026-10-28, desconhecida para deploy.

## 2. Problema

Implementar contra snapshot não implantado pode planejar APIs, schema ou progresso inexistentes no alvo. Escolher main/staging sem validar código do ambiente também pode divergir do runtime real.

## 3. Requisitos

- Baseline deve refletir código implantado e alvo da mudança, com SHA/digest verificável.
- Comparar contratos de backend, frontend, schema/indexes, auth e jobs.
- Não inferir ambiente implantado pela branch nominal.
- Nenhum merge/rebase nesta decisão documental.

## 4. Alternativas

| Opção | Benefício | Limite |
|---|---|---|
| A. e5bf… auditado | Inclui PoC e trabalho mais recente | Não está em main/staging observados; estado implantado não provado |
| B. main | Referência principal conhecida | Conteúdo remoto não contém todas as integrações auditadas |
| C. staging | Pode ser candidato de validação | Branch difere de main; implantação não provada |
| D. Baseline por ambiente com SHA/digest e objetivo de release | Evita inferir a partir de nome de branch | Exige acesso autorizado a evidência de deploy e alvo explícito |

## 5. Critérios de avaliação

Proveniência implantada, contrato de release, compatibilidade de schema e frontend, possibilidade de rollback, ownership e escopo do primeiro piloto.

## 6. Recommended Decision

Recomenda-se D como política e bloqueio da primeira implementação até que owner do ambiente confirme o SHA de aplicação e digest de imagem implantados no alvo, o branch/linha de release desejado e o escopo do rollout. Reauditar contra essa revisão; não cherry-pick/merge automático da auditoria para main/staging.

## 7. Matriz de compatibilidade lida

| Área | e5bf… auditada | main 22d… | staging fff… | Divergência observada / impacto |
|---|---|---|---|---|
| Schemas e índices | Inclui alterações de índices e schemas de atividade/progresso | Base mais antiga | Em comparação com main, apenas settings.py mudou no escopo consultado | e5 contém schema adicional; revalidar contra deploy |
| Escritores e serviços | Inclui CRUD e alterações de tracks/nodes/imports/versions | Sem vários componentes posteriores | Conteúdo de aplicação selecionado coincide com main | Integração e5 não é baseline comprovado |
| Leitores/atividades | Adiciona routes/services activities e sessions | Ausentes | Não presentes no diff app selecionado | Contratos de quiz/session podem não existir no alvo |
| Publicação/restore | Inclui immutable_publications e guarda de elegibilidade | Não presente | Não presente no snapshot comparado | Não assumir comportamento de e5 em runtime |
| Import/progresso | Serviços e rotas alterados | Versão base | Aplicação selecionada igual a main | Revalidar jobs/import idempotency e progress model |
| Frontend | UI quiz, sessão, hooks, types e testes alterados | Antigo | Aplicação selecionada igual a main | Não presumir payloads e cache em ambiente |
| Autenticação | e5 altera auth/security/routes | Base | Sem diferença selecionada reportada | Roles/claims do alvo exigem revalidação |
| Jobs/scripts | Migrations/manage/seed e import caminhos presentes no snapshot | Ref de aplicação mais antiga | Igual a main em seleção consultada | Operações administrativas podem contornar protocolo |
| Configuração operacional | main/staging diferem em backend/settings.py no escopo | settings base | settings distinto | Revisar configuração por ambiente; sem conclusão sobre deploy |

Esta matriz resume leitura estática de objetos Git. Não demonstra qual ref está implantada, nem compara tráfego, secrets ou infraestrutura.

## 8. Justificativa

Uma auditoria técnica válida não é automaticamente o alvo de implementação. E5 adiciona mudanças funcionais relevantes, inclusive sessões e atividades, enquanto nenhuma prova de deploy foi encontrada.

## 9. Consequências positivas

Evita implementar API inexistente; exige compatibilidade demonstrável; conserva branches sem integração automática.

## 10. Consequências negativas

Bloqueia trabalho funcional até obter proveniência do ambiente e pode exigir auditoria adicional.

## 11. Impacto na migração

Roadmap só avança para código depois do gate B.4 (aprovação e baseline). Inventários de e5 são mapas de referência, não lista final para produção.

## 12. Compatibilidade

Toda mudança futura deve informar baseline exato, matriz de payload/schema, ambientes-alvo, rollout e plano para branch principal. Não fundir histórico para “alinhar” evidências.

## 13. Estratégia de rollback

Manter commits de implementação isolados e não publicar até reauditoria. Se baseline escolhido divergir, descartar/replanejar alterações não mescladas; não rebasear sobre outra branch sem autorização.

## 14. Testes obrigatórios

Contract tests e schema diffs contra SHA escolhido; frontend build/tests para mesma linha; smoke de configuração; validação de migrations em DB descartável; teste de versão implantada e digest no gate operacional.

## 15. Critérios de aceitação

SHA e digest do alvo registrados por owner autorizado; main/staging e target compare documentados; dependências de feature presentes; auditoria revisada contra baseline; autorização do escopo funcional.

## 16. Decisões dependentes

Bloqueia todos os ADRs que dependem de interfaces atuais e todas as fases de código.

## 17. Perguntas para aprovação humana

Qual ambiente é o alvo? Qual SHA/digest está implantado? A implantação desejada segue main ou staging? As mudanças de e5 foram implantadas por mecanismo externo? Qual componente possui autoridade sobre a release?

## 18. Approved Decision

Nenhuma. Baseline de implementação permanece bloqueado.

## 19. Evidência e confiança

SHAs main/staging consultados por GitHub API e ls-remote em 2026-10-28; objetos e5/main/staging comparados localmente sem escrita. Nenhuma evidência de deploy foi consultada. Conclusão “e5 não comprovado como implantado” é alta; “qual ref está implantada” é desconhecida.

## 20. Próximo gate

Solicitar evidência de deploy autorizada (SHA + image digest + ambiente) e aprovar baseline antes de alterar qualquer código executável.
