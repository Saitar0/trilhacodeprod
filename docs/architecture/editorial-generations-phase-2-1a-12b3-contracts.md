# Fase 2.1A.12B.3 — contratos internos propostos e mapas de integração

**Status do documento:** proposta para revisão humana.
**Interfaces abaixo:** conceituais, não implementadas e não são endpoints HTTP.
**Baseline dos fatos atuais:** e5bf3147a7f9a5ee02e1a011ffcbf1fb7e0cc636.
**Referência da auditoria:** [Fase 2.1A.12B.2 — auditoria](editorial-generations-phase-2-1a-12b2-audit.md). A auditoria contém evidências linha a linha de escritores, leitores e fluxos.

## 1. Convenções e nível de evidência

- **Atual/código:** leitura estática do snapshot e5bf…; não afirma implantação.
- **Atual/teste:** apenas o comportamento coberto por teste no snapshot.
- **PoC homologada:** 15/15 casos de integração, 26/26 unitários e 7/7 guardas no run 40686021030; valida somente o pacote experimental em MongoDB 7.0.45 standalone.
- **Proposto:** contrato deste documento; não aprovado nem implementado.
- **Pendente:** depende de decisão humana, baseline escolhido ou validação real.

Os nomes de tipos, campos e códigos de erro são sugestões. Não devem ser tratados como esquema persistido nem como API existente. Para qualquer conflito, a compatibilidade do contrato HTTP atual precisa ser medida contra o baseline de release aprovado (ADR-008).

## 2. Fronteiras conceituais

| Componente proposto | Responsabilidade | Identidade candidata | Não deve fazer |
|---|---|---|---|
| EditorialRevisionContract | Revisão completa do estado editorial e conflito de comando | writer/service identity + operation_id + expected_revision | Publicar diretamente para aluno |
| EditorialGenerationBuilderContract | Montar, validar e selar geração de uma revisão imutável | builder identity + generation_id + fence | Ler coleções vivas para completar snapshot sem revisão |
| EditorialPublicationContract | Validar e selecionar head por CAS, emitir receipt | selector identity + operation_id + expected_head | Reescrever geração selada ou aplicar restore in-place |
| PublicGenerationReaderContract | Fixar geração e projetar conteúdo learner-safe | public-reader identity | Ler definição privada/gabarito ou fallback para live |
| EditorialRestoreContract | Construir nova revisão/geração a partir de fonte histórica | restore operation + expected revision/head | Apagar conteúdo ativo antes da seleção |
| LearningSessionContract | Vincular navegação do aluno à geração autorizada | student + server-issued session reference | Confiar em generation_id arbitrário do cliente |
| ActivityEvaluationContract | Avaliar contra definição privada fixada na tentativa | evaluator identity + attempt/version | Consultar head atual para escolher o gabarito |

## 3. Contratos internos propostos

### C-01 — Consultar revisão corrente

| Campo | Contrato proposto |
|---|---|
| Nome/responsabilidade | EditorialRevisionContract.current(track_id); retorna o controle atual sem conteúdo editorial bruto |
| Ator/acesso | Serviços editoriais; identidade de leitura do controle, sem acesso a respostas privadas |
| Entrada/restrições | track_id canônico; opcionalmente incluir active_generation_id e fence atual |
| Saída | revision_id monotônica, estado, active_generation_id, versão do schema; nenhum payload de bloco |
| Pré/pós-condições | Trilha existente; leitura consistente de um documento de controle; sem mutação |
| Invariantes | Revisão só avança por transição condicional; revisão ausente não é inferida de contagens |
| Erros/HTTP | Track inexistente: compatível com 404 legado; controle ausente/corrupto: erro interno fail-closed, sem inventar revision zero |
| Idempotência/concorrência | Leitura idempotente; operação linearizável no documento de controle conforme semântica MongoDB aprovada |
| Deadline/retry | Deadline curto por consulta; retry limitado para falha transitória, sem repetir efeitos |
| Falha parcial/projeção | Sem escrita; não retornar head parcial; campos administrativos não saem do domínio interno |
| Compatibilidade/testes | Adapter interno pode manter retorno de serviço atual; testar revisão monotônica e ausência de inferência de estado |

### C-02 — Validar revisão-base e aplicar comando editorial coerente

| Campo | Contrato proposto |
|---|---|
| Nome/responsabilidade | EditorialRevisionContract.apply(command, expected_revision, operation_id, fingerprint); cria uma revisão completa |
| Ator/acesso | Comando autenticado e autorizado por content.write/manage; service writer limitado às coleções de revisão |
| Entrada/restrições | track_id; expected_revision opaca/monotônica; operation_id estável; fingerprint canônico; comando validado; limite de tamanho/entidades |
| Saída | revision_id nova, operation receipt, resultado e IDs estáveis afetados; sem head público automático |
| Pré/pós-condições | Expected revision igual à corrente; comando válido. Pós: novo estado editorial completo e revisão anterior preservada |
| Invariantes | Toda alteração editorial relevante incrementa revisão exatamente uma vez; todos os writers passam pelo mesmo fence; comandos conflitantes não são reaplicados silenciosamente |
| Erros/HTTP | Conflito candidato 409; idempotency key reutilizada com fingerprint diferente 409; autorização 403; validação 422; mapeamento final depende do contrato HTTP existente |
| Idempotência/concorrência | Retry com mesma operation_id/fingerprint retorna mesmo receipt; CAS em controle por trilha define vencedor; sem rebase automático |
| Deadline/retry | Deadline por comando; retry apenas de erro transitório e pela mesma operation_id; conflito exige nova intenção explícita do editor |
| Falha parcial/projeção | Falha antes do CAS deixa candidato privado retomável/abandonável; nunca expõe estado incompleto. Retorno de API segue DTO atual |
| Compatibilidade/testes | Migrar CRUD e writers indiretos; testes de mesmo revision em entidades diferentes, lost response e writer obsoleto |

### C-03 — Preparar candidato de geração

| Campo | Contrato proposto |
|---|---|
| Nome/responsabilidade | EditorialGenerationBuilderContract.prepare(revision_id, operation_id, expected_head, fence) |
| Ator/acesso | Builder com insert/read restrito em armazenamento privado; não pode selecionar head |
| Entrada/restrições | Revisão committed imutável; schema_version suportado; conteúdo canônico; limites de chunk/BSON aprovados |
| Saída | generation_id determinística ou estável, estado building, manifesto preliminar e contagem de chunks |
| Pré/pós-condições | Revisão completa e autorizada. Pós: somente chunks de candidato privado; geração ainda não publicável |
| Invariantes | Fonte é uma revision_id exata; chunks não podem incorporar leitura viva de entidades mutáveis; IDs e ordem determinísticos |
| Erros/HTTP | Erros internos de validação/storage; endpoint público não é criado por este contrato |
| Idempotência/concorrência | Mesma operation_id + fingerprint retoma; mesmo ID com conteúdo diferente conflita; fence antigo rejeitado |
| Deadline/retry | Deadline global por build e limites por I/O; retry limitado, retomável pelo checkpoint verificado |
| Falha parcial/projeção | Chunks incompletos são privados e não selecionáveis; sem DTO público |
| Compatibilidade/testes | Não altera payload legado; testes de determinismo, duplicação, falha em cada chunk e retomada |

### C-04 — Validar e selar geração

| Campo | Contrato proposto |
|---|---|
| Nome/responsabilidade | EditorialGenerationBuilderContract.validate_and_seal(generation_id, expected_fence) |
| Ator/acesso | Builder; apenas transição de candidato próprio para sealed imutável |
| Entrada/restrições | generation_id, manifesto completo, hash, refs, schema e projeções privadas/públicas |
| Saída | Receipt de selo com hash, counts, schema_version, source_revision_id e estado sealed |
| Pré/pós-condições | Todos os chunks presentes e íntegros; refs resolvidas. Pós: bytes/manifest não podem ser alterados |
| Invariantes | Falha fechada diante de missing/extra/duplicate chunk, hash divergente, ref dangling ou tipo sem schema aprovado |
| Erros/HTTP | Integridade inválida é erro operacional, não 404 como se conteúdo inexistisse; sem expor detalhe sensível |
| Idempotência/concorrência | Repetir o mesmo seal retorna receipt; seal concorrente tem um único estado final; fence obrigatório |
| Deadline/retry | Deadline proporcional ao tamanho fixado; retry só para leitura/hash idempotente; não reescrever selo |
| Falha parcial/projeção | Estado permanece building/failed; não aparece a leitores; manter evidência opaca |
| Compatibilidade/testes | Testes com corrupção e limites reais em MongoDB 7 descartável; contrato atual inalterado |

### C-05 — Selecionar geração e recuperar resposta perdida

| Campo | Contrato proposto |
|---|---|
| Nome/responsabilidade | EditorialPublicationContract.select(generation_id, expected_revision, expected_head, operation_id, fence) |
| Ator/acesso | Selector/service de publicação, permissão content.publish; credencial mínima no controle do head |
| Entrada/restrições | Geração sealed, receipt válido, source_revision atual, expected active generation e operação autorizada |
| Saída | PublicationReceipt imutável com geração selecionada, revisão, operation_id e timestamp de controle |
| Pré/pós-condições | Valida selo, revisão, head e fence; pós CAS de um documento muda o head uma vez |
| Invariantes | Candidato obsoleto não vence; no retry a mesma operation_id retorna receipt original; não duplicar efeitos |
| Erros/HTTP | Conflito 409; candidato inválido 422/erro interno conforme contrato aprovado; sem indicar segredo/estado privado |
| Idempotência/concorrência | operation_id unique + fingerprint; CAS de expected head/revision; resultado de perda de resposta recuperado via receipt |
| Deadline/retry | Deadline curto; retry pela mesma operação após resultado ambíguo; nunca emitir novo operation_id automaticamente |
| Falha parcial/projeção | Antes do CAS, head antigo; depois, nova geração completa; não há etapa intermediária pública |
| Compatibilidade/testes | Mapear ao endpoint publish atual mantendo forma de resposta inicialmente; concorrência e retry em MongoDB real standalone |

### C-06 — Resolver e ler geração pública fixada

| Campo | Contrato proposto |
|---|---|
| Nome/responsabilidade | PublicGenerationReaderContract.resolve(track_id) e read(track_id, generation_id, resource_ids) |
| Ator/acesso | Identidade MongoDB de leitura pública; sem find em definições privadas, drafts ou gabaritos |
| Entrada/restrições | track_id autorizado; generation_id só aceito se veio de sessão/token validado pelo servidor ou head resolvido nessa operação |
| Saída | Head receipt e DTO público allowlist, com generation token opaco/aditivo para cache/sessão |
| Pré/pós-condições | Geração ativa selada; consulta de head feita uma vez por operação. Pós, toda leitura usa o mesmo generation_id |
| Invariantes | Não mistura chunks/gerações; hash/ref validados; tipo desconhecido e corrupção falham fechados; sem fallback live |
| Erros/HTTP | Ausência pode ser 404; corrupção/indisponibilidade retorna erro explícito não-cacheável; código exato requer API review |
| Idempotência/concorrência | Leitura idempotente; trocar head entre resolve e leitura não muda generation_id selecionado |
| Deadline/retry | Deadline por leitura; retry apenas na mesma generation_id; nunca re-resolver head dentro de retry de chunks |
| Falha parcial/projeção | Nenhuma resposta parcial; DTO por allowlist; sem campos privados, extras desconhecidos ou gabaritos |
| Compatibilidade/testes | Manter endpoints e IDs; comparar payload legacy por contract tests; testar publicação entre tree/node/quiz e cache |

### C-07 — Projetar DTO público

| Campo | Contrato proposto |
|---|---|
| Nome/responsabilidade | PublicGenerationReaderContract.project(generation_schema, block_type, stored_public_record) |
| Ator/acesso | Boundary de resposta pública, sem acesso ao documento privado de avaliação |
| Entrada/restrições | Schema/type allowlisted; dados learner-safe; limites de campo e tamanho |
| Saída | DTO estrito, versão compatível; nenhum campo desconhecido copiado automaticamente |
| Pré/pós-condições | A geração foi validada e está fixada. Pós, serialização contém somente campos publicados aprovados |
| Invariantes | Gabaritos, respostas, rubric, feedback interno, writer ID e hashes de controle nunca são públicos |
| Erros/HTTP | Schema desconhecido falha fechado e gera métrica sem payload |
| Idempotência/concorrência | Função determinística e sem I/O; sem race |
| Deadline/retry | Limite de CPU/tamanho de DTO; não aplicável retry de rede |
| Falha parcial/projeção | Falha no bloco rejeita resposta completa; sem “best effort” que omita silenciosamente campos semânticos |
| Compatibilidade/testes | Comparar campo a campo com DTO atual; teste de canário secreto em todas as rotas e cache |

### C-08 — Restaurar versão como nova candidata

| Campo | Contrato proposto |
|---|---|
| Nome/responsabilidade | EditorialRestoreContract.prepare_restore(track_id, source_version_id, expected_revision, operation_id) |
| Ator/acesso | Editor com content.publish/restore aprovado; serviço de restore limitado a ler histórico e criar nova revisão |
| Entrada/restrições | Versão histórica íntegra, source revision explícita, expected revision/head e motivo auditável |
| Saída | Nova revision_id e generation candidate; nunca reescreve versão antiga |
| Pré/pós-condições | Fonte existe, hash/refs válidos, política de progresso/atividade compatível. Pós candidata segue builder/seal/select |
| Invariantes | Restauração conserva IDs/refs conforme política; não apaga coleção ativa; CAS e fence comuns a CRUD/publicação |
| Erros/HTTP | Fonte ausente 404; conflito 409; fonte inválida erro fechado; mapeamento compatível pendente |
| Idempotência/concorrência | operation_id/fingerprint; retry da mesma restauração devolve o mesmo candidate/receipt; conflito com edição exige nova intenção |
| Deadline/retry | Deadline por restore; checkpoint apenas para mesma fonte/fingerprint |
| Falha parcial/projeção | Head anterior permanece; candidato parcial privado; após seleção, restore é nova generation |
| Compatibilidade/testes | Manter endpoint de restore e resposta inicial; testar failpoint, conflito, progresso e tentativa antiga |

### C-09 — Abrir, ler, retomar e encerrar sessão de estudo

| Campo | Contrato proposto |
|---|---|
| Nome/responsabilidade | LearningSessionContract.open(track_id), authorize/read(session_ref), resume(session_ref), close(session_ref) |
| Ator/acesso | Aluno autenticado; sessão vinculada a subject, track, generation, validade e revocation state no servidor |
| Entrada/restrições | track_id autorizado; referência opaca/assinada; nunca aceitar generation_id como autoridade isolada |
| Saída | session_ref, generation_id resolvida e estado/expiração não sensível; leitura retorna conteúdo da geração fixada |
| Pré/pós-condições | Head ativo resolvido no open; identidade de aluno e acesso verificados. Pós, requests da sessão permanecem no mesmo generation_id ou explicitam revogação |
| Invariantes | Não mudar pin silenciosamente; sessão revogada não lê; geração referenciada impede GC conforme ADR-004 |
| Erros/HTTP | Sessão inválida/expirada 401/404 conforme padrão de segurança aprovado; generation retirada retorna estado explícito |
| Idempotência/concorrência | Open pode aceitar idempotency key para evitar sessões duplicadas; close é repetível; resume valida owner |
| Deadline/retry | Sessão tem TTL a aprovar; retry de open usa mesma key; read fixa geração |
| Falha parcial/projeção | Se head corrupto, não criar sessão; não fallback live; resposta pública allowlist |
| Compatibilidade/testes | Adicionar campo/session token sem quebrar chamadas atuais; browser tests com cache em geração A/B |

### C-10 — Iniciar, submeter e avaliar atividade

| Campo | Contrato proposto |
|---|---|
| Nome/responsabilidade | ActivityEvaluationContract.start_attempt(session_ref, activity_id), submit(attempt_id, revision, answer), evaluate(attempt_id) |
| Ator/acesso | Aluno para start/submit; evaluator service identity para gabarito privado; staff somente conforme autorização atual |
| Entrada/restrições | Sessão válida, atividade existente nessa geração, attempt_id/idempotency key, expected attempt revision, payload validado |
| Saída | Attempt receipt, estado e resultado permitido; não retornar definição privada ou answer key |
| Pré/pós-condições | Tentativa registra generation_id, activity_definition_id/version e schema. Avaliação lê exatamente definição privada imutável dessa identidade |
| Invariantes | Head atual não altera avaliação em aberto; retry não duplica nota/progresso; uma resposta pertence a uma versão de atividade |
| Erros/HTTP | Tentativa/versão incompatível 409; atividade retirada 410/estado equivalente sujeito a API review; autorização negada 403 |
| Idempotência/concorrência | Chave por tentativa/submit; expected_revision CAS; retry usa mesmo conteúdo e key; resposta diferente na mesma key conflita |
| Deadline/retry | Deadline em armazenamento e avaliação; retry limitado e deduplicado |
| Falha parcial/projeção | Persistência de resultado e progresso precisa ser retomável/consistente; não avaliar contra head novo; retorno é DTO de tentativa |
| Compatibilidade/testes | Preservar published_version_id no período de transição; contract tests do frontend e attempts antigos; política de histórico pendente |

## 4. Inventário de escritores reais e mapeamento futuro

Os itens abaixo foram encontrados no snapshot e5bf… no audit B.2, seção 2; referências específicas são indicadas. Risco e contrato são propostas. O inventário não declara cobertura de scripts externos, infraestrutura ou arquivos não presentes no snapshot.

| Writer atual | Operação/coleções e concorrência atual | Risco / confiança | Contrato futuro e migração | Teste / gate |
|---|---|---|---|---|
| Trilhas CRUD/reorder/delete | backend/routes_content.py:69-95; backend/services/tracks.py:51-115; tracks insert/update, loop reorder, cascade multi-coleção; sem revisão comum | Estado parcial e perda de atualização; alta | C-02; tombstone de exclusão após ADR-004 | reorder/edit/delete concurrent; nenhum bypass; ADR-001 |
| Duplicação de trilha | backend/routes_content.py:94-96; backend/services/tracks.py:118-149; clona sequencialmente | Cópia parcial/órfãos; alta | C-02 em candidato completo, valida IDs/refs | failpoint e órfãos; writer coverage |
| Publicação | backend/routes_content.py:99-102; backend/services/tracks.py:152-227; snapshot/activity, promove children, depois CAS track | P1 confirmado pela ordem; concorrência que perde CAS é cenário | C-03–C-05; ADR-001/006 | failpoints, CAS dispute, reader interleaving |
| Nós CRUD/reorder/delete/duplicate | backend/routes_content.py:122-151; backend/services/nodes.py:61-82,152-232 | árvore/conteúdo/progresso parcial; alta | C-02; excluir estrutura sem apagar progresso até decisão | concorrência edit/reorder/duplicate; references |
| Blocos | backend/routes_content.py:156-175; backend/services/blocks.py:12-52; content_blocks | conteúdo, alternativas ou avaliação pode mudar durante leitura; alta | C-02; classificação ADR-003/005 | alteração same-count e projection canaries |
| Relações/pré-requisitos | backend/routes_content.py:177-190; backend/services/relations.py:12-50; ciclo validado antes de write | Duas inserções podem passar check separadas (inferido) | C-02; validar conjunto inteiro em revisão | disputa de ciclo; propriedade inferida precisa reproduzir |
| Importação | backend/routes_import.py:13-35; backend/services/imports.py:70-177,526-815; upserts e locks/import jobs | Lease não comum a CRUD; staff pode ver `_import_state`; alta | C-02/C-03, revisão isolada e fencing compartilhado | import×CRUD, resume, invisibilidade; zero bypass |
| Restauração | backend/routes_versions.py:17-19; backend/services/versions.py:24-139,245-332; deletes/inserts e lease local | P1 de exposição parcial confirmado pela ordem; alta | C-08 e C-05; restore nova geração | failpoints de cada delete/lote e edição concorrente |
| Taxonomies/tags/block types | backend/routes_taxonomy.py:47-81; backend/services/taxonomy.py:31-91; global mutations, tag `$pull` | interpretação de trilhas muda sem geração; alta para write, semântica por campo pendente | C-02 se semântica; ADR-003; maintenance global gate | mudança metadata e leitura pinada |
| Seeds | backend/seed.py:100-201; escrita de fixtures/demonstração e metadados | Pode contornar writer; alta no repo, uso em produção não identificado | C-02 em ambiente de conteúdo ou bloqueio por ambiente | scanner + role/env guard; sem afirmar production use |
| Migrations/manage/maintenance | backend/manage.py:18-42; backend/migrations/__init__.py:54-99 e migrations 0001/0002 | writes fora do fence; alta como caminho disponível, execução real não conhecida | Operação versionada ou janela/quiescence explícita | migration×writer; aprovação de operação |
| Tentativas de aluno | activities.py; collection activity_attempts; ids/keys/version | Não é writer editorial; exige referência imutável da avaliação | C-10 | retries e tentativa antiga |
| Progresso | backend/services/progress.py:152-379; progress/events/user_track_state | Não deve integrar snapshot editorial; geração ausente | C-09/C-10 após decisão de produto | republish com progresso preservado |
| Submissions | backend/services/submissions.py:20-204; submissão/progresso/eventos sequenciais | Histórico sem version/generation; avaliação pode resolver bloco vivo | C-10; separado do agregado editorial | resposta concorrente, retry, version pin |
| Notes/reviews | backend/learning.py:175-370; notas e revisões privadas | Fora da geração; título pode ser resolvido via node vivo | Leitura de histórico associada a IDs; retenção ADR-004 | delete/tombstone e associação histórica |

Cobertura integral não está declarada: o snapshot foi varrido nos módulos backend e não identificou worker editorial recorrente; ferramentas operacionais fora do repositório, deploy scripts e acessos diretos ao MongoDB ainda precisam de inventário autorizado antes do gate.

## 5. Inventário de leitores e mapeamento futuro

Referências atuais detalhadas no audit B.2, seção 3. Identidades reais indicam dependências observadas no código, não grants verificados no MongoDB implantado.

| Reader atual | Identidade/dados atuais | Risco e adaptação proposta | Compatibilidade/cutover/rollback | Teste |
|---|---|---|---|---|
| Catálogo GET /api/tracks; backend/services/tracks.py:20-48 | usuário autenticado/staff; tracks + counts nodes; sem geração | C-06; resolver geração e paginação no mesmo pin | DTO atual aditivo; rollback para geração segura, sem live fallback | publicação entre list/count; cache |
| Detalhe da trilha GET /api/tracks/{id}; backend/services/tracks.py:76-80 | current_user/can_view_track; raw serialized track | C-06/C-07, allowlist por audiência | Não serializar documento cru; indisponibilidade explícita no cutover | canários de campos privados |
| Árvore GET /tree; backend/services/nodes.py:234-256 | público/staff; track/nodes/relations/count em queries separadas | C-06, uma generation_id | tree DTO preservado; não misturar cache | interleaving tree A/B |
| Nó/blocos GET /nodes/{id}; backend/services/nodes.py:27-149 | staff draft; learner status; strips notes, quiz path explicit, outras types denylist | C-06/C-07; reader restrito e block schema allowlist | Mesmo IDs, projection revisada | extra fields, gabarito, tipo desconhecido |
| Busca GET /api/search; backend/services/search.py:9-47 | visibilidade de usuário; nodes live + tracks separados | C-06 por generation e search index versionado | Result refs incorporam generation | query concorrente com publish |
| Validate/prerequisites; backend/learning.py:116-153, track_locks | staff/aluno; track/nodes/relations/blocks/progress separados | C-06 + progress session context | Não misturar checks de gerações | precondition under publish |
| Atividade pública GET attempts; backend/services/activities.py:44-196 | aluno; activity_publications por published_version_id; public_activity DTO | C-06/C-07 e C-10; quiz atual é pin limitado | Manter version antiga durante transição | role e DTO canário |
| Avaliação de tentativa | backend/services/activities.py:209-451 | attempt guarda published_version_id/revision; evaluator usa definição correspondente | C-10; ligar também generation/session | B publicada após start, avaliação contra A |
| Progresso | backend/services/progress.py:152-379,421+ | aluno; user/node/block; live resolve | C-09, decisão de mapeamento; geração não comprovada | round-trip/session, conteúdo removido |
| Submission | backend/services/submissions.py:20-204 | aluno/staff; join a block/node vivos, sem snapshot/version | C-10; guardar activity/schema/generation | republish e answer submit |
| Notes/reviews | backend/learning.py:175-370 | privado por usuário; resolve títulos atuais | Separar do snapshot; presentation historical refs | authorization e tombstone |
| Versions/preview admin | backend/services/versions.py:142-227; integrity.py:63-122 | content.read; stored chunks/history ou atual; chunks podem ser substituídos para id em integrity.py | Admin reader separado; mesma geração para compare | preview auth, mutation/integrity |
| GET /api/meta | backend/services/taxonomy.py:12-28 | usuário autenticado; taxonomies/block_types/tags globais | C-06/C-07 para parte semântica; ADR-003 | alteração global após A |
| Frontend tree/node/progress | frontend/src/hooks/useData.ts:19-40; frontend/src/index.tsx:41; TrackViewer/NodeReader | Cache por track/node, staleTime 30s; sem generation key | Token de sessão/geração incluído em query key; clear no close/revoke; sem client authority | browser cross-generation e invalidation |

Não foi identificado endpoint explícito de exportação ou cache HTTP/CDN no snapshot auditado (audit B.2:73). Isso não prova ausência fora do snapshot. Leitores públicos, de staff e evaluator devem ser revisitados sobre o baseline escolhido.

## 6. Propagação de geração no frontend

Proposta: abrir sessão no servidor e receber session_ref vinculada ao usuário e trilha; requests posteriores enviam essa referência autenticada, não um generation_id livre. Servidor resolve e verifica geração a cada endpoint. A resposta inclui token/identidade de versão para query key/cache, sem tornar o token uma credencial de acesso autônoma. Cache keys de árvore, nó, progresso e atividade incluem session scope/generation; fechar/revogar sessão invalida dados em memória. Link direto sem sessão cria/resolução de sessão sob regra aprovada. A API atual não oferece essa semântica completa segundo audit B.2; mudança futura precisa manter ou versionar payloads.

## 7. Correspondência com a PoC homologada

Implementação experimental consultada: backend/services/editorial_generations_poc.py no commit de pacote 8a087fd5baa9e2eaa98bc1d2ed52b4a60f8c7036. Os nomes abaixo são funções reais da PoC, não contratos da aplicação.

| PoC real | Evidência no arquivo | Relação com contrato proposto | Limite da evidência |
|---|---|---|---|
| EditorialGenerationsPoC e namespace próprio | __init__:262-267; index_specs:270-288 | Inspira builder/selector/read store separado | Usa poc_editorial_*; não cria integração com coleções reais |
| GenerationHandle e begin | dataclass:58-66; begin:308-387 | operation_id, fingerprint, writer_id, fence, base generation/pointer revision | Recebe snapshot do chamador; não prova que snapshot veio de revisão editorial coerente |
| Append chunks e prepare/seal | _append_chunk:409-435; prepare:437-545; _complete_sealing:547-598 | Canonicalização, chunk refs, hash, seal intent e manifest imutável | Validação estrutural é a regra da PoC; precisa de schemas reais por tipo e papéis de produção |
| Verificação do manifesto | _load_verified:609-652 | Recalcula hash, sequência, chunk bytes, canonical form e activity refs; corrupção falha | É validação do schema experimental; não cobre todas rotas ou schemas reais |
| Select active e receipt | select_active:654-716 | CAS pelo base_generation_id/base_pointer_revision, recebe selection receipt/replay | Não condiciona editorial_revision do legado, pois não há protocolo comum de writers integrado |
| Reader pinado | read_active_public:718-732 | Lê head uma vez; usa manifest/generation fixos; fallback live proibido | Uma chamada da PoC; não propaga pin entre rotas/sessões do frontend |
| Projeção pública | _private_key:734-749; project_public_snapshot:752-809; select_fields:792-802 | Inspira filtragem pública | Keyword filter da PoC não substitui allowlist e separação de credenciais para schema real |
| Errors/failpoints | GenerationConflict/Invalid/NotFound:41-54; failpoint:251-257 | Conflitos, corrupção e pontos de falha testáveis | Não define HTTP status nem erros públicos da aplicação |

Relato experimental do run 40686021030 confirma 15/15 testes integrados, 26/26 unitários e 7/7 guardas no MongoDB 7.0.45 standalone. Isso confirma o harness/PoC naquele ambiente; não comprova roles de produção, coerência de source snapshot, interfaces HTTP ou cobertura total de writers.

## 8. Fontes e grau de confiança

| Evidência | Fonte | Grau |
|---|---|---|
| CRUD/publicação/restore e import | e5bf…; services/tracks.py:51-227; backend/services/nodes.py:61-232; backend/services/blocks.py:12-52; backend/services/relations.py:12-50; backend/services/imports.py:70-815; backend/services/versions.py:24-332 | Alto para snapshot |
| Readers e projeções | e5bf…; audit B.2:56-73; backend/services/nodes.py:27-149,234-256; backend/services/activity_publications.py:155-169 | Alto para código; grants Mongo desconhecidas |
| Índices/configuração | e5bf…; backend/indexes.py:7-91; backend/database.py:1-8 | Alto para declarações; criação no ambiente não comprovada |
| Attempts e progresso | e5bf…; backend/services/activities.py:130-190; backend/services/progress.py:152-379 | Alto para os caminhos citados |
| Protocolo | PoC commit 8a087fd5…; run 40686021030 | Confirmado somente no harness experimental reportado |

## 9. Escopo não comprovado

Não foram encontrados no snapshot workers recorrentes editoriais ou endpoint explícito de exportação; infraestrutura e scripts externos não auditados. Os títulos e nomes acima descrevem funções/rotas encontradas; contratos C-01–C-10 permanecem propostas. Nenhuma mudança em código, schema, API, frontend ou dados decorre deste documento.
