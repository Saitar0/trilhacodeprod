# C16 — Evidências de bypass de escritores

## Pergunta

Uma transação cooperativa que atualiza a revisão da trilha impede um writer legado que escreve diretamente em coleção? **Não.** A prova usou dois clientes autenticados sintéticos no MongoDB C16:

1. Um adapter C10 preparou a revisão zero, sem confirmar.
2. O cliente legado alterou o bloco diretamente com uma conta MongoDB `readWrite` do banco de teste.
3. O adapter C10 confirmou a intenção e seu próprio estado protocolar.
4. O cliente legado alterou novamente o bloco diretamente.
5. A última escrita ficou persistida sem nova revisão, item de histórico ou auditoria.

O resultado foi observado lendo os documentos persistidos após cada passo. Não houve chamada ao writer real nem acesso a banco não descartável.

## Evidência de prevenção versus detecção

| Controle | Resultado C16 | Classe da garantia |
|---|---|---|
| CAS/fence no caminho C8/C10 | Serializa apenas os participantes que atualizam a mesma autoridade | Prevenção entre writers cooperativos |
| Revisão e auditoria consultadas depois da escrita direta | Desvio pode ser identificado por comparação posterior, mas pode já ter sido confirmado | Detecção, se houver reconciliador; nenhum reconciliador foi testado |
| Identidade sintética `readWrite` | Modificou `content_blocks` sem revisão, fence ou auditoria | Ausência de prevenção para credencial ampla |
| Role sintético restrito a `content_blocks` | Ainda alterou o conteúdo; não atualizou a coleção C8 da autoridade | Contém autoridade, mas não contém o bypass no conteúdo |
| Identidade de banco somente leitura | Não conseguiu atualizar bloco | Prevenção para aquele principal sintético |

Os dois últimos casos não modelam os roles MongoDB da aplicação. Demonstram apenas que retirar escrita da coleção impede o caminho correspondente, enquanto conceder escrita de conteúdo sem encaminhamento ao protocolo mantém o bypass.

## Escritores versionados C13 e contenção futura

Inventário referenciado: `backend/integration_tests/editorial_writer_inventory_c13.json`. As classificações abaixo permanecem as da C13; “C16” indica somente o tipo de evidência produzido agora.

| ID | Símbolos versionados | C13 | Efeito/invariante e contenção futura | Evidência C16 |
|---|---|---:|---|---|
| W-01 | `tracks.create_track`, `update_track`, `reorder_tracks` | A | Revisão/ordem da trilha; participar da mesma autoridade da trilha e auditar | Sem execução do writer real |
| W-02 | `tracks.delete_track` | B | Cascade afeta conteúdo e estado de aluno; bloquear até política de retenção e protocolo composto | Exclusão sintética removeu conteúdo/progresso/tentativa atomicamente; sem política aprovada |
| W-03 | `tracks.duplicate_track` | B | Nova trilha derivada; idempotência, autorização de origem/destino, proveniência e snapshot consistente | Duplicação sintética participou da autoridade da origem |
| W-04 | `tracks.publish_track` | B | Snapshot/publicação/head precisam uma revisão fonte única e ativação atômica | Publicação sintética competiu com edição/import/restore; falha após snapshot abortou |
| W-05 | `nodes.create_node`, `update_node`, `reorder_nodes` | A | Estrutura que influencia conteúdo/snapshot; versão da trilha e escopo | Sem execução do writer real |
| W-06 | `nodes.delete_node`, `duplicate_node`, `clone_nodes` | B | Cascade e duplicação podem afetar progresso/referências; bloquear até invariantes claros | Exclusão/duplicação sintéticas somente |
| W-07 | `blocks.create_block`, `update_block`, `reorder_blocks`, `delete_block` | A | Conteúdo, CAS, auditoria obrigatória e compatibilidade de leitura | Modelo sintético; C7 anteriormente exerceu `update_block`, C16 não |
| W-08 | `relations.create_relation`, `update_relation`, `delete_relation` | A | Relações fazem parte do snapshot/import/restore; mesma revisão quando afetam trilha | Não modelado persistente individualmente |
| W-09 | taxonomias, tags, block types | D | Catálogo potencialmente global/cross-track e snapshots; definir autoridade separada e blast radius | Não modelado; investigação permanece necessária |
| W-10 | `run_import`, `_execute`, `_acquire_import_lock` | B | Lote multi-coleção e workers retomados; common fence, atomicidade/recuperação, idempotência | Import mínimo competiu; falha depois da primeira inserção reverteu tudo |
| W-11 | `restore_version`, `apply_snapshot`, `resume_restore_jobs`, `_claim_restore` | B | Substituição e job retomado; fencing real e recuperação de batch | Restauração mínima competiu; erro abortou substituição sintética |
| W-12 | `integrity.store_snapshot`, `save_version`, migração/reconciliação | A | Snapshot/manifest ligado à revisão imutável; reconciliação não deve tocar learner state sem política | Snapshot sintético protegido pelo CAS comum, não os helpers reais |
| W-13 | seed editorial | B | Não sobrescrever estado ativo nem escapar de revisão; escopo descartável e identidade restrita | Upsert sintético cooperativo × edição; não executou `run_seed` |
| W-14 | `manage.run`, `manage.main`, migrações/índices | B | Cada migração precisa classificar mutação, privilégios e janela; lock de migração não é fence editorial | Não executado; migrações não foram iniciadas |
| W-15 | `immutable_publications.prepare_track_publication` | D | Resolver lifecycle, leituras/ACL e consistência; ativação permanece separada e bloqueada | Não modelado |
| W-16 | `audit.audit` | A | A chamada precisa aceitar a mesma sessão do writer para auditoria obrigatória atômica | Participante C16 gravou evento sintético na transação; helper ativo não foi chamado |
| W-17 | `EditorialGenerationsPoC` | C | Permanecer namespace isolado da PoC, sem ser confundido com runtime | Não executado; exclusion continua baseada em código/inventário C13 |

**Contagem C13 mantida:** 6 A, 8 B, 1 C, 2 D. C16 não altera essas classificações históricas.

## Barreiras necessárias contra bypass

Antes de qualquer cutover, devem ser combinadas e verificadas barreiras em mais de uma camada:

1. **Identidade e privilégios:** separar identidade de writer protocolar de identidades de seed, import, restore, worker e administração; remover privilégios de mutação direta das identidades antigas no escopo protegido. Validar uso real e segredo distribuído por processo.
2. **Bloqueio de entrada:** desligar/restringir rotas, jobs e comandos antigos que não participem do contrato, inclusive retomadas de jobs e scripts operacionais. Uma feature flag apenas no endpoint não bloqueia worker/script.
3. **Serviço de escrita comum:** centralizar chamadas autorizadas e transacionais, sem deixar cada escritor manter um caminho de fallback de escrita direta.
4. **Banco:** validar roles/privileges reais e a menor granularidade suportada. O teste mostrou restrição por coleção, não por documento; qualquer usuário que possa atualizar `content_blocks` ainda pode alterar um bloco diretamente.
5. **Prova de bypass negativa:** sob as identidades antigas e novas, tentar cada caminho e confirmar que o antigo é negado antes que uma mutação protegida seja persistida.
6. **Detecção complementar:** auditoria/reconciliação de divergências pode alertar e apoiar recuperação; não substitui prevenção nem torna uma escrita irregular válida.

Uma transação MongoDB só ordena operações que participam dela. Sem controle dos privilégios efetivos ou sem bloquear as entradas legadas, a aplicação não pode garantir contenção global.

## Escopo dos testes e evidências ainda ausentes

* MongoDB 7.0.43, `rsC16`, nó único, WiredTiger, rede interna, sem portas e sem volume persistente.
* Teste C16 criou identidade `readWrite` temporária por banco aleatório e uma role de teste limitada a `content_blocks`.
* Nenhum usuário real, credencial, URI operacional, dado curricular, sessão de aluno ou conteúdo real foi acessado.
* Não foram inspecionados privilégios de MongoDB implantados; não houve tentativa de conexão operacional.
* O bypass prova possibilidade sob as permissões sintéticas usadas, não que toda identidade de produção possua o mesmo privilégio.
* Os resultados persistentes não abrangem jobs concorrentes reais, cron, command line externo, scripts de migração nem todas as coleções e leituras.

## Conclusão

**Demonstrado:** protocolo comum serializa os cenários cooperativos C16 e transaciona seus efeitos sintéticos.

**Demonstrado:** uma identidade com escrita direta em conteúdo contorna a autoridade C8/C10 sem deixar revisão/auditoria coerentes.

**Não demonstrado:** que a segregação operacional de identidades e os controles de entrada já existam ou possam ser aplicados sem alterar processos ativos. Até essa evidência, o cutover global permanece bloqueado.
