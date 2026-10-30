# Plano proposto — extensões do importador versionado

**Status: sequência para aprovação; sem alterações de produção nesta etapa.** Não executar nenhuma fase abaixo sem autorização própria.

## Princípios de sincronização

- Manter `curriculum_ref` como identidade externa estável e `_id` Mongo como identidade interna. Nunca renumerar o pacote nem produzir IDs por posição de leitura.
- Resolver por um registry/upsert versionado com índice único no escopo da trilha e referência externa. O atual `meta.import_ref` é útil, mas o índice único não está definido para as referências do currículo.
- Hash canônico por conteúdo exclui timestamps/runtime e inclui tipo, payload, ordem e relações semânticas relevantes. Para gabarito privado, não expor hash por questão no relatório público; manter proveniência e controle no processo administrativo.
- Classificação contra snapshot: ausente → candidato a criar; conteúdo atual igual → inalterado; atual ainda igual ao último importado e fonte mudou → atualização candidata; divergência local → conflito.
- Sem snapshot não declarar create/update/unchanged/conflict. Ausência do pacote gera diferença para revisão, nunca delete automático.
- Um `import_run` futuro deve guardar bundle SHA/schema/base, plano, ator autorizado, resultados por entidade e rollback/compensações. Quizzes/projetos publicados usam versões imutáveis.
- Validar o pacote inteiro e dependências antes da primeira escrita. Nenhum caminho parcial pode publicar quiz sem chave privada correspondente, projeto incompleto ou relação não classificada.

## Etapas propostas

| Etapa | Escopo/arquivos prováveis | Dependências | Testes/aceite | Risco e rollback |
|---|---|---|---|---|
| 1. Aprovar decisões curriculares | `MATRIZ_DECISOES_CURRICULARES.md`; sem produção | Aprovação humana de quiz textual, progresso compartilhado, relações | Todas as pendências têm decisão ou bloqueio formal | Sem decisão, nenhuma escrita. |
| 2. Registro de identidade e plano versionado | Novos schemas de import run/registry; `indexes.py`; migration futura | Refs, hash e snapshot aprovados | Unicidade concorrente, colisão, novo/inalterado/conflito; não apagar extras | Migração reversível; índice em DB descartável primeiro. |
| 3. Modelo de conteúdo compartilhado | schemas/services/routes de canonical content e placement; leitura/progresso | Aprovação política per-context/global; migração progress deliberada | Uma entidade canônica, múltiplas placements, ordem, privacidade, progress | Backfill tem risco a progresso; compensar com snapshot e não mesclar sem regra. |
| 4. Modelos e APIs de projeto | schemas/models/services/routes e renderer administrativo/estudante futuro | Contrato de projeto aprovado | Round-trip de entregas/marcos/aceites/rubricas/stack e nenhum marco artificial | Publicação versionada; rollback para versão anterior. |
| 5. Suporte de quiz compatível | quiz schemas/service/serializer/OpenAPI; sem alterar policy sem aprovação | Decisão para resposta livre, correção/revisão, cinco prompts sem chave | Gabarito não vaza; formato não suportado bloqueia; versões e tentativas preservadas | Nunca adaptar existentes silenciosamente; manter quiz não publicado se inválido. |
| 6. Tipos auxiliares e privacidade | checklists, critérios, feedback, solução, objective, notas do instrutor, referências | Destinos e audiência explicitados | Testes de autorização/serialização por tipo | Bloquear tipos sem serializer permitido. |
| 7. Importador 1.0 em modo preview | Módulo separado de importer; endpoints admin novos e autorização | Etapas 1–6; snapshot somente leitura e aprovado | Plano determinístico completo, nenhum write, relatório de toda entidade | Rota legacy continua fail-closed; nada de execução por `dry_run` legado. |
| 8. Simulação de aplicação descartável | integração/test containers; banco isolado | Preview e migration/indexes aprovados | Retry, concorrência, execução por lote, checkpoint e falha parcial | Descartar banco de teste; provar rollback/compensação. |
| 9. Importação experimental | Subconjunto explicitamente homologado, ambiente segregado | Autorização futura específica | Conteúdo, segurança, progresso, links e observabilidade | Snapshot, restore testado e gate de interrupção. |
| 10. Importação integral e validação funcional | Todas as fases, depois de autorização separada | E2E e gates editoriais/operacionais fechados | Reconciliação pós-import e renderer, sem perda nem drift | Plano de recuperação e rollback aprovados antes da execução. |

Os nomes de arquivos são áreas prováveis, não autorização para criá-los agora. Nenhuma etapa deve editar importador legacy para aceitar bundle 1.0 silenciosamente.

## Gates antes de uma primeira escrita

1. 0 bloqueios de schema ou compatibilidade não resolvidos nas entidades a importar.
2. Toda relação enforced tem semântica aprovada; tipo ausente não é convertido em aprovação.
3. Privacidade de gabaritos, soluções e notas comprovada em payloads e logs.
4. Chaves externas únicas e idempotência testadas.
5. Política de progresso compartilhado aprovada e efeito no progresso existente documentado.
6. Projetos completos e versionados; sem associação órfã.
7. Snapshot sanitizado aprovado e verificado; nenhum acesso a DB desconhecido.
8. Dry-run reproduzível; lote/rollback testados em banco descartável representativo.
9. Importação em produção ou banco real autorizada em solicitação separada.
