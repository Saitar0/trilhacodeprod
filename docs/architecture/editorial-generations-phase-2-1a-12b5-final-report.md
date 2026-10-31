# Fase 2.1A.12B.5 — relatório final da revisão arquitetural

**Resultado:** ADRs revisados e decisões preparadas para aprovação humana.
**Escopo:** documentação/análise somente; sem implementação, acesso a banco ou infraestrutura, execução de aplicação, mudança de flags ou aprovação automática.
**Baseline arquitetural usado nas referências de código:** `e5bf3147a7f9a5ee02e1a011ffcbf1fb7e0cc636`.
**Estado operacional herdado, sem nova consulta:** Fase B.4B, commit `ccc5ade1fc92f4532a820d0ade41c50555d19ffa`.

## 1. Resumo executivo

Os oito ADRs foram revisados à luz da auditoria B.2, contratos e invariantes B.3, evidências de baseline B.4/B.4A/B.4B e código referido no snapshot técnico. Os ADRs originais permanecem todos com `Status: Proposed`; a matriz original continua sendo a referência de `PENDING_APPROVAL`. As novas classificações no pacote são triagem preparatória, não decisão aprovada.

Recomendação técnica central: estabelecer primeiro uma revisão editorial única, monotônica, atribuída pelo servidor e comum a todos os writers de um escopo; gerar snapshot privado coerente; aplicar CAS e fencing; separar definição privada e projeção pública; selecionar uma geração imutável por um único head; fixar a geração nas leituras e avaliações; nunca retornar silenciosamente ao reader legado após cutover. A implementação continua bloqueada por questões de contrato/coexistência e pelo baseline operacional não comprovado.

Lacunas críticas explicadas nesta revisão: (1) como manter compatibilidade sem dual-write divergente durante adaptação de todos os writers/readers; (2) unidade de publicação quando quizzes têm versão publicada própria; (3) autoridade única de revisão/head; (4) horizonte e recuperação de receipts; (5) ciclo sessão↔retenção; (6) semântica de taxonomias globais; (7) identidade real do baseline implantado.

## 2. Git e isolamento

* Nova worktree: `C:\Users\Joao\.codex\worktrees\trilhacode-fase2-1a-12b5-adr-decision-review\trilhacodeprod`.
* Branch: `codex/fase2-1a-12b5-adr-decision-review`.
* Base exata: `ccc5ade1fc92f4532a820d0ade41c50555d19ffa`.
* Sparse-checkout foi configurado antes de materializar arquivos; paths protegidos `docs/courses/trilhacode/` e `docs/migracao/` permaneceram ausentes.
* A worktree de origem B.4B foi inspecionada como limpa; checkout original e outras worktrees não foram alterados.
* Os documentos desta fase são novos e exclusivos; o commit local será registrado após as validações, se todos os gates documentais passarem.

## 3. Fontes e grau de confiança

Foram lidos integralmente os relatórios B.2 (auditoria, arquitetura-alvo, rollout, riscos), B.3 (oito ADRs, contratos, invariantes, decisões, roadmap), B.4 (baseline, compatibilidade, fichas, gates e relatório), B.4A (evidências de runtime e revisão de ADR-008) e B.4B (runtime, OCI, roteamento, matriz, pedido de evidência, gates e relatório). Os oito ADRs originais também foram relidos.

As referências de arquivos/funções e linhas de código pertencem ao snapshot técnico `e5bf3147a7f9a5ee02e1a011ffcbf1fb7e0cc636`; o presente trabalho não assumiu que esse snapshot esteja implantado. Resultados da PoC MongoDB 7 (15 testes integrados, 26 unitários, sete guardas Docker) são evidência experimental reportada pelas fases anteriores e não foram repetidos. Evidência operacional do baseline é a conclusão B.4B e continua parcial.

## 4. Síntese por ADR

| ADR | Status original | Triagem B.5 | Recomendação resumida | Bloqueio principal |
|---|---|---|---|---|
| 001 — revisão/concorrência | Proposed | REQUIRES_CLARIFICATION | revisão server-side por trilha, snapshot coerente, CAS, fence, conflito explícito, retry idempotente | Compatibilidade com writers legados e modelo de transição; escopo e conflito |
| 005 — público/privado | Proposed | PENDING_APPROVAL | partição privada, principals mínimos, DTO allowlist, falha fechada | Roles atuais não foram comprovados; detalhar schema e endpoint/caches |
| 006 — publicação atômica | Proposed | REQUIRES_CLARIFICATION | candidata privada, validação/selagem, um CAS do head, reader pinned e sem fallback live | Unidade de publicação, fonte única do head, receipts e integração com 001 |
| 002 — sessões/progresso | Proposed | REQUIRES_CLARIFICATION | sessão fixada pelo servidor e avaliação contra atividade privada original | Política de produto para duração, submissões tardias, revogação e progresso |
| 003 — taxonomias | Proposed | REQUIRES_CLARIFICATION | congelar/versionar semântica pública; IDs distintos de rótulos/schema | Inventário e classificação campo a campo, incluindo dependências globais |
| 004 — retenção/exclusão | Proposed | BLOCKED_BY_EVIDENCE | retenção por referências/obrigações; sem GC até política e grafo completo | Referências e política de privacidade/legal não fechadas |
| 007 — migração gradual | Proposed | PENDING_APPROVAL | flags separadas off; writers antes de readers; backfill sem seleção; rollback sem live fallback | Revisar owners/métricas e autorizações separadas por etapa |
| 008 — baseline | Proposed | BLOCKED_BY_EVIDENCE | manter runtime não comprovado; escolher linha apenas após reconciliação/decisão | digest/container/produção/proveniência e compatibilidade ausentes |

Detalhes completos: [ADR-001](./editorial-generations-phase-2-1a-12b5-adr001-review.md), [ADR-005](./editorial-generations-phase-2-1a-12b5-adr005-review.md), [ADR-006](./editorial-generations-phase-2-1a-12b5-adr006-review.md), [demais ADRs](./editorial-generations-phase-2-1a-12b5-remaining-adrs.md) e [pacote de aprovação](./editorial-generations-phase-2-1a-12b5-approval-packet.md).

## 5. Concorrência editorial e escritores

A unidade recomendada para o primeiro escopo é a trilha agregada: árvore, relações, blocos, metadados semânticos e referências a atividades são lidos em conjunto. Um documento de controle server-side seria autoridade de revisão/fence; a CAS da revisão esperada decide o único vencedor. Revisão-base obsoleta resulta em conflito explícito, recomendavelmente HTTP 409 com código estável e sem dados privados; a edição do usuário permanece recuperável. Não há merge/rebase automático silencioso.

`operation_id` representa a operação lógica; fingerprint canônico liga a operação ao conteúdo. Mesmo ID + fingerprint igual retorna receipt/resultado; mesmo ID com fingerprint diferente conflita. Operações longas usam lease/fence crescente; writes tardios de worker antigo podem deixar somente candidatas privadas e não podem validar, selar ou selecionar. Recuperação exige verificar operação, fingerprint, fence e estado, não reexecutar cegamente.

Foram conectados aos contratos futuros: CRUD de tracks/nodes/blocks/relations e ordenação; questões/alternativas; taxonomias/tags/block types; duplicação/exclusão/arquivamento; import/jobs; publicação; restore; seeds/scripts/admin. Progresso, submissões, tentativas, notas e reviews são writers de dados de aluno, não writers editoriais, mas precisam referenciar geração/atividade fixa. A tabela de cobertura e testes está em [matriz de dependências](./editorial-generations-phase-2-1a-12b5-dependency-matrix.md).

**Lacuna de transição:** writers CRUD e publicação atuais podem alterar documentos públicos separadamente. Não se deve supor atomicidade ao dual-write entre legado e store de gerações. Recomendação: nenhum cutover para um escopo até seus writers e readers estarem cobertos; manter escopos ainda não migrados no caminho legado, isolados por escopo, sem misturar suas respostas com geração; candidato sombra escreve somente em namespace privado. Se a coexistência não puder ser isolada sem fonte dupla ou resposta mista, a etapa deve parar até um contrato adicional/outbox/estratégia de consistência ser aprovada e testada.

## 6. Segurança público/privado e avaliação

O estado atual observado não prova grants de MongoDB: aplicação auditada usa cliente compartilhado; schema genérico admite extras e serializer não é allowlist geral; conteúdo de atividade pública/privada coexiste no domínio auditado. Recomenda-se defesa em profundidade: armazenamento/partição de definições privadas, identidade pública sem leitura dessas definições, evaluator com privilégio específico, projeções com allowlist por tipo/schema e fail-closed para campo/tipo desconhecido. Cobrir catalog/detail/tree/node/search/activity/preview/cache/erro/log e endpoints legados.

O leitor público não recebe resposta correta, critério privado, feedback interno, hashes de controle, IDs de writer, dados administrativos ou campos desconhecidos. O cache incorpora geração e audiência; conteúdo privado não é armazenado no cache público. A recomendação não afirma que configuração atual satisfaz esses papéis.

Para aluno: sessão fixada server-side; cliente não escolhe geração livremente; atividade e tentativa conservam identidade/versionamento original; submissão tardia é avaliada pela definição privada correspondente, não pelo head atual. Produto deve decidir duração, renovação, versão antiga, retirada urgente, links, histórico de notas e progresso órfão.

## 7. Publicação atômica e conflitos ainda abertos

Publicar/restaurar exige origem coerente (001), dados privados protegidos (005), candidata completa e selada, e um único controle/head atualizado por CAS. Geração incompleta não é selecionável; chunk selado não muda; reader resolve head uma vez e usa somente aquele `generation_id`; missing/corrupt generation falha fechado sem buscar documentos vivos. Restore cria nova revisão/geração com `restored_from`; não reescreve a geração passada.

MongoDB standalone oferece atomicidade de uma escrita de documento, não transação de todos os chunks/coleções. Os chunks são privados até o CAS do controle. A proposta deve evitar segundo ponteiro mutável (`tracks.version`, estado da atividade) como autoridade concorrente.

**Unidade pendente:** recomendação inicial é geração da trilha inteira. O sistema histórico contém `published_version_id` para atividades, que pode permitir publicação independente; se produto exigir essa independência, a identidade versionada de atividade precisa fazer parte do token/sessão/manifesto. Um pointer de quiz independente não pode alterar silenciosamente o conteúdo de uma sessão.

## 8. Taxonomias, retenção e migração

IDs estáveis, rótulos de apresentação, versão de schema e versão semântica são conceitos separados. O snapshot confirma áreas como tags/taxonomies/block types; existência e significado de dificuldade, competências ou objetivos precisam de verificação antes de classificar. Campos que afetam ordenação, apresentação ou interpretação são congelados ou apontam a versão imutável. Campos administrativos não entram na projeção pública. A matriz campo/coleção proposta está em [demais ADRs](./editorial-generations-phase-2-1a-12b5-remaining-adrs.md).

Retenção depende de head ativo, sessões, tentativas, resultados, progresso, receipts, auditoria, restore e holds. Não propor prazo nem GC agora. Separar PII e conteúdo pedagógico quando compatível; exclusão/tombstone/anonimização é política de produto e privacidade. Até que grafo e autoridade sejam conhecidos, nenhuma geração candidata ou histórica é coletada.

Sequência de rollout proposta: baseline/decisões → instrumentação passiva → revisão/fencing compartilhados → roles/armazenamento privado → backfill idempotente sem head → shadow comparison somente privada → readers admin → reader aluno/sessão → seleção CAS → restore → observabilidade e desativação do legado. Flags independentes começam off. Cada fase tem autorização separada; rollback de código/flag não retorna à leitura mutável insegura.

## 9. Baseline e ADR-008

ADR-008 permanece `Proposed` e `BLOCKED_BY_EVIDENCE`. A conclusão B.4B é baseline parcialmente comprovado: staging teve deployments históricos associados ao SHA de staging, mas sem digest ativo/container/rota/tráfego; produção não foi identificada com segurança; recurso nomeado `trilhacode` não foi provado como produção; build G2 associado a `41dc470c567bae50b7ebcf0662d45d43863980c9` não prova runtime. Esta fase não repetiu consultas operacionais.

Não escolher automaticamente main, staging ou `e5bf...`; exigir baseline e matrix de compatibilidade revisados antes de qualquer código/runtime. A relação com deployment exige nova autorização e evidência sanitizada por autoridade de infraestrutura, conforme pedido documentado em B.4B.

## 10. Dependências, conflitos e gates

A [matriz transversal](./editorial-generations-phase-2-1a-12b5-dependency-matrix.md) define grafo sem ciclo e gates. Para quebrar a dependência mútua entre sessão e retenção: ADR-002 identifica referências; ADR-004 fecha política depois; GC fica proibido até ambos estarem aprovados. ADR-001 precede ADR-006. ADR-003 precisa ser contabilizado na revisão de origem. ADR-008 bloqueia runtime paralelamente, não impede a discussão conceitual.

Conflitos registrados: revisão/head duplicados; CAS vs snapshot de origem; atividade publicada independentemente; dual-write; sessão fixada vs retirada imediata; receipt vs retenção; rollback vs legacy reader; contagem por trilha vs taxonomia global; colisão na numeração das fases do roadmap anterior. Nenhum conflito é silenciosamente resolvido aqui.

## 11. Estratégia de testes futura

Nenhum teste de aplicação foi executado nesta fase. Antes de implementação, associar invariantes a:

* **Unitários:** revisão, conflitos, fingerprint/idempotência, schema/DTO allowlist, policy e estados.
* **MongoDB descartável:** índices, CAS, fencing, append-only, seal, receipt, grants e corrupção; não inferir suporte a transação multidocumento.
* **API/autorização:** contratos existentes, cliente antigo, papel público/admin/evaluator, campos desconhecidos, erros sem vazamento.
* **Concorrência:** CRUD concorrente, import×publish, restore×publish, candidate obsoleto, leitura A→B e resposta tardia.
* **Frontend/cache:** identidade de sessão, navegação, geração mista, erro de conteúdo retirado, cache por audiência/geração e progresso histórico.
* **Migração:** backfill repetido/interrompido sem pointer, contagem/hash, órfãos, comparação sombra sem efeitos e retomada.
* **Segurança:** tentativa de obter gabarito via toda rota/cache/preview, acesso de reader público às coleções privadas, logs e exceções.
* **Rollback:** falha antes/depois de seal/CAS, flag desligada, serviço reader indisponível, preservação da última geração válida e confirmação de ausência de fallback vivo.

Critério de aprovação de cada suite deve ser objetivo, vinculado ao invariante, com versão de baseline/fixture e sem dados reais.

## 12. Decisões e roadmap para aprovação

Pacote humano: [approval packet](./editorial-generations-phase-2-1a-12b5-approval-packet.md). Próximos passos documentais/organizacionais possíveis, ainda sem autorização de execução:

1. Reunião de decisão para ADR-001: unidade de revisão, conflito e modo de coexistência.
2. Revisão de segurança para ADR-005 e classificação por tipo de dado.
3. Decidir unidade publicável e autoridade única do head no ADR-006.
4. Decisões de produto para ADR-002/003 e de privacidade/negócio para ADR-004.
5. Tratar evidências do baseline e a linha de implementação no ADR-008 sob autorização operacional própria.
6. Aprovar ADR-007 e somente então autorizar fase de instrumentação passiva separada, delimitando arquivos, métricas e proibições.
7. Cada etapa de runtime, banco, backfill, reader, seleção e cutover requer autorização própria, gates e reversão.

**Colisão de nomenclatura:** roadmaps B.2/B.3 já associam parte de 12B.5 a etapas técnicas; esta fase usa B.5 para revisão documental dos ADRs. Não alterar roadmap anterior nesta entrega; governança deve escolher um esquema de IDs antes de criar work items de implementação.

## 13. Arquivos produzidos

* [ADR-001 — concorrência](./editorial-generations-phase-2-1a-12b5-adr001-review.md)
* [ADR-005 — dados público/privado](./editorial-generations-phase-2-1a-12b5-adr005-review.md)
* [ADR-006 — publicação](./editorial-generations-phase-2-1a-12b5-adr006-review.md)
* [ADR-002/003/004/007/008](./editorial-generations-phase-2-1a-12b5-remaining-adrs.md)
* [Matriz de dependências, escritores, leitores e invariantes](./editorial-generations-phase-2-1a-12b5-dependency-matrix.md)
* [Pacote de aprovação](./editorial-generations-phase-2-1a-12b5-approval-packet.md)
* Este relatório.

## 14. Validações e segurança

Foram verificados diff whitespace, conjunto de arquivos Markdown, links relativos, status dos oito ADRs originais, oito linhas da matriz original `PENDING_APPROVAL`, estados válidos do pacote de aprovação, ausência de código executável, ausência de paths protegidos e padrões comuns de credenciais. Não foram executados Docker, MongoDB, testes da aplicação, workflows ou consultas Coolify/GHCR; não houve escrita remota. A homologação e os dados operacionais mencionados são apenas referências das fases anteriores.

## 15. Próxima decisão humana

Recomenda-se iniciar a aprovação por ADR-001 (unidade e coerência de origem), ADR-005 (limite de segurança) e ADR-006 (unidade/head), registrando proprietário e resolução para cada questão aberta. Manter ADR-008 bloqueado, não iniciar implementação e solicitar uma autorização específica para qualquer investigação operacional futura.

**Veredito:** ADRs revisados — decisões preparadas para aprovação humana. Este veredito não libera arquitetura para produção, implementação, migração, cutover ou deploy.
