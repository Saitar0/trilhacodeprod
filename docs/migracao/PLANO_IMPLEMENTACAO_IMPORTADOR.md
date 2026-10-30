# Plano incremental para o importador da árvore migrada

**Estado:** proposta; nenhuma implementação executada.  
**Base:** `147dc68b81169f66b0ba3802fa2f26e5130923a3`. JSON, banco, modelos, frontend e árvores não foram modificados.

## Princípios

* Manifestos homologados + Markdown alimentam contrato versionado e pacote candidato temporário.
* Tipo desconhecido gera erro, nunca fallback genérico silencioso.
* Ausência de conteúdo não significa exclusão; não apagar nem resetar progresso.
* Escrita futura requer dry-run, ambiente verificado e autorização específica.
* Privacidade deve ser testada na API, renderer e submissão.

## A — Contrato e validadores

**Arquivos futuros:** `backend/import_payload.py`, novos schemas em `backend/schemas/`, testes em `backend/unit_tests/` e documentação.  
**Dependências:** hierarquia, metadados, gabaritos, compartilhamento/progresso e projetos aprovados.  
**Riscos:** aceitar tipo sem renderer ou quebrar payload legado.  
**Testes:** versão, refs/caminhos duplicados/orfãos, ordem, relações, quiz+key, escalas, BSON e regressão legado.  
**Aceite:** versão explícita, erros com caminho, desconhecidos rejeitados, regra para cada categoria migrada.  
**Rollback:** selecionar validador legado; sem escrita no banco.

## B — Conversor Markdown/manifesto

**Arquivos futuros:** ferramenta offline em `docs/migracao/` ou módulo conversor, fixtures e testes.  
**Dependências:** A e manifestos aprovados.  
**Riscos:** bloco perdido, ID instável, metadado omitido, projeto quebrado ou compartilhado duplicado.  
**Testes:** hashes por segmento, determinismo, cobertura de origem, um bloco compartilhado com N colocações e fixtures por tipo/projeto.  
**Aceite:** zero blocos sem destino; mesma entrada gera mesma saída; conflitos/links sem destino reportados.  
**Rollback:** descartar só o diretório temporário.

## C — Simulação e revisão

**Arquivos futuros:** relatório por ação/hash; adaptação de `backend/services/imports.py` se necessária.  
**Dependências:** contrato/conversor aprovados; ambiente de consulta comprovadamente descartável.  
**Riscos:** dry-run atual pode não espelhar toda escrita; DB incorreto.  
**Testes:** zero writes no dry-run; estados novo/inalterado/atualizado/conflito/ausente/tombstone; órfãos/limites.  
**Aceite:** operação e impacto em progresso visíveis por ref; ambiente validado.  
**Rollback:** nenhum; descartar relatório.

## D — Importação experimental isolada (autorização futura)

**Arquivos potenciais:** `backend/services/imports.py`, `backend/indexes.py`, schemas/rotas de quiz e placements, fixtures.  
**Dependências:** autorização própria e Mongo efêmero.  
**Amostra:** unidade simples, quiz+gabarito, prática+solução, compartilhado e projeto com entrega/rubrica.  
**Riscos:** chave revelada, progresso compartilhado sem decisão, duplicação, índice conflitante, escrita parcial/metadado perdido.  
**Testes:** dry-run/import/reimport idempotente/conflito/ausência/rollback estrutural/aluno-staff/renderer/progresso.  
**Aceite:** chave ausente antes da tentativa; refs estáveis; compartilhado único; escalas fiéis; progresso preservado.  
**Rollback:** descartar banco efêmero, sem staging/produção.

## E — Importação completa (autorização separada)

**Arquivos potenciais:** importador, runner versionado, relatório e changelog.  
**Dependências:** piloto aprovado, contrato congelado, pendências resolvidas, snapshot/restore testados e janela autorizada.  
**Riscos:** volume, escrita parcial, colisão, progresso e links sem destino.  
**Testes:** validação integral, dry-run, diff, hashes, lotes e auditoria pós-escrita.  
**Aceite:** 131 unidades cobertas sem perda/duplicação; amostras de todos os tipos renderizam.  
**Rollback:** restaurar estrutura de snapshot verificado; não reverter progresso/submissões automaticamente.

## F — Validação funcional

**Arquivos potenciais:** `frontend/src/components/blocks/BlockRenderer.tsx`, `BlockRendererParts.tsx`, telas/rotas novas e suites backend/frontend/E2E.  
**Dependências:** import autorizado; decisão para revelação, placements/progresso e projetos.  
**Riscos:** ordem/contexto errados, caminho local não virar rota, escala sem efeito funcional.  
**Testes:** E2E aluno/instrutor, teclado, quiz antes/depois, checklist, submissão, rubrica, entrega, relações e reimport.  
**Aceite:** conteúdo fiel, chave protegida, progresso com escopo aprovado, links/catégorias funcionais, sem regressões.  
**Rollback:** reverter código; restaurar estrutura só se necessário e autorizado.

## Arquivos provavelmente envolvidos

Planejamento, não autorização para editar: `backend/import_payload.py`, `backend/services/imports.py`, `backend/routes_import.py`, `backend/schemas/content.py`, `backend/indexes.py`, `backend/integrity.py`, `backend/services/nodes.py`, `backend/services/blocks.py`, `backend/services/relations.py`, `backend/services/progress.py`, `backend/services/submissions.py`, `backend/routes_submissions.py`, `backend/schemas/submissions.py`, `backend/seed.py`, `frontend/src/components/blocks/BlockRenderer.tsx`, `BlockRendererParts.tsx`, `backend/tests/test_import_workflow.py`, `backend/unit_tests/test_import_payload_shape.py`, `backend/tests/test_phase2.py`, `frontend/e2e/admin-import.spec.ts`.

## Riscos comprovados e gates

* Sem schema version, hash de estado semântico ou atomicidade global.
* Metadados de fonte não são copiados automaticamente.
* API de quiz remove campos que o renderer espera.
* Relação atual não posiciona bloco em vários assuntos.
* Snapshot não inclui progresso/submissões/eventos.
* 94 wikilinks dependem de raiz de vault não confirmada; menções 47.2/47.3 sem destino; versões editoriais 37.1/37.2 diferentes.

## Prontidão

**Não pronto para JSON definitivo ou importação.** Aprovar contrato/IDs, segurança de quiz/soluções, placements/progresso, rubricas/projetos, status e referências. Nenhuma etapa A–F foi executada.
