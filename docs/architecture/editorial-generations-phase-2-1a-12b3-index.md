# Fase 2.1A.12B.3 — índice de ADRs e contratos propostos

**Estado:** documentação proposta para aprovação humana; não autoriza implementação.
**Baseline auditado:** e5bf3147a7f9a5ee02e1a011ffcbf1fb7e0cc636.
**Auditoria anterior:** [Fase 2.1A.12B.2](editorial-generations-phase-2-1a-12b2-audit.md).
**PoC experimental:** commit 8a087fd5baa9e2eaa98bc1d2ed52b4a60f8c7036; run 40686021030.

## Documentos desta fase

| Documento | Conteúdo |
|---|---|
| [ADR-001 — revisão editorial](adr-editorial-generations/ADR-001-editorial-revisions.md) | Revisão monotônica, writers, conflitos, máquina de estados e fencing |
| [ADR-002 — sessão e geração](adr-editorial-generations/ADR-002-learning-session-generation.md) | Pin do aluno, tentativas, progresso, revogação e cenários pedagógicos |
| [ADR-003 — taxonomias](adr-editorial-generations/ADR-003-versioned-taxonomies.md) | Classificação campo/coleção e semântica versionada |
| [ADR-004 — retenção](adr-editorial-generations/ADR-004-retention-and-deletion.md) | Referências, exclusão e GC sem prazo presumido |
| [ADR-005 — público/privado](adr-editorial-generations/ADR-005-public-private-data-separation.md) | Roles, armazenamento privado e projeções allowlist |
| [ADR-006 — publicação atômica](adr-editorial-generations/ADR-006-atomic-publication.md) | Candidate, selo, CAS, leitor pinado e restore |
| [ADR-007 — migração gradual](adr-editorial-generations/ADR-007-gradual-migration.md) | Coexistência, flags separadas, ordem e rollback |
| [ADR-008 — baseline](adr-editorial-generations/ADR-008-baseline-compatibility.md) | Divergência de refs e gate bloqueante para implementar |
| [Contratos e matrizes](editorial-generations-phase-2-1a-12b3-contracts.md) | Contratos conceituais, PoC versus aplicação, writers, readers e frontend |
| [Invariantes](editorial-generations-phase-2-1a-12b3-invariants.md) | Catálogo testável vinculado a ADR, teste e gate |
| [Decisões pendentes](editorial-generations-phase-2-1a-12b3-decisions.md) | Ordem e perguntas de aprovação humana; status PENDING_APPROVAL |
| [Roadmap](editorial-generations-phase-2-1a-12b3-roadmap.md) | Fases futuras, dependências, testes, riscos, reversão e autorização |

## Leitura recomendada

1. Aprovar ou bloquear o baseline proposto em ADR-008.
2. Decidir ADR-001 antes de interpretar o CAS do head como garantia de origem coerente.
3. Revisar ADR-005 e ADR-003 antes de definir o formato da geração pública.
4. Aprovar semântica de sessão/progresso e retenção (ADR-002/004) antes de backfill.
5. Revisar ADR-006 e ADR-007 para definir cutover e comportamento seguro de rollback.

## Limites do material

Todos os oito ADRs têm status Proposed. Approved Decision é None em cada documento. A matriz humana usa PENDING_APPROVAL. As referências de código descrevem o snapshot e5bf…, não provam deploy. Os resultados da PoC homologam apenas o pacote experimental no ambiente reportado. Nenhum contrato, schema, flag, migration ou política de retenção foi criado para runtime nesta fase.
