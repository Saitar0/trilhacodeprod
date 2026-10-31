# Fase 2.1A.12C.12 — Prontidão para integração editorial IAM

**Conclusão:** existe um mecanismo experimental de ordenação por transação, mas ainda não há prontidão para conectar o IAM ativo. Fonte de grant, escopo administrativo, versão da política global e evidência operacional precisam ser resolvidos antes de mudança funcional.

## Pré-requisitos de decisão e evidência

| Dependência | Estado observado | Critério para desbloquear etapa futura |
|---|---|---|
| Fonte da identidade e papel | Código usa JWT, `users` e papel recarregado por request | Confirmar o proprietário e contrato de `users` na linha/runtime aprovada; não aceitar principal do cliente |
| Sessão | `auth_sessions` guarda digest, owner, expiração e revogação | Confirmar mesmo armazenamento/topologia de confirmação; definir epoch/participação sem alterar o contrato de logout |
| Permissões globais | `PERMISSIONS` é uma constante Python por papel | Decidir se matriz permanece versionada no artefato, com epoch de rollout, ou passa a uma policy persistida; nenhuma seleção foi feita |
| Grants por trilha | Não encontrados na autorização de escrita ativa | Aprovar um único schema/authority, operações cobertas, grantor/revoker e política explícita de admin global |
| Ordenação | C12 provou touch condicional dos três estados no mesmo MongoDB descartável | Confirmar que usuário, sessão, grant, C8, conteúdo e auditoria podem compartilhar uma transação na topologia selecionada |
| Esquema operacional e permissões DB | Não conectados/consultados | Evidência sanitizada de schema, índices, grants Mongo e concerns; não usar configuração operacional nesta fase |
| Cobertura de writers | C4 inventariou caminhos versionados W-01–W-12; W-13 é PoC | Provar runtime e tratar cada writer/worker/script capaz de bypass antes de habilitar escopo |
| Release e runtime | ADR-008 permanece bloqueado | Handoff sanitizado aprovado, serviço/digest/proveniência/rota/readiness/linha-alvo confirmados pelo responsável autorizado |
| ACL e retenção | Não definidas | Decisão de produto/privacidade/segurança antes de leitura externa, expiração de recibos, histórico ou limpeza |

## Famílias de escritores que condicionam a integração

Os grupos abaixo vêm do [inventário estático C4](editorial-generations-phase-2-1a-12c4-writer-inventory.md). Eles não estão confirmados no runtime:

| Família | Evidência C4 | Requisito futuro para não haver bypass |
|---|---|---|
| CRUD/reordenação de tracks, nodes, blocks e relations (W-01/W-04/W-05/W-06) | Updates diretos; sem CAS editorial/fence comum | Comandos cobertos pela mesma revisão, grant e idempotência; nenhum endpoint legado escrevendo às mesmas coleções |
| Duplicação/exclusão (W-02 e efeitos W-01/W-04) | Inserts em sequência/cascatas multicoletânea | Operação composta única ou fluxo recuperável aprovado; política de referências/retention antes de delete |
| Publicação e snapshots (W-03/W-10) | Efeitos preparatórios antecedem CAS final de `tracks.version`; contagem não prova snapshot coerente | Separar revisão editorial de geração/head público; cumprir ADR-006 e cobrir readers antes de publicar |
| Taxonomias/tags/tipos (W-07) | Escrita global/referências cruzadas; alguns caminhos não propagam ator | Definir autoridade/catalog scope, auditoria e impacto em trilhas; não usar grant por track para esconder efeito global |
| Import (W-08) | Lease/job/marker, writes sequenciais e multicoletânea | Fence em cada confirmação ou staging privado + confirmação composta; retry idempotente e nenhuma coexistência descoordenada |
| Restore (W-09) | Job/lease; delete e reinserção em batches | Tratar como nova revisão com recovery/fence; bloquear concorrência import/CRUD até protocolo comum |
| Scripts/seeds/migrations/restore CLI (W-11) | Comandos versionados executáveis; invocation no runtime não confirmada | Catalogar identidade, execução, allowlist e remover/bloquear caminho não migrado; não presumir inatividade |
| Writer privado/PoC (W-12/W-13) | Armazenamento isolado ou inelegível; chamadas operacionais não provadas | Manter desligado até origem, ACL e revisão aprovadas; não incluir em coverage de integração sem prova |

O [plano C4](editorial-generations-phase-2-1a-12c4-integration-readiness.md) registra que lease/marker, inventário, ferramenta e adaptador isolado não provam que todos os writers usam CAS/fencing. Nenhum corte parcial é seguro enquanto escritor incompatível puder gravar o mesmo estado editorial.

## Sequência mínima futura

| Etapa | Objetivo e arquivos possivelmente afetados | Dependências e testes necessários | Entrada / saída / bloqueio | Recuperação e evidência | Aprovação futura |
|---|---|---|---|---|---|
| 1. Autoridade e admin | Definir `users`, `auth_sessions`, policy global, grants; documentos de arquitetura | Revisar JWT/session/role/grants; cenários admin global e revogação | Entrada: owner IAM. Saída: uma fonte sem concessões contraditórias. Bloquear se autoridade/owner ambíguo | Sem mudanças de estado; ata da decisão | Aprovação humana de fonte e grantors |
| 2. Grant e revogação | Aprovar schema, epochs, scope e audit de autorização | Migração apenas em plano; teste de schema/índices/backfill em cópia sintética | Bloquear em grant wildcard implícito, retenção sem decisão ou auditoria irrecuperável | Não mudar produção; rollback de desenho antes da migração | Aprovação de produto/segurança/privacidade |
| 3. Compatibilidade da autoridade | Adaptador experimental de `users` e `auth_sessions` com schema sintético realista | Testar corrida papel/sessão/grant com C8/C10 no replica set descartável | Saída: transação única com negative cases. Bloquear se storage difere ou permission code não tem epoch | Preservar C11/C12; artefato removível sem conexão ativa | Nova autorização técnica isolada |
| 4. Fronteira de capability | Resolver recurso e trilha; emitir capability server-side | JWT/session reais apenas em harness seguro; negativos actor/track/op/role, fence separado | Bloquear se resolver trilha é ambíguo, session check sem ordem ou capability serializada ao cliente | Sem rota ativa; documentação/API contract | Aprovação API/IAM específica |
| 5. Writer piloto seguro | Integrar um writer só quando houver exclusão mútua do legado para a mesma entidade | CAS/fence, auditoria, receipts, retries, import/restore interleavings e falha pós-commit | Entrada: baseline ADR-008 + cobertura de writers em escopo. Bloquear se qualquer bypass pode atuar durante teste | Manter escrita bloqueada/read-only na incerteza; nunca fallback silencioso | Nova autorização de código e dados sintéticos/ambiente explicitado |
| 6. Cobertura por família | Converter, bloquear ou provar remoção de cada CRUD/import/restore/publish/script | Regressões da família, cobertura real e processo externo autorizado | Não avançar se caminho residual puder gravar sem protocolo | Reversão por família só se fonte e heads compatíveis; sem duas autoridades | Aprovação por escopo e rollout |
| 7. Observabilidade e auditoria | Eventos mínimos de execução e eventos funcionais de grant | Privacidade/ACL; eventos não substituem auditoria obrigatória | Bloquear se observabilidade coleta payload ou se ausência de evento for tratada como prova de ausência | Instrumentação pode falhar aberta, auditoria obrigatória não | Aprovação operacional posterior |
| 8. Snapshot/publicação/leitores | Reconciliar revisão, generation immutable e head público | ADR-005/006; concorrência, pinning, no-mix, público/privado e session tests | Bloquear até origem estável e writer coverage; revisão CAS não é CAS de head | Sem fallback a live collections; recuperação de geração independente | Aprovação de publicação e cutover separadas |
| 9. Rollback/cutover | Trocar linha controladamente | Baseline, ensaio, métricas, rollback sem escritor bypass | Bloquear se cliente/worker residual não estiver coberto ou se rollback reabre grant/revision velha | Modo escrita pausada; correção como nova revisão; sem reset de histórico | Aprovação de operação/release e responsável |

### Dependências obrigatórias versus opcionais

Obrigatórias antes de qualquer writer ativo: fonte e grant aprovados; política de administrador/revogação; ordenação de sessão/papel/permissões; baseline ADR-008; compatibilidade do driver/schema; auditoria transacional; cobertura ou bloqueio de todo writer capaz de bypass no escopo; rollback seguro; autorização específica de implementação. Métricas de performance, otimizações de índices e expansão para gerações podem ser posteriores se não forem pré-condição de correção, mas não substituem nenhum bloqueio obrigatório.

## Matriz de autoridade e operação futura

| Mudança | Estado que deve ser ordenado com commit | Evidência exigida |
|---|---|---|
| Revogar grant de trilha | Mesmo grant/epoch lido e condicionalmente tocado na transação | Commit-before-revoke e revoke-before-commit; corrida sem estado parcial |
| Alterar papel/remover `content.write` | Registro `users` ou epoch de policy atualizado, além da reavaliação das permissões | Role-change durante request e no ponto de commit; atualização estática de policy durante rollout |
| Invalidar sessão | Documento `auth_sessions` da sessão cujo digest está no JWT | Logout/revoke concorrente com confirmação; nenhuma capacidade de reviver sessão em replay |
| Revogar admin global | Registro do escopo global explícito, mais papel/epoch do usuário | Wildcard negado sem grant explícito; revogação ordenada em qualquer trilha |
| Replay externo | Estado atual de usuário/sessão/permissão/grant e recibo persistido | Negativo após revogação/role demotion, sem conteúdo privado e sem segunda mutação |
| Reconciliação interna | Recibo por identidade de operação confiável | Leitura read-only e scoped; consulta interna não funciona como autorização de cliente |

Nenhum único `authorization_epoch` isolado resolve estados em fontes que não participam de atualização coordenada. Epoch de sessão, papel/policy e grant são decisões lógicas distintas; podem compartilhar uma transação, mas não devem ser confundidas com revisão editorial ou fence de writer.

## Plano de rollback

1. Antes de cutover, preservar as coleções legadas e manter writer novo inacessível aos serviços ativos.
2. No futuro primeiro rollout, limitar o escopo e bloquear operações editoriais durante divergência/rollback; não permitir que a rota antiga volte a escrever após revisão ou geração nova.
3. Não desfazer transação confirmada por apagar receipt/history/audit. Se for necessário corrigir conteúdo, criar nova revisão autorizada.
4. Não reabrir grant/session revogado para recuperar capacidade; qualquer concessão exige novo evento e aprovação.
5. Não resolver commit indeterminado reexecutando mutação. Reconciliar operation ID/fingerprint e retornar indeterminado se não houver evidência.
6. Inverter schema/backfill só após verificar referências; a etapa de migração não foi aprovada nem testada.

O ponto irreversível é publicação/consumo por leitores ou eliminação de informação/histórico; estes exigem gates e autorizações distintos. Uma flag, isoladamente, não fecha a janela de concorrência nem bloqueia writers externos.

## Critérios de bloqueio

* Fonte de grant, global admin, grantor/revoker ou acesso a auditoria sem decisão.
* Revogação/papel/sessão em store externo ou projeção que pode estar stale sem protocolo de ordenação.
* Política estática `PERMISSIONS` sem estratégia de versão durante rollout.
* Falta de prova de transação/session/topology ou database roles no alvo.
* Identidade do bloco/trilha não resolvida sem ambiguidade.
* Writer legado/job/script/seed com acesso às mesmas coleções e sem controle comum.
* Compromisso de auditoria ou retry que pode deixar partial state ou duplicar efeito.
* Necessidade de alterar IAM/config/schema ativo sem autorização específica.
* ADR-008 sem baseline sanitizado do serviço/digest/proveniência/rota/readiness/linha.

## Gates e ADR-008

Estados históricos inalterados: G1 `PARTIAL`; G2 `NOT_VERIFIED`; G3 `NOT_VERIFIED`; G4 `PARTIAL`; G5 `NOT_VERIFIED`; G6 `PARTIAL`; G7 `PARTIAL`; G8 `NOT_VERIFIED`; G9 `BLOCKED`; G10 `BLOCKED`. C12 contribui evidência de mecanismo synthetic para G2, não cobre escritores reais. ADR-008 segue bloqueado; não houve acesso a infraestrutura. O handoff sanitizado da C12B.4B permanece referência e não foi repetido.
