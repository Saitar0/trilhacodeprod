# Trilha Code — Beta 5: relatório final

## A. Resultado executivo

A Beta 5 implementou e exercitou, somente em ambiente isolado, uma proteção fail-closed para testes persistentes, contratos curriculares tipados com separação campo a campo entre aluno/instrutor/sistema, e staging curricular recuperável desacoplado do runtime. A conversão Beta 4 foi reutilizada para as dez unidades e os 11 materiais do projeto 3.5. A prova MongoDB 7 demonstrou retomada depois de falha sintética, repetição sem duplicação e concorrência local com dois clientes independentes.

O resultado não permite servir conteúdo aos alunos, publicar, promover nem integrar writers. A fonte continua `rascunho`; visibilidade de projeto, ACL operacional, política de conclusão, grants reais e contenção de writers permanecem pendentes.

**Veredito:** FUNDAÇÃO CURRICULAR SEGURA VALIDADA EM AMBIENTE ISOLADO — PROMOÇÃO E INTEGRAÇÃO NÃO AUTORIZADAS.

## B. Git e isolamento

* Base: `3e7c1a8778597cf30e7d4d2e7a13b3f29fb72beb`, contendo os entregáveis Beta 4.
* Branch: `codex/beta5-safe-curriculum-foundation`.
* Worktree: `C:\Users\Joao\.codex\worktrees\trilhacode-beta5-safe-foundation\trilhacodeprod`.
* Worktree criada com `git worktree add --no-checkout`, sparse-checkout configurado antes da materialização. Foram materializados `backend`, `docs/beta`, `docs/architecture`, `ops/g2` e `.github/workflows` para as regressões estáticas. `docs/courses/trilhacode/` e `docs/migracao/` não foram materializados nem alterados nessa worktree.
* Fonte de migração lida em modo somente leitura na worktree `fase1-migracao`, HEAD `147dc68b81169f66b0ba3802fa2f26e5130923a3`; as 221 referências de artefatos conferem com o manifesto Beta 4 e `Conteudos_migrado/Fase_1` não aparece como modificado. A worktree de migração já contém alterações locais e arquivos não rastreados em materiais adjacentes (incluindo o bundle e `docs/migracao/`); nenhum foi copiado, alterado ou consolidado pela Beta 5.
* O checkout original protegido já apresentava alterações locais e arquivos não rastreados quando inspecionado; permaneceu fora do escopo de escrita e não foi limpo nem teve arquivos incluídos nos commits Beta 5.
* Commits locais e estado final estão registrados ao final desta execução; sem push, PR, merge ou deploy.

## C. Ocorrência Beta 4

O fixture antigo podia selecionar `localhost:27017`; identidade e limpeza daquela instância não foram comprovadas. Não houve investigação nem limpeza retroativa. Na Beta 5, a coleta persistente sem opt-in foi bloqueada antes da importação dos módulos de aplicação, e nenhum acesso a essa porta foi feito.

## D–E. Política e provas fail-closed

`backend/test_support/beta5_mongo_target.py` valida URI, UUID, banco, credenciais, container/rede com IDs completos, labels de propriedade, image tag, volume temporário, binding loopback, topologia, MongoDB 7, WiredTiger e marcador do banco. Sem a validação Docker anterior à conexão, a fábrica de cliente não é chamada. A identidade do banco é verificada antes de importar a aplicação, migrar, semear ou gravar. `MONGO_URL_TEST` não é fallback.

O ambiente descartável foi criado pelo harness, com MongoDB `mongo:7.0.43`, credenciais aleatórias, banco por execução, bridge dedicada, porta efêmera apenas em 127.0.0.1 e tmpfs, sem volumes. O harness revalidou o marcador e labels antes de remover seu próprio contêiner e rede.

Provas offline incluem URI ausente, vazia ou malformada; localhost/27017; URI com parâmetro extra; banco e credenciais sem vínculo à execução; labels/IDs divergentes; segredo divergente; binding público; volume persistente; rede com contêiner adicional; marcador ausente/divergente; e opt-in ausente. `pytest tests --collect-only -q` sem opt-in terminou com erro esperado de política, antes da importação dos testes persistentes.

Limite: Docker Desktop rejeitou porta publicada em uma bridge `--internal`; a bridge Beta 5 é dedicada e não compartilhada, mas saída de rede do contêiner não foi desabilitada nem provada. A URI e a porta publicada, porém, ficaram limitadas ao loopback e foram confrontadas com o inspect. Não se afirma isolamento de rede absoluto.

## F–K. Índices e contratos pedagógicos

A expectativa histórica de 38 foi substituída por verificações semânticas dos dois índices de `track_publications` acrescentados no commit `2574bf1b98482b58746c5e7a42b4df0fe07bec93`. A definição operacional `backend/indexes.py` não foi modificada. A análise detalhada está em [beta5-index-regression-analysis.md](beta5-index-regression-analysis.md).

Os contratos tipados separam `STUDENT_PUBLIC`, `INSTRUCTOR_RESTRICTED` e `SYSTEM_INTERNAL`, validam chaves permitidas e não emitem respostas privadas em projeções públicas. O acesso a projeção restrita requer evidência sintética vinculada à trilha e à operação; isso não é IAM/ACL operacional. Critérios preservam texto sem limiar automático. Relações externas não viram pré-requisitos forçados; referências preservam descrição e proveniência. Ver [conteúdo protegido](beta5-protected-content-contract.md), [conclusão](beta5-completion-criteria-contract.md) e [relações/referências](beta5-curricular-relations-and-references.md).

O projeto 3.5 tem 11 materiais: brief, quatro marcos, uma rubrica e cinco checklists. O contrato contém projeto, etapas e artefatos. Todo conteúdo do projeto continua interno ou restrito; nenhum artefato compõe projeção de aluno enquanto a visibilidade estiver pendente. Nenhum material privado foi colocado no manifesto. Ver [beta5-project-3-5-contract.md](beta5-project-3-5-contract.md).

## L–O. Staging, identidade e recuperação

`CurriculumStagingService` não importa a aplicação e escreve somente em quatro coleções `_beta5_staging_*`. Valida o pacote em memória e confere banco/ownership antes de criar índices ou gravar. O pacote usa SHA-256 canônico completo, `batch_id` derivado do conteúdo, IDs estáveis, hashes individuais, checkpoints e eventos únicos. Não há rota/leitor, coleção editorial de destino, estado publicado ou promoção.

No MongoDB descartável, uma falha sintética depois do primeiro documento e antes do checkpoint deixou um registro parcial e o lote `RECOVERABLE`. A repetição completou registros/checkpoints e chegou a `PREPARED`; outra repetição não aumentou documentos nem eventos. Uma identidade persistida adulterada resultou em `StagingIdentityConflict` antes de novas gravações. Duas chamadas concorrentes de serviços com clientes AsyncMongoClient independentes prepararam outra identidade de pacote sem registros, checkpoints ou evento `prepared` duplicados.

Isso demonstra recuperação por etapas no cenário exercitado, não atomicidade global. Não foram simulados crash de processo, perda de rede, failover, writers em hosts distintos ou leitor HTTP. Os detalhes estão em [beta5-staging-design.md](beta5-staging-design.md) e [beta5-staging-recovery-evidence.md](beta5-staging-recovery-evidence.md).

## P–Q. Segurança editorial e promoção

O serviço não altera IAM, grants, revisões, fences, auditoria editorial, snapshots, gerações, conteúdo publicado, progresso ou tentativas. A C16 segue aplicável: credenciais com escrita direta podem contornar protocolo cooperativo. A promoção precisa aguardar autoridade C8–C16, grants e revogação ordenada, versionamento de política, writers concorrentes contidos, auditoria, CAS/fencing, idempotência, ACL/retention e testes integrados. Nenhum caminho Beta 5 permite publicar. Ver [dependências de promoção](beta5-editorial-promotion-dependencies.md).

## R–U. Persistência, testes e regressões

Ambiente Python exclusivo: Python 3.11.9 em `C:\Users\Joao\.codex\tmp\trilhacode-beta5-venv`; dependências vieram dos requirements oficiais do backend. `httpx==0.28.1` estava declarado em `requirements-dev.txt` e foi instalado no venv, sem editar dependências operacionais ou Python global.

| Verificação | Resultado |
|---|---:|
| Suíte offline `backend/unit_tests` com raiz da worktree migrada | 318 passed, 36 skipped, 26 subtestes |
| Testes Beta 5 focados, incluindo inventário e contratos de fonte real | 41 passed na execução final do gate offline |
| Prova persistente staging MongoDB 7 | 1 passed |
| Testes históricos de índice no banco descartável | 2 passed |
| Coleta de `backend/tests` sem opt-in | bloqueada como esperado, 0 testes coletados |
| Ruff nos novos módulos/testes | passed |
| Ruff nos arquivos de fixture/teste alterados | passed |
| MyPy direcionado | passed com `--disable-error-code=import-untyped` para o YAML do conversor Beta 4 existente |
| Compilação sintática | passed |

Os 36 skips da suíte offline são os testes condicionados a Bash/jq/flock POSIX no Windows. Nenhuma suíte completa de API ou E2E foi executada. Uma primeira invocação da suíte offline apontou para o subdiretório curricular em vez da raiz da worktree e terminou com 311 passed, 36 skipped, 1 failed e 6 erros de coleta; o gate do harness bloqueou a etapa persistente. Corrigida a raiz para a worktree de migração, a suíte completa terminou com 318 passed, 36 skipped e 26 subtestes. A suíte histórica de snapshot não foi executada nesta fase porque exigiria outro alvo persistente; os testes pertinentes já executados na Beta 4 permanecem evidência histórica, não execução Beta 5.

## V–X. Qualidade, segurança, gates e limpeza

Nenhuma rota, IAM operacional, writer ativo, schema ou configuração foi alterada; o único código em `backend/tests/` alterado foi o fixture de testes autorizado e a asserção histórica de índice autorizada. Não houve acesso a dados reais, staging/produção, Coolify, GHCR ou credenciais operacionais. Manifestos e inventário não contêm gabaritos, corpos restritos ou segredos.

Gates preservados: G1 PARTIAL; G2 NOT_VERIFIED; G3 NOT_VERIFIED; G4 PARTIAL; G5 NOT_VERIFIED; G6 PARTIAL; G7 PARTIAL; G8 NOT_VERIFIED; G9 BLOCKED; G10 BLOCKED. ADR-008 permanece BLOCKED.

O harness removeu somente os recursos MongoDB com ownership Beta 5 verificado. Nenhuma instância ou banco preexistente foi tocado. A worktree foi limpa após commits locais.

## Y–AC. Arquivos, limitações e próximo incremento

O manifesto agregado por unidade está em [beta5-first-phase-manifest.json](beta5-first-phase-manifest.json). A lista completa de entregáveis está na seção Z abaixo. Limitações centrais: sem ACL real para instrutores, sem destino operacional para rubricas/critério/artefatos de projeto, sem aprovação de visibilidade, sem integração da autoridade editorial e sem interface do aluno. Conversão/ staging não equivalem à beta utilizável.

Próximo incremento recomendado: especificar e implementar, sob autorização própria, um adaptador de leitura/avaliação com ACL real para quiz e submissões manuais, mantendo publicação bloqueada até o cutover de todos os writers concorrentes e a aprovação da promoção editorial. Antes, o responsável do produto deve decidir visibilidade dos 11 materiais do projeto 3.5 e os critérios de conclusão; o IAM deve aprovar a autoridade/grants e a política de retenção.

## Z. Arquivos

Novos módulos e testes:

* `backend/curriculum_contract/beta_completion_criteria.py`
* `backend/curriculum_contract/beta_curricular_metadata.py`
* `backend/curriculum_contract/beta_project_contract.py`
* `backend/curriculum_contract/beta_protected_content.py`
* `backend/curriculum_contract/beta_staging_contract.py`
* `backend/services/beta_curriculum_staging.py`
* `backend/test_support/beta5_mongo_target.py`
* `backend/test_support/beta5_mongodb_harness.py`
* `backend/integration_tests/beta_staging_harness.py`
* `backend/integration_tests/test_beta_staging_recovery.py`
* `backend/unit_tests/test_beta_project_contract.py`
* `backend/unit_tests/test_beta_protected_content.py`
* `backend/unit_tests/test_beta_staging_contract.py`
* `backend/unit_tests/test_beta_test_database_policy.py`

Arquivos de teste ajustados dentro da autorização:

* `backend/tests/conftest.py`
* `backend/tests/test_integrity_concurrency.py`

Documentação e inventários:

* `docs/beta/beta5-completion-criteria-contract.md`
* `docs/beta/beta5-curricular-relations-and-references.md`
* `docs/beta/beta5-editorial-promotion-dependencies.md`
* `docs/beta/beta5-final-report.md`
* `docs/beta/beta5-first-phase-manifest.json`
* `docs/beta/beta5-index-regression-analysis.md`
* `docs/beta/beta5-project-3-5-artifacts.json`
* `docs/beta/beta5-project-3-5-contract.md`
* `docs/beta/beta5-protected-content-contract.md`
* `docs/beta/beta5-staging-design.md`
* `docs/beta/beta5-staging-recovery-evidence.md`
* `docs/beta/beta5-test-isolation-policy.md`