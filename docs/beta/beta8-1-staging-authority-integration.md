# Beta 8.1 — Serviço de staging sob autoridade experimental

## Implementação

`Beta8_1StagingAuthorityBridge` reutiliza `CurriculumStagingService` da Beta 5. O teste prepara e inspeciona o lote pelo serviço real, em banco aleatório separado com o role `beta8_1_preparation`. O adaptador valida estado `PREPARED`, contagem, hash do payload, batch ID e proveniência sintética antes de formar candidato experimental para `Beta8ExperimentalPromoter`.

O bridge só aceita IDs de trilha `beta8-track-synthetic-*`, revisão `synthetic:beta8-1:*`, manifest hash de fixture e registros `synthetic-*`. O SHA-256 completo do staging é vinculado à revisão de origem sintética. Não há destino nas coleções operacionais `tracks`, `track_publications`, `activity_publications`, leitores públicos ou serviço `run_import`.

## Prova persistente

1. O preparador grava pacote Beta 5 em banco temporário `beta5_<run>`, com credencial restrita às quatro coleções de staging e marcador de propriedade.
2. O bridge usa `prepare` e `inspect_batch` reais e rejeita estado/hash divergentes.
3. C12 valida sessão e grant sintéticos; C8/C10 valida revisão/fence do namespace experimental.
4. A transição registra geração e auditoria experimental.
5. A identidade de preparação não consegue gravar o head de promoção.
6. A integração não escreve em coleções operacionais de publicação.

Resultado persistente: `BETA8_1_REAL_STAGING_TO_EXPERIMENTAL_AUTHORITY: PASS` e `BETA8_1_PREPARER_PROMOTION_DENIAL: PASS`.

## Limites

O conteúdo do pacote e o grant são sintéticos. `SYNTHETIC_FIXTURE_APPROVED` é estado de teste, não decisão editorial/pedagógica. O teste exercita uma preparação e uma transição; não cobre toda recuperação de falhas, repetição com payload divergente, promoções simultâneas, fontes reais ou integração da interface do importador. Não demonstra publicação, geração operacional, restore, backup, rollback ou segurança para produção.

Veredito da Entrega C: **STAGING REAL INTEGRADO À AUTORIDADE EXPERIMENTAL — PUBLICAÇÃO NÃO AUTORIZADA**.
