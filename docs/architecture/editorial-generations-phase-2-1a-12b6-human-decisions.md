# Fase 2.1A.12B.6 — Deliberação humana e maturidade dos contratos

**Nenhuma decisão está aprovada por este documento.** Os oito ADRs originais continuam `Status: Proposed`; a matriz de B.3/B.5 continua com oito `PENDING_APPROVAL`. O estado operacional do ADR-008 continua bloqueado. As recomendações abaixo são opções informadas para uma decisão posterior.

## 1. Ordem recomendada de deliberação

| Ordem | Decisão | Recomendação técnica provisória | Alternativas reais | Consequências e risco | Dependências | Categoria | Estado desta ficha |
|---:|---|---|---|---|---|---|---|
| 1 | Unidade e regra de revisão (ADR-001) | Revisão monotônica por trilha + versão separada de catálogo/taxonomias com impacto global; servidor atribui seq; CAS/fence; conflito explícito sem rebase | Por documento/módulo; híbrido composto; serialização/lock | Agregado mais coerente, porém conflitos mais amplos; dependência em cobertura de todos writers e quiesce | Baseline escolhido, inventário de writers, papéis e produto (edição colaborativa) | Técnica/produto | `REQUIRES_CLARIFICATION` quanto ao escopo; contrato técnico especificado |
| 2 | Política de conflito e coexistência legacy (ADR-001/007) | Uma fonte canônica; command layer; sem dual-write; bloquear/drain writers antigos; API reporta conflito e preserva draft | Instrumentar apenas; adaptar incrementalmente mantendo legacy; outbox dual-write | Pode exigir freeze/janela e adaptação abrangente; writer desconhecido bloqueia cutover | Decisão 1; baseline/deploy; inventário de jobs e scripts | Operacional/técnica | `NEEDS_TECHNICAL_EVIDENCE` |
| 3 | Fronteira de dados e principals (ADR-005) | Draft/candidate e gabarito em namespace privado; principals separados; DTO allowlist; falha fechada | Mesmo DB/coleções; DB separado; filtro em controller | Menor privilégio versus custo operacional; grants reais são desconhecidos; collection grants não fazem row filtering | Baseline, mapa de roles/routes/cache, threat model | Segurança | `NEEDS_TECHNICAL_EVIDENCE` para selecionar o mecanismo real |
| 4 | Unidade de publicação e quiz (ADR-006) | Generation da trilha inteira, incluindo definition/evaluation ref; uma única autoridade de head | Por módulo; quiz com publication pointer separado; geração composta | Coerência exige publicar quiz com trilha; produto pode exigir publicação de quiz independente; segundo head permite combinações parciais | Revisões, taxonomias, sessão/progresso, classificação de quiz | Técnica/produto | `REQUIRES_CLARIFICATION` sobre independência do quiz |
| 5 | Sessão e tentativa (ADR-002) | Server-side session fixa geração; attempt fixa definition/evaluator original | Seguir latest; pin por request; somente tentativa; híbrido | Coerência melhora; duração, revogação, UX e submissões tardias são produto | ADR-005/006, retention, frontend/progresso | Produto/privacidade | `REQUIRES_CLARIFICATION` |
| 6 | Semântica de taxonomias (ADR-003) | Fixar taxonomia que muda navegação/render/avaliação; labels dinâmicos apenas se provado não semântico | Snapshot integral; refs mutáveis; versões globais; split semântico/admin | Evita mudança histórica; exige classificação do campo e suporte de schemas antigos | Escopo da primeira trilha, inventário frontend/catalog, owners de produto | Produto/frontend | `REQUIRES_CLARIFICATION` campo a campo |
| 7 | Retenção/exclusão (ADR-004) | Nenhum GC até grafo de refs, obrigações e janela aprovada; separar conteúdo e PII; tombstone precede purge quando apropriado | Ilimitada; janela fixa; por referência; por curso | Reter custa/afeta privacidade; apagar cedo quebra avaliação/histórico | ADR-002/003/006; revisão privacidade/jurídica | Privacidade/legal/produto | `BLOCKED_BY_EVIDENCE` e decisão humana |
| 8 | Rollout, flags e rollback (ADR-007) | Fases pequenas e flags separadas off; private shadow only; cutover após writer+reader closure; sem fallback | Big-bang; shadow writes; por coorte | Menor risco incremental, mas longa coexistência; sem operação segura se bypass | ADR-001/005/006/008; owners e métricas | Operacional | `PENDING_APPROVAL`, gates especificados |
| 9 | Baseline, ambiente e release (ADR-008) | Não selecionar branch até confirmar alvo/release e reconcile com baseline implantado; linha de integração específica após prova | main; staging; snapshot auditado; integração controlada | Implementação no código errado pode não operar no runtime e quebrar contratos | Evidência sanitizada runtime/digest/commit, branch alvo e autorização | Operacional/infra | `BLOCKED_BY_EVIDENCE` |

Esta ordem é uma sugestão de dependência. ADR-008 é gate para qualquer alteração funcional mesmo que a deliberação de ADR-001 avance em paralelo.

## 2. Decisões que produto/código não resolve sozinho

| Pergunta | Recomendação técnica | Decisor necessário |
|---|---|---|
| Um editor em revisão-base antiga recebe conflito explícito e mantém seu draft? | Sim; sem rebase automático | Produto/editorial + UX |
| Editor pode trabalhar em módulos distintos sem conflito, ou trilha inteira é unidade inicial? | Track-wide é seguro para primeira composição; confirmar custo/colaboração | Produto/editorial |
| Quiz pode publicar separadamente da trilha? | Não criar segundo head no primeiro corte; atividade independente vira nova generation composta da trilha | Produto pedagógico |
| Aluno continua sessão de A após B? Até quando? | Manter A enquanto autorizada/referenciada; duração não definida | Produto/privacidade |
| Tentativa aberta A pode ser enviada após B? | Avaliar com A se não revogada; janela e exceções não definidas | Produto pedagógico |
| Como agir quando geração é retirada urgentemente? | Fail closed/revogar acesso, não retarget; definir autoridade e comunicação | Segurança + produto |
| Progresso legado sem geração verificável é associado a qual versão? | Não inferir; migração explícita ou continuar como legado separado | Produto/dados |
| Quais tags/metadados são pedagógicos e quais são apenas administrativos? | Classificar por campo/consumidor e versionar semântica | Produto + frontend |
| Quais conteúdos/avaliações podem ser purgados e quem aprova? | Nenhuma remoção física até policy e base legal/prazo aprovados | Privacidade/jurídico + produto |
| Qual ambiente/branch é alvo de primeira fase? | Só após baseline/digest/deploy e branch release confirmados | Owner operacional/release |
| Quem autoriza cutover e pausa de publicação? | Owner nomeado, checklist e evidência de rollback | Operações + segurança |

## 3. Maturidade atual dos contratos

| Contrato ou área | Classificação | Justificativa objetiva |
|---|---|---|
| `CommitEditorialRevision` | `NEEDS_TECHNICAL_EVIDENCE` | Modelo/CAS está definido, mas todos writers/identidades/runtime e write concern não foram comprovados. |
| Idempotência/replay de revisão | `NEEDS_TECHNICAL_EVIDENCE` | Lineage pode provar retry sem transação se retido; formato/índices/retention e failure semantics ainda não testados. |
| Import/restore como candidate revision | `NEEDS_TECHNICAL_EVIDENCE` | Código observado usa writes sequenciais e restore destrutivo; adapters e process inventory faltam. |
| Cutover/compatibilidade de writers | `NEEDS_TECHNICAL_EVIDENCE` | Rollout não pode bloquear processo antigo sem baseline e ownership de deploy. |
| Projeção learner-safe e privadas | `NEEDS_TECHNICAL_EVIDENCE` | Allowlist conceitual está definida; grants, coleções, rotas e caches reais por ambiente faltam. |
| Geração/selagem/CAS head | `NEEDS_PRODUCT_DECISION` | Contrato técnico sem transação está especificado; quizzes independentes e conteúdo de corte requerem produto; baseline operacional bloqueia rollout. |
| Resolução de sessão pinada | `NEEDS_PRODUCT_DECISION` | Autoridade server-side é recomendada; validade, expiração, retomar e revogar são política de produto. |
| Avaliação por definição original | `READY_FOR_HUMAN_DECISION` | Snapshot já tem pin limitado por tentativa; expandir para generation/evaluator é tecnicamente claro, mas autorização/política de atraso exige ADR-002/005. |
| Versões de taxonomia | `NEEDS_PRODUCT_DECISION` | Princípio é definido; classificação dos campos e consumidores não está completa. |
| Retenção/GC | `NEEDS_PRODUCT_DECISION` | Grafo e perguntas estão listados; prazo/obrigações não foram fornecidos; GC bloqueado. |
| Baseline de implementação/release | `BLOCKED_BY_OPERATIONAL_BASELINE` | 12B.4B não comprovou produção, digest/runtime/rota/tráfego; usuário proibiu reconsulta nesta fase. |

Um contrato classificado como pronto para decisão não está aprovado e não libera implementação. Todos os contratos que chegam a código dependem do baseline e da autorização específica.

## 4. Perguntas para registrar na ata de aprovação

Para cada item, registrar: decisão exata, opções consideradas, pessoa/área aprovadora, data, impacto, condições, ADR relacionado e se a aprovação se aplica somente ao escopo piloto. A aprovação de um ADR não deve ser interpretada como autorização de deploy, migração, feature flag ou mudança de schema.

## 5. Relação com ADRs originais

| ADR original | Status original | Triagem B.5 mantida | Observação desta fase |
|---|---|---|---|
| ADR-001 | Proposed | REQUIRES_CLARIFICATION | Contrato técnico mais preciso; inventory/fence de todos writers continua evidência bloqueante. |
| ADR-002 | Proposed | REQUIRES_CLARIFICATION | Pin de session+attempt especificado; expiração/revogação/progresso legado aguardam produto. |
| ADR-003 | Proposed | REQUIRES_CLARIFICATION | Taxonomia/catálogo global separados da revisão por trilha; matriz por campo incompleta. |
| ADR-004 | Proposed | BLOCKED_BY_EVIDENCE | Referências e obrigações não fechadas; GC permanece bloqueado. |
| ADR-005 | Proposed | PENDING_APPROVAL | Defesa em profundidade recomendada; papéis/grants efetivos não comprovados. |
| ADR-006 | Proposed | REQUIRES_CLARIFICATION | Single head e algoritmo CAS especificados; granularidade/quiz independente precisa produto. |
| ADR-007 | Proposed | PENDING_APPROVAL | Sequência sem dual-write especificada; baseline/owners bloqueiam execução. |
| ADR-008 | Proposed | BLOCKED_BY_EVIDENCE | Sem baseline operacional; não consultado novamente por restrição desta fase. |

`PENDING_APPROVAL` da matriz original não é editado por esta fase. Esta tabela é triagem analítica; não substitui nem atualiza os arquivos ADR/matriz anteriores.
