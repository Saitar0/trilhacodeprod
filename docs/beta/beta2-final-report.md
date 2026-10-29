# Beta 2 — relatório final

## A. Resultado executivo

A base Beta 1 foi aberta em worktree isolada; a fonte de unidade 1.1 foi identificada e copiada sem alterar a origem; contratos legados e tipados foram comparados. O conversor determinístico transformou a unidade e o serviço real de importação persistiu a projeção em MongoDB 7 descartável. Os leitores de serviço reais consultaram a estrutura, e o replay do importador não duplicou registros ou auditoria.

A prova é **parcial**: critérios de conclusão, conexões e respostas privadas de exercícios não têm destino seguro no importador C16; o esquema de bloco de quiz versionado gera warnings no editor genérico; a conversão colapsa segmentação tópica; a rota, publicação, frontend e IAM real não foram exercitados; o importador é multi-fase e não transaciona globalmente. Nenhuma integração é autorizada.

## B. Git e isolamento

- Base exata: `e801cee8f765f87b6e42ccf867a9a70f0325b389`.
- Branch: `codex/beta2-curriculum-import-proof`.
- Worktree: `C:\Users\Joao\.codex\worktrees\trilhacode-beta2-import-proof\trilhacodeprod`.
- A base contém a Beta 1 e é descendente do commit C16 local. `main`, checkout `codex/compose-ci-validation` e `origin/main` em cache são ancestrais; `origin/staging` e `migracao-estrutura` divergem.
- A worktree de migração e o checkout original foram somente leitura e não foram alterados. Sem fetch, merge, cherry-pick, push ou deploy.
- Commit e limpeza final serão registrados após verificações.

## C. Base canônica

Recomenda-se `e801cee` como base técnica limpa de consolidação e decisão, não como versão operacional demonstrada. O responsável ainda deve ratificar a base do produto após refs remotas serem atualizadas por processo autorizado e após revisão do trabalho dirty em outras worktrees. Ver [decisão Git](beta2-canonical-git-decision.md).

## D–E. Trabalho paralelo e fonte curricular

`migracao-estrutura@147dc68` contém a representação segmentada rastreada, além de bundle/contratos/código local não commitados. O bundle dirty validou estruturalmente 10 fases, 572 nós e 3.431 blocos; isso não é release nem conteúdo aprovado. A fonte piloto é uma cópia identificada e hash-verificada da unidade monolítica limpa 1.1, ainda marcada `rascunho`. Ela é `PROPOSED_SOURCE`.

## F–I. Unidade piloto, contratos e conversão

O backend C16 recebe `track/options/nodes/relations`; o contrato tipado local da migração é `trilhacode.intermediate/1.2`/`trilhacode.import_bundle/1.0`, mais rico e sem projeção automática ao importador legado. O conversor mapeia título/objetivos/taxonomias, teoria, resumo, 5 quizzes, 3 exercícios manuais e referências. Campos sem destino foram retirados explicitamente do payload e constam no manifesto. O resultado é determinístico e rastreável, mas perde a segmentação em cinco tópicos e não grava o hash da fonte no banco. Detalhes em [matriz](beta2-import-contract-matrix.md), [conversão](beta2-pilot-unit-conversion.md) e [manifesto](beta2-pilot-unit-manifest.json).

## J–P. Persistência, leitura e segurança editorial

O `run_import` real gravou e repetiu a unidade no banco descartável. `get_track_tree` e `get_node` reais leram o estado staff; leitura estudante foi negada para track privado/draft. Não houve rota, publicação ou frontend. As respostas versionadas foram filtradas por helpers reais em testes offline. A prova não resolve a segurança C16: o importador não tem transação global e escritores diretos podem contornar a autoridade editorial. Não usar esse caminho operacional.

## Q–S. Testes e qualidade

- Conversor: 9 testes aprovados.
- Mongo persistente: 1 teste aprovado.
- Regressões offline selecionadas (import, snapshots, publicação, avaliação, IAM/revisão editorial e gerações): 148 aprovadas e 2 subtests aprovados.
- Ruff e Mypy passaram nos arquivos experimentais após correções de tipagem e imports. A compilação sintática, validação de links/JSON, secret scan, `git diff --check` e auditoria final dos arquivos também passaram. A worktree foi commitada e ficou limpa.
- A coleta padrão tentou importar `backend/tests/conftest.py` e falhou por `httpx` ausente no venv C14. Suítes selecionadas foram executadas sem esse conftest para não usar banco escolhido por fixture antiga.

## T–Y. Gates, limitações e próximo incremento

Gates preservados: G1 `PARTIAL`; G2 `NOT_VERIFIED`; G3 `NOT_VERIFIED`; G4 `PARTIAL`; G5 `NOT_VERIFIED`; G6 `PARTIAL`; G7 `PARTIAL`; G8 `NOT_VERIFIED`; G9 `BLOCKED`; G10 `BLOCKED`. ADR-008 continua bloqueado.

Próximo incremento recomendado: obter aprovação explícita do commit/conteúdo migratório e fechar um contrato de adaptação de fase (tópicos, gabaritos privados, conclusão, relações e placements) com prova de falha/retomada; não integrar até a autoridade editorial conter todos os writers concorrentes.

**Veredito: IMPORTAÇÃO-PILOTO PARCIALMENTE VALIDADA — ADAPTAÇÕES CURRICULARES E TÉCNICAS PENDENTES.**
