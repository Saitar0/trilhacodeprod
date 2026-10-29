# Fase 2.1A.12C.15 — Contrato de enforcement editorial

**Status:** contrato técnico proposto para futura implementação. Políticas P1–P8 ratificadas como diretrizes; nenhuma implementação operacional autorizada. O documento acompanha o [registro de ratificação](editorial-generations-phase-2-1a-12c15-authority-policy-ratification.md), a [transição de permissões](editorial-generations-phase-2-1a-12c15-permission-version-transition.md) e a [matriz JSON verificável](editorial-generations-phase-2-1a-12c15-enforcement-contract.json).

## Fontes e evidência

O IAM versionado segue `JWT → sessão ativa em auth_sessions → usuário ativo em users → papel → PERMISSIONS estático → dependência de rota`. `security.current_user` realiza validação por requisição; `permissions.require` verifica uma permissão global. Não há grant por trilha confirmado no código. Isso prova comportamento do checkout, não do deployment. Evidências: [`security.py`](../../backend/security.py#L75-L110), [`sessions.py`](../../backend/services/sessions.py#L30-L83), [`permissions.py`](../../backend/permissions.py#L9-L31), [`constants.py`](../../backend/constants.py#L5-L16) e [`routes_content.py`](../../backend/routes_content.py#L69-L175).

C8/C10 continuam sendo a única autoridade de revisão editorial proposta: revisão monotônica por trilha, CAS e fencing. Não criar uma segunda revisão por bloco nem duplicar o motor C8/C10. C11/C12 validaram, com registros sintéticos, que autorização e edição podem se ordenar quando os estados relevantes compartilham uma transação; as provas não cobrem IAM implantado ou writers ativos.

## Contrato futuro de grant

Schema lógico, sem nome de coleção operacional definitivo:

| Campo | Obrigatório | Regra proposta |
|---|---:|---|
| `schema_version` | Sim | Inteiro fechado da versão do contrato. |
| `grant_id` | Sim | Identidade estável não derivada de dados privados. |
| `subject_id` | Sim | Identidade lógica resolvida pelo servidor; referência inexistente nega. |
| `track_id` | Sim | Trilha resolvida a partir do recurso no servidor; não aceitar substituição do cliente. |
| `operations` | Sim | Conjunto não vazio de enum fechado; sem wildcard implícito. |
| `state` | Sim | `active` ou `revoked`; estados desconhecidos negam. |
| `epoch` | Sim | Inteiro monotônico, avançado em alteração/revogação relevante. |
| `granted_by`, `granted_at` | Sim ativo | Principal e instante confiáveis, gravados pelo servidor. |
| `revoked_by`, `revoked_at` | Revogado | Principal e instante; nunca apagar para representar revogação. |
| `delegation` | Condicional | Grant pai e limites de operações, quando concedido por delegação. |
| `expires_at` | Opcional, decisão pendente | Se adotado, expiração é checada no commit e não substitui revogação explícita. |
| metadados de auditoria | Sim | Identidade da operação e correlação opaca; sem token, payload ou segredo. |

Invariantes: no máximo um grant efetivo por (subject, track, operation scope) segundo unicidade definida; nenhuma concessão contraditória; epoch monotônico; concessor só administra subconjunto autorizado; autoconcessão negada; grant não substitui papel/permissão global; usuário desativado ou grant revogado não autoriza; referências ausentes/inconsistentes falham fechadas; grant e evento de auditoria de governança confirmam juntos. Índices e forma de unicidade dependem do BSON/identificadores reais e devem ser validados no baseline, sem migração nesta fase.

## Modelo de autorização efetiva

Allow exige cumulativamente: principal autenticado; sessão ativa; conta ativa; papel atual; permissão global pertinente; versão de política aceita; recurso e trilha resolvidos pelo servidor; grant ativo para operação exata ou escopo global explicitamente provisionado; capability emitida pelo servidor e ainda atual; revisão esperada e fence válidos. Falha/timeout da consulta de autoridade resulta em deny/indeterminate, nunca allow. Fence não é autorização, chave idempotente não é credencial, recibo não concede acesso e capability não cria revisão editorial.

Resultados internos distintos: `unauthenticated`, `invalid_session`, `inactive_subject`, `missing_global_permission`, `missing_track_grant`, `revoked_grant`, `operation_out_of_scope`, `stale_authority`, `resource_not_found`, `indeterminate`. A resposta externa deve evitar enumeração: recurso inexistente e inacessível podem compartilhar resposta conforme contrato HTTP aprovado; não expor nomes de grants, epochs internos ou detalhes Mongo. 401/403/404/409/412/422/503 são opções de mapeamento, ainda sujeitas ao contrato de produto/API.

## Capability, revision, fence e recibo

Capability é contexto não-forjável emitido pela fronteira confiável após IAM e resolução server-side; vincula ator, sessão/versionamento relevante, papel/policy version, track, operação, grant epoch, `operation_id`, revisão esperada e preparação editorial. Sua validade lógica termina quando algum estado vinculado muda; no commit os estados autoritativos são revalidados/ordenados. Não aceitar capability do cliente.

* **Revisão/CAS:** autoridade editorial C8/C10 sobre estado e concorrência lógica.
* **Fence:** impede writer obsoleto de confirmar; não prova identidade ou privilégio.
* **Idempotency-Key/operation id:** identifica a mesma intenção sob escopo definido; não autoriza leitura ou escrita.
* **Recibo:** resultado histórico mínimo, sem payload; replay externo verifica autorização atual.

## Sequência lógica da confirmação

1. Validar JWT e sessão; obter usuário atual e negar se desativado.
2. Verificar permissão global conforme versão de política ativa.
3. Carregar o recurso, resolver cadeia/track no servidor e checar grant/escopo global para operação exata.
4. Validar o request sem converter campo ausente em `null`; canonicalizar intenção em fronteira com campos permitidos; associar identidade idempotente estável.
5. Emitir capability vinculada ao contexto autorizado.
6. Abrir uma sessão/transaction no mesmo cliente assíncrono e na autoridade compatível aprovada.
7. Dentro da fronteira, condicionalmente verificar/participar do grant e epoch; usuário ativo, papel, sessão e escopo administrativo precisam participar ou ter mecanismo de transição coordenada equivalente. Uma checagem inicial não fecha corrida.
8. Aplicar CAS da revisão editorial por trilha e fence C8/C10. Rejeitar revisão/fence obsoletos.
9. Executar a mutação específica da família; não presumir que publicação, import ou restore seja update simples.
10. Gravar auditoria editorial obrigatória, histórico minimizado e recibo idempotente na mesma unidade de confirmação.
11. Confirmar uma vez. Em resultado de commit indeterminado, reconciliar pelo ID estável em canal interno; nunca repetir a mutação às cegas.
12. Para replay externo, reautorizar agora; retornar recibo mínimo e não reconstruir bloco removido nem expor estado privado.

Uma transação só ordena estados que efetivamente participam do mesmo mecanismo transacional/serializável. Estado IAM externo precisa de coordenador linearizável demonstrado ou aceitação explícita de garantia menor; revalidar duas vezes apenas move a janela. Se o commit de revogação e o editorial colidem em registro/epoch comum, a transação obsoleta falha/conflicta; se a edição confirma primeiro, o histórico confirmado permanece válido.

## Papel, sessão e matriz Python

`users` e `auth_sessions` existem no código versionado, mas o commit editorial não compartilha ainda sua leitura/versão. Para garantia forte, alterações de estado relevantes precisam incrementar versão persistida e disputar a transação editorial, ou o rollout deve drenar instâncias/writers antigos de forma demonstrável. A matriz `PERMISSIONS` em Python não tem epoch persistido: usar estratégia híbrida de policy epoch persistido + drenagem e troca coordenada, conforme [documento de transição](editorial-generations-phase-2-1a-12c15-permission-version-transition.md). Até isso existir, política estática obsoleta é bloqueador.

JWT válido não substitui estado de sessão. Alteração de papel carregada em nova request não ordena automaticamente uma transação já iniciada. Desativação, remoção de `content.write`, invalidar `auth_sessions` e revogar admin scope precisam de versão/registro autoritativo ou barreira de rollout que cubra todos os writers. Não afirmar que o mesmo registro de grant resolve automaticamente esses casos.

## Auditoria e dados

Auditoria editorial (o que mudou), auditoria de autoridade (grant/delegação/revogação/scope), histórico, recibo, fingerprint HMAC e logs são classes distintas. Contrato recomendado: ação fechada, ator lógico, escopo, operação, epoch/revisão, instante confiável, correlation ID opaco e resultado; sem token, payload integral, conteúdo de resposta, segredo, mensagem de exceção ou fingerprint em log. A auditoria de grant deve identificar grant lógico, subject, track, operações, epoch anterior/novo, concedente/revogador e instante; não deve copiar motivo livre que possa carregar conteúdo privado. Tentativas negadas podem usar audit/security channel separado e não precisam participar da transação editorial se não houve mutação, desde que a falha de gravação nunca autorize a operação nem vaze detalhes. Recibo mínimo contém identidade da operação, status histórico e revisão; ACL de consulta não é herdada automaticamente do papel editor. HMAC fornece integridade/correlação controlada, não confidencialidade. ACL, retenção, exclusão, rotação/perda de chave e leitores autorizados exigem decisão de produto/segurança.

## Famílias de writer e extensões

| Família | Extensão necessária ao contrato comum |
|---|---|
| CRUD/reordenação de track, node, block e relation | Resolver trilha; uma intenção/revisão por trilha; validar invariantes relacionais; mutação/audit/receipt atômicos. |
| Duplicação/importação | Autorizar origem e destino; operação composta idempotente; staging privado e ativação indivisível; coordenar todos writers concorrentes. |
| Publicação/snapshot | Capturar snapshot da revisão exata; geração imutável; validar artifacts; trocar head público atomicamente; leitores pinados; não expor candidato incompleto. |
| Restauração | Criar nova revisão/generation a partir de fonte validada; state machine e recibo; fencing por lote ou commit atômico; preservar tentativas/progresso. |
| Exclusão | Contrato explícito de retenção/retirada; impedir cascade involuntária do estado de aluno; tombstone/recuperação só após decisão de produto. |
| Taxonomia global | Autoridade/epoch global separada do grant por trilha; impacto transversal e snapshots classificados antes de escrever. |
| Seed/migração/CLI | Identidade de execução explícita, target allowlist/preflight, sem caminho operacional silencioso; mesma contenção e auditoria quando tocar estado protegido. |
| Auditoria/helper | Receber session/transaction e gravar junto; falha aborta mutação obrigatória. |

A lista individual preserva os 17 IDs/classificações C13 na [estratégia dos writers](editorial-generations-phase-2-1a-12c15-writer-enforcement-plan.md). Todos continuam `runtime NOT_VERIFIED`.

## Limites

O contrato não é enforcement até todos os writers do scope e identidades de execução serem cobertos ou impedidos de escrever. Uma convenção, import central ou feature flag de rota não basta. Não se demonstrou topologia Mongo implantada, papéis DB, grants reais, call graph externo, comportamento multinó, política de ACL/retention nem compatibilidade HTTP. O veredito C14 de ausência de primeira onda segura permanece.
