# Fase 2.1A.12C.12 — Autoridade IAM editorial e ordenação de revogações

**Escopo:** inspeção do código versionado na base C11 e prova isolada com documentos sintéticos. Não altera o IAM ativo e não demonstra a configuração implantada.

## Conclusão

O código atual autentica o sujeito por JWT assinado, valida uma sessão server-side, recarrega o usuário e deriva permissões de uma tabela estática por papel. O acesso de escrita observado é global por papel: não foi encontrada autorização de escrita por trilha. O `can_view_track` existente é uma regra de leitura/visibilidade, não um grant editorial.

A prova C12 confirmou que a revogação de papel, sessão ou grant pode ser ordenada com o commit **quando a autoridade correspondente é condicionalmente tocada na mesma transação MongoDB** que revisão, fencing, alteração editorial, auditoria, histórico e recibo. Dois contraexemplos persistentes demonstraram que uma consulta externa — mesmo repetida imediatamente antes do commit — e uma projeção eventualmente consistente não fornecem essa ordenação.

Isso não escolhe definitivamente a arquitetura operacional. A implantação, o armazenamento real, os papéis administrativos e a política da matriz estática de permissões ainda requerem decisão/evidência.

## Evidência do IAM versionado

| Fato no código | Evidência | Interpretação e limite |
|---|---|---|
| JWT de acesso é assinado com algoritmo fixo e contém `sub`, `sid`, `ver`, tipo e expiração de 15 minutos. | [`security.py`](../../backend/security.py#L33-L47) | O token identifica sujeito/sessão; claims enviados pelo cliente não são a fonte atual de papel ou permissões. O segredo/configuração implantados não foram consultados. |
| Cada requisição valida o token, exige sessão ativa, lê `users`, verifica conta/versão/e-mail e calcula permissões pelo papel carregado. | [`current_user`](../../backend/security.py#L87-L112) | A validação de papel é atual por requisição no código. Uma requisição que já obteve o principal pode manter esse snapshot até sua operação terminar. |
| A sessão é armazenada em `auth_sessions` com ID em SHA-256, `user_id`, criação, expiração e `revoked_at`; expiração declarada é sete dias. | [`sessions.py`](../../backend/services/sessions.py#L13-L47) | A sessão em banco pode invalidar um JWT ainda criptograficamente válido. O estado implantado não foi consultado. |
| A validação procura digest, sujeito, expiração futura e `revoked_at: null`; logout atualiza o registro da sessão. | [`sessions.py`](../../backend/services/sessions.py#L50-L83), [`logout`](../../backend/routes_auth.py#L215-L237) | O JWT sozinho não mantém acesso depois de uma revogação observada por uma nova requisição. A consulta atual não participa da transação editorial. |
| Cadastro atribui `student`; papéis permitidos são `admin`, `editor`, `student`; permissões vêm de `PERMISSIONS` em código. | [`auth.py`](../../backend/services/auth.py#L85-L99), [`constants.py`](../../backend/constants.py#L5-L15) | A autorização global é uma matriz estática versionada no código, não um grant persistido por trilha. |
| `/api/users/{user_id}/role` exige `users.manage`; o serviço atualiza `users.role` e depois grava auditoria `role_changed`. | [`routes_auth.py`](../../backend/routes_auth.py#L277-L283), [`change_user_role`](../../backend/services/auth.py#L221-L229) | A escrita de papel e sua auditoria não compartilham transação. A função não incrementa `token_version`; isso não impede que novas requisições vejam o papel atualizado, pois `current_user` recarrega o usuário. |
| Mudanças de senha/reset/confirmação podem incrementar `token_version`. | [`auth.py`](../../backend/services/auth.py#L138-L153), [`auth.py`](../../backend/services/auth.py#L179-L205) | A comparação com `ver` invalida tokens existentes. Não substitui a verificação da sessão individual. |
| O endpoint `PUT /api/blocks/{block_id}` exige `content.write`; o serviço recebe o usuário, mas não existe grant editorial por trilha nessa fronteira. | [`routes_content.py`](../../backend/routes_content.py#L166-L173), [`permissions.py`](../../backend/permissions.py#L9-L23) | A permissão global do papel não prova acesso à trilha específica do bloco. |
| `can_view_track` permite staff ler ou aluno ler trilha publicada/pública elegível. | [`permissions.py`](../../backend/permissions.py#L25-L31) | Regra de leitura, não autorização de edição por recurso. |
| Clientes/serviços usam o mesmo objeto `db` criado por `AsyncMongoClient` no código. | [`database.py`](../../backend/database.py#L1-L8) | Sugere um limite lógico comum no código versionado; não prova URI, nome de banco, topology, grants Mongo ou runtime implantado. ADR-008 segue bloqueado. |

### Demonstrado em testes versionados e na C12

O teste de regressão existente demonstra que mudança de papel passa a afetar uma sessão já aberta, promovendo e rebaixando o papel; veja [`test_auth_role_refresh.py`](../../backend/tests/test_auth_role_refresh.py#L6-L29). Testes de sessão exercitam logout, refresh, expiração, desativação e invalidação por alteração de senha no ambiente próprio da suíte; veja [`test_auth_sessions.py`](../../backend/tests/test_auth_sessions.py#L30-L85) e [`test_auth_sessions.py`](../../backend/tests/test_auth_sessions.py#L145-L221). Eles não foram executados nesta fase contra configuração de aplicação.

Nesta fase, a implementação real de `security.py` e `services/sessions.py` foi carregada em testes isolados com JWT sintético e coleções em memória. Foram exercitados token válido/expirado/malformado, sessão ativa/revogada, usuário desativado, versão divergente e atualização do papel recarregada. Esses testes exercitam o código Python, mas os doubles **não** validam MongoDB operacional.

## Autoridade proposta para deliberação

Proposta de menor duplicação de autoridade, sujeita a aprovação e evidência de ambiente:

1. **Identidade e papel:** manter `users` como fonte do sujeito, conta e papel, conforme o contrato atual; não aceitar `actor_id` ou papel de body/header como principal.
2. **Sessão:** manter `auth_sessions` como fonte de sessão individual e seu `revoked_at`/expiração.
3. **Permissão global:** reconhecer que `PERMISSIONS` é hoje política em código. Para ordenação transacional durante alterações dessa matriz ou rollout, será necessário representar uma versão de política com mecanismo de atualização ordenado, ou provar uma fronteira de release que drene operações antigas. A escolha está pendente.
4. **Grant editorial:** um único registro por ator e escopo de trilha em uma fonte aprovada. Não manter fontes independentes capazes de conceder grants contraditórios.
5. **Confirmação:** a operação editorial deve revalidar/participar condicionalmente de usuário, sessão e grant na mesma transação MongoDB do CAS editorial C8. O fence continua autoridade de escritor, não IAM.
6. **Grant global administrativo:** não presumir que papel `admin` significa acesso universal de escrita. Exigir grant/scope global explícito e política humana definida.

Não está decidido quem recebe poder de conceder/revogar grants. `users.manage` hoje permite alteração de papel, mas não é evidência de que tenha sido concebido para grants editoriais. Uma permissão administrativa editorial própria seria uma proposta, não um direito já existente. O fluxo futuro deverá registrar concedente/revogador e produzir auditoria de autorização protegida; a auditoria da alteração editorial permanece distinta.

## Modelo experimental de grant

O módulo [`experimental_editorial_grants.py`](../../backend/curriculum_contract/experimental_editorial_grants.py) define schema fechado sintético:

| Campo | Uso experimental |
|---|---|
| `_id` | SHA-256 de ator e escopo para unicidade determinística; não é autorização secreta. |
| `schema_version` | Versão do schema experimental. |
| `actor_id`, `track_id`, `scope_kind` | Sujeito e escopo exato; `*` só com `global_admin_scope=true`. |
| `allowed_operations` | Lista fechada: `block.update`, `content.publish`, `content.delete`. |
| `state`, `authorization_epoch` | Estado ativo/revogado e geração monotônica do grant. |
| `granted_by`, `revoked_by`, `granted_at`, `revoked_at` | Proveniência mínima da mudança. Não constitui histórico imutável completo. |

Campos extras, operações desconhecidas, timestamp sem timezone, wildcard sem escopo explícito e estado revogado sem revogador/data são rejeitados. A prova não define índices operacionais: `_id` dá unicidade no teste; índices administrativos e de consulta precisam de sizing e validação no armazenamento alvo.

## Capabilities, autorização e fencing

A implementação [`experimental_editorial_iam_authority.py`](../../backend/curriculum_contract/experimental_editorial_iam_authority.py) emite uma capability HMAC após ler o principal, sessão e grant sintéticos. A capability vincula ator, digest de sessão, papel, trilha resolvida, operação e epochs dos três estados. O escopo do bloco/trilha deve ser resolvido no servidor; se um escopo pedido diverge do resolvido, a decisão é negada.

O harness vincula a capability a uma atualização/commit, mas **não** a transforma em credencial HTTP operacional. A capability não contém fence. O adaptador C8/C10 valida o writer credential e fence; a autoridade IAM decide quem pode agir; a autorização de trilha não substitui `content.write` global nem vice-versa.

O objeto Python isolado não constitui uma fronteira de segurança por si só. Segurança futura depende de construção apenas por dependência confiável após JWT/sessão/papel/permissão e resolução do recurso pelo servidor, assinatura/validação, escopo, revalidação transacional e não exposição ao cliente.

## Semântica experimental de revogação

Regra testada: **se a revogação for confirmada antes do commit editorial, o commit é rejeitado; se o commit ganhar primeiro a ordenação transacional, a revisão e auditoria confirmadas permanecem válidas e a revogação é aplicada em seguida.** Revogar não apaga o histórico de uma operação anterior.

Na prova, o participante da transação do C8 atualiza condicionalmente os documentos sintéticos de principal, sessão e grant, conferindo os epochs e estado ativo. Essas escritas competem com as atualizações de revogação nos mesmos documentos. A operação editorial, CAS de revisão/fence, auditoria, histórico e recibo usam a mesma sessão/transação do AsyncMongoClient.

Foi exercitado:

* grant revogado depois da preparação e antes da confirmação: negado, revisão/conteúdo/auditoria/recibo sem commit;
* papel rebaixado, `content.write` removido e sessão revogada no mesmo intervalo: capability anterior negada e sem estado editorial parcial;
* revogação concorrente iniciada quando a transação já tocou o documento, em grant, principal e sessão: a transação observada concluiu integralmente antes da revogação; não houve estado misto;
* duas operações concorrentes com mesma revisão esperada: uma confirmou, a outra não, com uma única auditoria/revisão;
* fence antigo após avanço: C8 rejeitou o writer; a capability não foi tratada como fence.

### Limites desta garantia

Essa ordenação só abrange fatos cujo estado participa da transação e cuja alteração de revogação escreve o mesmo registro coordenado. Consulta inicial, segundo check ou capability assinada, sem escrita condicional/transacional na autoridade não impedem revogação posterior.

Na aplicação atual, `users`/`auth_sessions` e conteúdo são acessados por um `db` comum no código, mas C12 usou coleções `c12_*` sintéticas. Portanto, o teste não demonstra que URI/runtime, database roles, topology, transaction concerns ou schemas implantados permitem compor esses documentos numa transação. A matriz `PERMISSIONS` em Python não é documento Mongo e não é serializada automaticamente por esse mecanismo.

## Comparação de arquiteturas

| Modelo | Ordenação da revogação | Prova C12 | Limite / decisão |
|---|---|---|---|
| **A. Grant e estados IAM coordenados na fronteira MongoDB editorial** | Pode ordenar grant, papel e sessão se cada alteração e commit escrevem os mesmos documentos/epochs na transação responsável. | Persistente: sucesso, revogação pré-commit e corrida nos três tipos de documento com C8/C10 em replica set descartável MongoDB 7. | Demonstra mecanismo, não adaptação ao schema/runtime atual. Requer fonte única, compatibilidade de topologia, roles Mongo, índices e transações. Não duplicar `users`/`auth_sessions` em outro IAM sem regra de sincronização. |
| **B. IAM externo, check antes do commit** | Não ordena. Depois do último check, a revogação pode confirmar e o Mongo editorial ainda confirmar. Repetir check apenas move a janela. | Contraexemplo persistente determinístico: check (uma e duas vezes), revogação da fonte sintética externa, commit Mongo posterior bem-sucedido. | Sem transação distribuída ou coordenador linearizável, não promete que revogação confirmada preceda commits que já passaram pelo check. Falhas de comunicação precisam negar/ficar indeterminadas, não conceder. |
| **C. Epoch/projeção** | Epoch monotônico ajuda apenas quando a versão lida é atual e sua mudança participa da coordenação de commit. Projeção eventual permite decisões stale. | Contraexemplo persistente: autoridade revogada/epoch 2 enquanto projeção fica ativa/epoch 1; transação editorial baseada na projeção antiga confirmou depois da revogação. | Projeção síncrona com confirmação e alteração coordenadas no mesmo limite equivale operacionalmente ao modelo A. Projeção assíncrona não garante revogação imediata. Sequenciador externo exigiria contrato de ordem, disponibilidade e recuperação próprios. |

## Ameaças da fronteira editorial

Critério qualitativo: `CRITICAL` significa possibilidade direta de escrita não autorizada ou corrupção pública em grande escopo; `HIGH` significa bypass/revogação ou exposição privada com consequência material; `MEDIUM` exige outra falha ou limita alcance; `NOT_VERIFIED` indica que falta evidência, não que o risco seja baixo.

| Ameaça | Impacto | Pré-condição | Mitigação proposta | Evidência/estado |
|---|---|---|---|---|
| 1. `content.write` global edita trilha sem grant | HIGH | Papel com permissão e bloco conhecido | Resolver trilha pelo recurso no servidor e exigir grant exato | Ausência de grant por trilha no código; C12 nega sem grant sintético |
| 2. Capability reutilizada após revogação | HIGH | Capability ainda válida localmente | Epoch + participação condicional na transação | C11/C12 sintéticos; não operacional |
| 3. JWT válido, sessão revogada | HIGH | Request autenticou antes da revogação ou cache | Validar sessão e ordenar seu registro na confirmação | Sessão verificada a cada request; C12 ordenou apenas sessão sintética |
| 4. Papel muda durante operação | HIGH | Principal carregado antes da mudança | Revalidar/tocar registro do usuário ou epoch transacional | Código atual recarrega por request; corrida intra-request não coordenada |
| 5. Grant revogado durante operação | HIGH | Grant consultado antes do commit | Touch condicional na mesma transação | Testado persistentemente com grant sintético |
| 6. Cliente troca `track_id` | HIGH | Endpoint confia no escopo enviado | Resolver bloco→trilha server-side e comparar escopo pedido | C12 compara requested/resolved; route ativa não recebe grant por trilha |
| 7. Cliente forja capability | HIGH | Campo/token do cliente tratado como confiável | Capability assinada, server-issued, nunca aceita do body | Teste de capability alterada rejeitada; contrato HTTP não integrado |
| 8. Fence usado como autorização | HIGH | Processo válido tenta agir em nome de ator sem permissão | Separar IAM de credential/fence C8 | Teste de fence stale e separação estrutural; não operacional |
| 9. Replay de outro ator | HIGH | Idempotency key exposta ou compartilhada | Escopo de recibo por ator/operação/trilha e autorização atual | C11 cobre synthetic replay; API ativa não integra recibo |
| 10. Replay após remoção do bloco | MEDIUM/HIGH | Recibo tenta reconstruir conteúdo excluído | Retornar recibo mínimo somente após autorização atual; nunca recriar bloco | C11/C10 testaram recibo mínimo; ACL/retention pendentes |
| 11. Escritor legado ignora CAS/fence | CRITICAL para consistência de corte | Writer ainda pode escrever as mesmas coleções | Nenhum cutover até todo bypass ser convertido, bloqueado ou removido | C4 documenta bypasses W-01–W-11; runtime não confirmado |
| 12. Auditoria ausente após confirmação | HIGH | Writer e auditoria fora de transação | Auditoria obrigatória na transação editorial | C7 demonstrou lacuna do writer; C8/C10/C11 apenas protótipos |
| 13. Commit indeterminado | HIGH | Cliente perde resposta ou recebe label de commit ambíguo | Reconciliar identidade persistente; nunca repetir cegamente | C11 simulou resposta perdida; falha real de rede/label não provada |
| 14. Recibo/histórico vaza conteúdo | HIGH | Acesso de leitura amplo ou recibo carrega payload | Minimização, ACL por recurso e recibo mínimo | C11 sintético minimiza; ACL atual/implantada e retenção não definidas |
| 15. Cache/projeção stale | HIGH | Revogação não chega ao dado usado no commit | Epoch versionado e atualização coordenada na autoridade de commit | Projeção atrasada permitiu commit posterior em teste persistente |
| 16. Confusão identidade/permissão/grant/fence | HIGH | Um dos atributos substitui os demais | Contratos tipados separados, fail-closed e negativos de teste | C12 usa autoridade/epochs e C8 fence separados; integração pendente |

## Auditoria de autorização, ACL e retenção

Auditoria editorial registra o que mudou; auditoria de autorização registra concessão, revogação, mudança de papel/escopo e tentativas negadas selecionadas. As trilhas não devem compartilhar automaticamente o mesmo público nem os mesmos dados.

Proposta de acesso, ainda não política aprovada:

| Dado | Acesso mínimo a deliberar | Observação |
|---|---|---|
| Conteúdo atual do bloco | Editor com grant atual da trilha; alunos conforme publicação/visibilidade | Não ampliar por possuir recibo. |
| Recibo idempotente | Serviço confiável para reconciliação; cliente autenticado e autorizado para consulta externa | Chave não é credencial; payload/estado privado não compõem o recibo mínimo. |
| Auditoria editorial | Editor autorizado e auditoria interna explicitamente autorizada | Separar do reader de aluno. |
| Histórico de intenção/fingerprint | Serviço de integridade; acesso de auditoria condicionado | Não registrar payload privado ou HMAC em log. HMAC não criptografa dados. |
| Grant e auditoria de autorização | Responsável autorizado por IAM e auditoria interna | Papéis administrativos e API de concessão/revogação não existem como contrato C12. |

Os documentos C12 carregam `granted_by`/`revoked_by` no estado corrente, mas não são um log imutável de cada transição. Uma futura alteração de grant deve registrar evento de auditoria durável no limite de consistência apropriado. Tentativa negada pode ter observabilidade minimizada fora da transação editorial; não registrar tokens, payload, sessão em claro nem conteúdo. Prazo de retenção, expiração de recibos/fingerprints, exclusão e acesso jurídico/privacidade permanecem sem decisão; nenhum prazo é proposto aqui.

## Plano de integração incremental (não autorizado nesta fase)

1. **Decidir fonte de autoridade e política administrativa.** Definir owners para usuário/papel, sessão, grant por trilha, grant global, concessão/revogação e auditoria; escolher a ordem de autorização/permissão global versionada.
2. **Aprovar semântica de revogação e grant.** Aprovar schema, `content.write` + grant por trilha, política explícita de admin global, epochs, ponto efetivo de revogação e acesso/retention.
3. **Provar compatibilidade operacional.** Após evidência ADR-008, verificar topology, MongoDB, PyMongo Async, transações/concerns, database roles, índice e collections reais. Sem isso, bloqueio.
4. **Implementar adaptador de IAM experimental compatível com `users`/`auth_sessions`.** Somente após aprovação; sintetizar campos legados, permissões, active/token_version, digest de sessão e grant em testes; sem ligar rota.
5. **Emitir capability confiável na fronteira HTTP.** Resolver recurso/trilha no servidor, autenticar, validar sessão, papel, permissão, grant e operação; capability vinculada aos epochs/intent, sem fence como IAM. Compatibilidade de API e status codes requer aprovação separada.
6. **Compor IAM e protocolo C8/C10.** Última validação/participação de usuário, sessão, grant, revisão, fence, bloco, auditoria, histórico e recibo no contrato transacional; falhar fechado e reconciliar resultado ambíguo sem replay cego.
7. **Cobrir escritores legados, sem dual-write bypass.** Por família: CRUD/reorder, duplicação/exclusão, taxonomia, import, restore, publish/snapshot, scripts/seeds/workers. Cada caminho precisa usar uma autoridade comum ou estar bloqueado/removido do runtime antes do escopo correspondente ser habilitado.
8. **Testar e observar antes do cutover.** Negativos IAM, revogação, transações, idempotência, privacidade, sessões e compatibilidade em baseline aprovado; instrumentação passiva não substitui auditoria nem enforcement.
9. **Preparar snapshots/publicação/leitores separadamente.** Seguir ADR-005/006: revisão editorial não é geração nem head público; publicação precisa de CAS próprio e leitor pinado por geração.
10. **Rollback e cutover controlados.** Prever janela sem escrita ou writers comprovadamente coordenados; nunca reabilitar writer antigo como fallback contra revisão nova. Exigir autorização específica por etapa.

## Rollback: limites para desenho futuro

Uma transação já confirmada não pode ser “desconfirmada” apagando histórico. Correção posterior deve ser nova revisão sob autorização/fence atuais; auditoria e recibos permanecem. Revogação não deve ser revertida junto com rollback de código. Se o novo caminho falhar, negar/pausar escrita enquanto não houver caminho antigo provadamente compatível; simples feature flag não serializa escritores. A estratégia concreta exige inventário completo, release/baseline operacional e ensaio de rollback, todos pendentes.

## Limitações e gates

* O C12 testou MongoDB 7.0.43 descartável, replica set de nó único, WiredTiger, `AsyncMongoClient` 4.18.2, sessões e transações. `w:majority` em nó único não demonstra tolerância a falha multinó.
* JWT e sessão foram sintéticos nos testes C12; as rotas de teste da aplicação não foram executadas contra o backend. Não se validaram IAM implantado, grants de produção, database roles, caches, topologia operacional ou escritores externos.
* O modelo experimental espelha a matriz `PERMISSIONS`, validada por teste de igualdade no commit-base; uma futura mudança de código requer nova versão/evidência.
* Status históricos preservados: G1 `PARTIAL`; G2 `NOT_VERIFIED`; G3 `NOT_VERIFIED`; G4 `PARTIAL`; G5 `NOT_VERIFIED`; G6 `PARTIAL`; G7 `PARTIAL`; G8 `NOT_VERIFIED`; G9 `BLOCKED`; G10 `BLOCKED`. ADR-008 segue bloqueado; C12 não promove gate.

Referências de escritores e limites: [inventário C4](editorial-generations-phase-2-1a-12c4-writer-inventory.md), [prontidão C4](editorial-generations-phase-2-1a-12c4-integration-readiness.md), [política C11](editorial-generations-phase-2-1a-12c11-authorization-replay-policy.md) e [handoff ADR-008](editorial-generations-phase-2-1a-12b7-adr008-evidence-handoff.md).
