# Fase 2.1A.12B.6 — Relatório final de contratos fundamentais

**Escopo:** análise e documentação local. Nenhuma implementação, migração, mudança de dados, consulta de infraestrutura, execução de aplicação ou aprovação arquitetural ocorreu.
**Conclusão proposta:** contratos fundamentais especificados para deliberação; decisões de produto, evidências de cobertura e baseline operacional continuam bloqueando qualquer alteração funcional.

## A. Resumo executivo

Esta fase converteu as hipóteses preferenciais dos ADRs 001, 005 e 006 em contratos verificáveis e delimitou as condições em que podem operar sem assumir transação multidocumento:

1. A revisão editorial é recomendada por trilha, atribuída pelo servidor e confirmada por CAS em documento de controle. A revisão vencedora aponta a uma revisão imutável; conflitos são explícitos e mantêm o draft.
2. CAS editorial, CAS de publicação, lease, fencing e idempotência têm papéis diferentes. Lease sem token monotônico no ponto de commit não impede worker antigo; CAS de head não torna coerente uma fonte montada de documentos vivos.
3. Snapshot é coerente quando deriva de revisão comprometida imutável com dependências globais versionadas. O método atual de comparar contagens não é suficiente. Todos os writers precisam migrar ou ser bloqueados antes da ativação; a cobertura completa ainda não está provada.
4. Publicação recomendada é uma generation imutável da trilha inteira com manifest/chunks privados, selagem e um único CAS de `active_generation_id`. `ACTIVE` deve ser derivado do único head, não replicado num segundo status. Quizzes não terão segundo head por padrão; publicação independente exigiria composição na generation da trilha ou uma decisão de identidade composta.
5. Separação de dados exige draft/candidate e gabaritos privados, principals distintos, projeções DTO por allowlist, testes negativos e cache por geração/audience. O código contém DTOs que aceitam extras e serializer genérico por denylist; grants reais não foram comprovados.
6. Sessões e tentativas devem fixar geração/definição no servidor para leitura e avaliação reproduzíveis. Duração, conclusão tardia, revogação e histórico são escolhas pedagógicas/privacidade pendentes.
7. Sem dual-write canônico durante a migração. Fazer adapters para fonte única, shadow candidates privados e comparação somente leitura. Se um writer/reader antigo não puder ser bloqueado, o cutover permanece proibido.
8. ADR-008 permanece bloqueado: produção e digest/runtime não estão comprovados; esta fase não consultou infraestrutura, conforme instrução.

## B. Git e isolamento

| Item | Evidência |
|---|---|
| Base exata | `5cd10aaae355ba93efee962f4287af973b8421e5` |
| Branch criada | `codex/fase2-1a-12b6-core-contract-deliberation` |
| Worktree | `C:\Users\Joao\.codex\worktrees\trilhacode-fase2-1a-12b6-core-contract-deliberation\trilhacodeprod` |
| Preparação | Worktree criada sem checkout de arquivos, sparse-checkout configurado antes de materializar a base técnica e documentação. |
| Source B.5 | `codex/fase2-1a-12b5-adr-decision-review`, limpa em `5cd10aaae355ba93efee962f4287af973b8421e5` antes do trabalho. |
| Estado final | Oito arquivos Markdown commitados localmente; worktree verificada limpa depois do commit. O SHA completo é o `HEAD` verificável da branch desta fase. |

O checkout original e outras worktrees não foram alterados. Os diretórios protegidos não foram materializados nesta worktree.

## C. Fontes examinadas e confiança

- Sete documentos B.5 lidos integralmente: revisão ADR-001, ADR-005, ADR-006, ADRs restantes, matriz de dependências, pacote de aprovação e relatório.
- ADRs originais 001–008 consultados; todos os originais permanecem Proposed. B.3/B.5 mantém as oito decisões PENDING_APPROVAL.
- Código consultado por objetos Git no baseline técnico `e5bf3147a7f9a5ee02e1a011ffcbf1fb7e0cc636`, sem materializar arquivos executáveis na worktree: `tracks.py`, `nodes.py`, `blocks.py`, `relations.py`, `taxonomy.py`, `imports.py`, `versions.py`, `immutable_publications.py`, `activities.py`, `activity_publications.py`, `progress.py`, `content.py`, `serialization.py`, `database.py`, `indexes.py`, rotas de conteúdo/taxonomia/atividade e testes de tentativa.
- PoC/homologação mencionada em fases anteriores: evidência experimental do harness, não evidência de integração, papéis, schema ou runtime da aplicação.
- `OBSERVED` = comportamento do commit estático lido; não prova execução/implantação. `PROPOSED` = contrato sugerido. `ASSUMPTION` = depende de premissa explícita. `OPEN_DECISION` = exige produto/segurança/owner. `BLOCKED` = sem evidência necessária.

## D. ADR-001 — revisão e concorrência

**Proposta:** agregado editorial por trilha; revisão e sequência monotônicas server-side; candidata privada copy-on-write; CAS único do revision head; conflitos explícitos; sem rebase silencioso. Controlar catálogo global e taxonomias semânticas por versões separadas fixadas na generation.

**Razão:** os readers compõem trilha/nós/blocos/relações, enquanto CRUD atual grava coleções separadas. Publicação atual modifica filhos antes do update final (`tracks.publish_track`), restore apaga/reinsere em lotes e snapshot compara cardinalidade. Há risco concreto no desenho estático; não se afirma incidente real.

**Contrato:** `CommitEditorialRevision(track_id, expected_revision_id/seq, operation_id, fingerprint, actor, payload, fence?)`. Candidata/manifest ficam privadas; somente CAS condicionado a revisão-base/fence aumenta seq e torna a revisão corrente. Sequência `base+1` só é comprometida no CAS, então concorrentes perdedores não criam gaps na cadeia. Uma restauração cria revisão nova.

**Retry:** identidade lógica estável + fingerprint igual reproduz resultado via ID/lineage/receipt retidos; chave com payload divergente dá conflito. Se a prova foi eliminada ou é ambígua, `RECONCILIATION_REQUIRED`, nunca reaplicação cega. Retenção de lineage/receipt depende do ADR-004.

**Limite:** atomicidade de um documento não é transação multidocumento nem garantia de durabilidade/failover. Escritas de chunks confirmadas antes do CAS; write concern, journaling e topologia futura ainda precisam de evidência e aprovação.

## E. Writers e coexistência

Inventário no snapshot cobre CRUD de trilhas, ordenação global, publicação, nodes e duplicação, blocks, relações, taxonomias/tags/block types, importação, restore, exclusão, tentativas e progresso. Jobs/scripts externos e todas as versões implantadas não foram exaustivamente demonstrados.

Import tem lease/owner verificado em fases, mas a escrita de conteúdo é sequencial e não recebe fence individual em cada mutação. Restore usa lease de job, mas `apply_snapshot` faz deletes/inserts em lotes sem CAS de owner por write. Lease cooperativa não é fence. `delete_track` tem cascata que também alcança progresso/tentativas; retenção e exclusão precisam ser separadas.

**Recomendação de transição:** instrumentação para descobrir; command layer como única fonte canônica; adaptar todos writers; congelar/quiescer e bootstrap de revisão coerente; drenar/revogar versões antigas; shadow builder em namespace privado sem efeitos públicos; migrar readers/cache por trilha; cutover apenas com zero bypass demonstrado. Dual-write de conteúdo é rejeitado sem outbox e recuperação formal, que não fazem parte desta proposta. Writer desconhecido ou processo antigo apto a escrever bloqueia ativação.

## F. CAS e fencing

- CAS editorial: escolhe um sucessor da revisão-base.
- CAS de publicação: escolhe um sucessor do active head.
- Lease: reduz concorrência/trabalho duplicado, mas expira.
- Fencing token: monotônico, validado no commit canônico, rejeita worker stale.
- Idempotency key/fingerprint: identifica/reproduz intenção lógica.
- Lock administrativo: coordenação humana, sem garantia de estado.

Eles não se substituem. Candidate stale pode somente escrever seu namespace privado; não pode alterar controle ou dados canônicos. Publisher depende de source revision ainda corrente e active head esperado. Detalhes e cenários estão no [`protocolo de revisão`](./editorial-generations-phase-2-1a-12b6-revision-protocol.md) e [`cenários de falha`](./editorial-generations-phase-2-1a-12b6-failure-scenarios.md).

## G. Snapshot coerente

Coerência exige source revision imutável e comprometida, referências de taxonomy/catalog versionadas, manifest fechado, contagens/referências/digests validados e CAS que confirme revisão-base corrente. A leitura antes/depois de dados vivos só seria suficiente após cobertura comprovada de todos os writers; essa cobertura não existe no snapshot. Comparar contagens não detecta alteração de conteúdo com mesma cardinalidade. A preparação atualmente encontrada em `immutable_publications.py` declara `source_consistency="unverified"`, `activation_eligible=False`; portanto não é geração ativável.

## H. ADR-005 — fronteira público/privado e DTOs

“Learner-safe” não é sinônimo de anônimo. Texto didático, ordem e alternativas aprovadas podem ser apresentados ao aluno autenticado; gabaritos, rubricas, drafts, operation/fence, autoria interna e dados de progresso/tentativa ficam privados ou em domínio separado.

O código atual tem `content.APIModel` com `extra="allow"` e serializer genérico que remove campos privados conhecidos (denylist); `public_activity` é uma allowlist positiva localizada. Não foram comprovados roles/grants de produção e há cliente Mongo compartilhado no código auditado. Não afirmar isolamento real.

**Proposta de defesa em profundidade:** candidates/drafts privados; definições privadas de avaliação em coleção/partição protegida; principal public reader sem grant privado; evaluator separado; DTO versionado e allowlist; schema/capability desconhecida falha fechada; auditoria de todos readers, previews, buscas, logs, erros e caches. Collection-level grants não filtram documents por generation; público não deve ter grant sobre candidates privadas. Escolha “mesmo DB vs DB separado” requer threat model e evidência operacional.

## I. ADR-006 — generation e ativação

Generation inicial por trilha inteira, manifest/chunks limitados e imutáveis; dados privados e learner-safe separados. Estados candidate propostos: PREPARING → VALIDATING → READY ou REJECTED; `ACTIVE` e `SUPERSEDED` são derivados, não armazenados como autoridade paralela. `editorial_control.active_generation_id` é único head público.

Ativação valida READY, digests/referências/schema, source revision corrente, expected active generation, actor, operation e fence; um CAS único muda head/publication_seq. Crash antes do CAS deixa candidate inativa; crash depois deixa generation íntegra ativa e retry reproduz receipt. Leitor resolve head uma vez e somente busca chunks desse ID; falta/corrupção/schema incompatível falha fechado sem consultar dados mutáveis.

Recomendação para quiz: não manter ponteiro público independente. Alteração isolada de quiz é nova generation composta da trilha; se produto exigir independent release, precisa identidade composta e provas de compatibilidade, decididas separadamente.

## J. Integração dos conceitos

`revision_id/seq` = estado editorial comprometido. `generation_id` = projeção publicável. `schema_version` = formato interpretável. `taxonomy_refs` = dependências semânticas globais. `session_id` = pin server-side de estudo. `activity_definition_id/evaluation_version` = objeto privado usado para avaliar. `operation_id` = replay. `fencing_token` = época de operação longa.

Uma alteração cria nova revisão; builder converte revisão para geração; CAS altera head; reader resolve geração; sessão conserva pin; tentativa guarda definition/evaluator original. IDs não são intercambiáveis.

## K. ADR-002 — sessão, progresso e avaliação

Recomenda-se sessão criada/resolvida pelo servidor com geração fixada; attempt guarda geração, definition ID e versão de evaluator. O snapshot já persiste `published_version_id` por tentativa e avaliação busca essa versão (`activities.py`), mas não fixa árvore/navegação completa nem sessão. Progresso legado usa IDs de nós/blocos sem geração comprovada. Não associar progresso histórico por inferência.

Produto precisa definir duração/retomada, troca após publicação, submissão tardia, retirada urgente, links antigos, revogação e política de notas/histórico. O teste futuro deve iniciar tentativa em A, publicar B, submeter e demonstrar avaliação privada de A (salvo revogação explicitamente aprovada).

## L. ADR-003 — taxonomias

Semântica de bloco, capabilities/rendering/evaluation, ordem, relação/pré-requisito e metadado que muda navegação deve ser congelada/versionada. Rótulo só pode ser dinâmico quando produto/frontend provarem que não muda significado. Tags/taxonomies/block_types existem no snapshot; categorias como difficulty, competencies/objectives não foram confirmadas por evidência nesta fase. Inventário por campo e consumidores permanece decisão antes de backfill.

## M. ADR-004 — retenção

Geração não é coletável enquanto ativa ou referenciada por sessões, tentativas, progresso, history, receipts, restore ou auditoria/holds. O grafo de referência precisa incluir conteúdo, políticas de privacidade e operações concorrentes. Não há prazo numérico. GC permanece desabilitado até inventário completo, aprovação de produto/privacidade/jurídico, grace period e teste de corrida. Recomendação: tombstone/revogação e purge são ações distintas.

## N. ADR-007 — sequência de migração

Instrumentar e fechar inventário → comando central e revisão/fence → roles/partição private/public → writers adaptados e antigos bloqueados → snapshot/backfill privado sem pointer → comparação shadow somente leitura → readers e caches pinados → avaliação/sessões → cutover CAS → restore por nova generation → desligar legado após prova de zero bypass. Flags separadas começam desligadas; nenhuma etapa é ativada por este documento. Antes do cutover, rollback pode manter legado se ele ainda é fonte coerente; depois, operar com generation ou modo read-only/503, sem fallback live.

## O. ADR-008 — gate operacional

Continua `Proposed` e bloqueado por evidência. Fase 12B.4B concluiu baseline apenas parcialmente: staging com deployments históricos, sem digest/container/rota/tráfego ativos comprovados; produção não identificada. Fase 12B.6 não consultou Coolify, GHCR, bancos ou ambientes (proibido). Nenhuma linha técnica foi escolhida. Antes de código: owner confirma alvo, SHA+digest ativos, estratégia release/branch e plano de reconciliação; auditar contratos contra essa revisão.

## P. Contradições e bloqueios críticos

1. **Atomic CAS não resolve origem incoerente:** ADR-006 depende de ADR-001 e de closure dos writers.
2. **Role de coleção não faz filtragem por head:** candidate privado e published learner-safe precisam fronteira distinta ou reader service aprovado como trusted boundary.
3. **Unidade de trilha vs reorder/taxonomia global:** requer catálogo/taxonomy revision além de track revision.
4. **Quiz independente vs head único:** requer decisão pedagógica; não introduzir segundo pointer por conveniência.
5. **Replay vs GC:** receipt/lineage precisa reter prova pelo horizonte aprovado em ADR-004.
6. **Rollback vs legacy:** pós-cutover fallback live reabre risco P1; recuperação pode ser read-only/503.
7. **Deployment:** ADR-008 bloqueia roadmap de runtime mesmo que contratos sejam aprovados.

## Q. Decisões humanas necessárias

Prioridade: (1) unidade da revisão e catálogo global; (2) conflito e freeze/draft; (3) estratégia de compatibilidade e bloqueio de writer antigo; (4) separação de roles/collections; (5) generation de trilha e regra de publicação de quiz; (6) pin/duração/revogação da sessão; (7) taxonomy por campo; (8) retenção/legal/privacy; (9) baseline operacional e owner do cutover. Nenhum item recebe aprovação automática. A ficha em [`decisões humanas`](./editorial-generations-phase-2-1a-12b6-human-decisions.md) inclui alternativas, dependências e maturidade.

## R. Critérios de teste e próxima fase

Os 24 invariantes estão associados a testes conceituais em [`invariantes integrados`](./editorial-generations-phase-2-1a-12b6-integrated-invariants.md); 15 cenários negativos estão em [`cenários de falha`](./editorial-generations-phase-2-1a-12b6-failure-scenarios.md). Não foram executados nesta fase. A próxima ação é deliberar decisões de produto/segurança e obter o baseline operacional sanitizado; só então aprovar escopo de uma primeira fase passiva de instrumentação. Não iniciar alteração de publish/readers/backfill.

## S. Arquivos produzidos

1. [`revision-protocol.md`](./editorial-generations-phase-2-1a-12b6-revision-protocol.md)
2. [`writer-coexistence.md`](./editorial-generations-phase-2-1a-12b6-writer-coexistence.md)
3. [`public-private-boundary.md`](./editorial-generations-phase-2-1a-12b6-public-private-boundary.md)
4. [`generation-contract.md`](./editorial-generations-phase-2-1a-12b6-generation-contract.md)
5. [`integrated-invariants.md`](./editorial-generations-phase-2-1a-12b6-integrated-invariants.md)
6. [`failure-scenarios.md`](./editorial-generations-phase-2-1a-12b6-failure-scenarios.md)
7. [`human-decisions.md`](./editorial-generations-phase-2-1a-12b6-human-decisions.md)
8. Este relatório.

## T. Validações e limitações

Validações documentais concluídas: `git diff --check` sem erros; oito arquivos da fase, todos Markdown; links relativos locais resolvidos; 21 referências distintas de arquivo/linha verificadas contra o objeto Git `e5bf…`; oito ADRs originais continuam Proposed; as oito linhas da matriz original continuam PENDING_APPROVAL; paths protegidos ausentes da worktree; scan de padrões de credenciais sem correspondências; nenhum código funcional no diff; worktree limpa após commit. Não foram executados testes da aplicação, Docker, MongoDB, workflows ou acesso à infraestrutura.

## U. Segurança e operações

- Nenhum segredo, dado pessoal ou conteúdo curricular protegido é necessário nos documentos.
- Nenhum arquivo foi materializado nos diretórios protegidos `docs/courses/trilhacode/` e `docs/migracao/`.
- Nenhuma alteração foi feita no repositório principal remoto, executor MongoDB, Coolify, deploy, branches remotas, banco ou feature flag.
- Apenas objetos Git locais foram lidos; nenhum processo/serviço foi executado.

## V. Veredito

**CONTRATOS ESPECIFICADOS — DELIBERAÇÃO HUMANA NECESSÁRIA.** As recomendações de revisão, fronteira público/privado e publicação estão precisas o bastante para avaliação, mas não liberam implementação. Inventário de writers em runtime, papéis reais, taxonomias por campo, políticas pedagógicas/retention e baseline operacional permanecem gates.
