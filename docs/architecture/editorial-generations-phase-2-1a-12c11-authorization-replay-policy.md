# Fase 2.1A.12C.11 — Política experimental de autorização, replay e privacidade

## Escopo e status da evidência

Esta documentação registra uma prova isolada da política autorizada para experimentação. Os módulos C11 e seus dados existem somente nos testes e em um MongoDB 7 descartável. Não foram importados por rotas, serviços ou startup da aplicação. A autorização desta fase não inclui integração operacional.

As afirmações abaixo distinguem: **OBSERVADO NO CÓDIGO** (implementação versionada), **EXERCITADO** (teste executado), **PROPOSTA** (contrato experimental) e **NÃO VERIFICADO** (runtime, IAM ou dados implantados). A Fase C10 continua sendo a fonte do inventário da API e do IAM atual; este adendo não reaudita nem altera aquele contrato: [contrato API/IAM/async C10](editorial-generations-phase-2-1a-12c10-api-iam-async-contract.md) e [relatório C10](editorial-generations-phase-2-1a-12c10-final-report.md).

## IAM existente e limite da prova

**OBSERVADO NO CÓDIGO, conforme a inspeção C10:** a rota ativa `PUT /api/blocks/{block_id}` exige `require("content.write")`; `current_user` valida JWT, sessão, conta e versão do token; `require` consulta permissões associadas ao papel. O código analisado não demonstrou uma regra de escrita por trilha. Referências diretas: [rota](../../backend/routes_content.py#L166), [validação de identidade e sessão](../../backend/security.py#L87), [verificação da permissão](../../backend/permissions.py#L13) e [permissões por papel](../../backend/constants.py#L11). A análise mais detalhada está no [contrato C10, fronteira HTTP e IAM](editorial-generations-phase-2-1a-12c10-api-iam-async-contract.md#fronteira-http-atual).

**NÃO VERIFICADO:** JWT, cookie, sessão real, repositório de usuários, cache ou revogação operacional, grants implantados, escopo por trilha em produção e identidade efetivamente persistida pela auditoria. A identidade e os grants C11 são sintéticos. `content.write` é uma condição necessária no modelo, nunca uma autorização global sobre qualquer trilha.

## Decisão de autorização experimental

A decisão do gate é fechada e distingue autenticação, sessão, permissão global e escopo do recurso:

| Resultado | Condição no modelo C11 |
|---|---|
| `ALLOWED` | Principal atestado pela autoridade sintética; sessão válida; `content.write`; grant ativo para a trilha resolvida (ou escopo global de administrador explicitamente provisionado); operação `block.update` permitida; contexto de writer e fence coerentes. |
| `AUTHENTICATION_REQUIRED` | Principal ausente, adulterado ou sem assinatura da autoridade de teste correspondente. |
| `SESSION_INVALID` | Sessão inválida, digest diferente ou sessão revogada no registro sintético. |
| `PERMISSION_INSUFFICIENT` | Ausência de `content.write` no principal ou no grant atual. |
| `TRACK_SCOPE_DENIED` | Trilha sem grant, operação fora do grant ou papel/escopo incompatível. Administrador não recebe `*` implicitamente. |
| `RESOURCE_NOT_FOUND` | O harness não encontra bloco nem recibo confirmado aplicável. |
| `AUTHORIZATION_REVOKED` | O epoch, papel ou grant deixou de corresponder antes da confirmação. |
| `INDETERMINATE` | A consulta à autoridade sintética falha; nenhuma permissão é presumida. |

O harness resolve `track_id` a partir do bloco sintético armazenado e rejeita divergência com a trilha solicitada. Um bloco sem referência válida não recebe uma trilha inferida. Essa resolução e as permissões exercitadas são prova de uma política C11, não da implementação IAM real.

## Capability e autoridade editorial

`MongoEditorialAuthorizationGate.issue_capability` emite capability somente depois de verificar principal, sessão, `content.write`, grant e operação. A assinatura HMAC do gate vincula ator, papel, digest da sessão, trilha efetiva, escopo do grant, operação, identidade da operação, epoch de autorização, identidade e digest da credencial de writer, fence, revisão esperada e, depois da preparação C8, fingerprint, hash e ID da preparação. A capability não é aceita de HTTP e não pode ser substituída por um fence.

O papel foi incluído nos claims e comparado ao papel atual do grant também durante leitura externa do recibo. Assim, mesmo uma nova identidade sintética do mesmo ator que conserve `content.write`, mas troque de papel, não reutiliza a capability antiga. O teste cobre adulteração de capability, troca de ator/trilha/operação, fence apresentado como falsa autorização e mudança de papel.

**Limite de confiança:** um dataclass Python, um HMAC ou uma autoridade sintética não constituem por si sós uma fronteira de segurança operacional. A autoridade de teste conhece uma chave sintética; o usuário do cliente, IAM, gestão de segredo, proteção do processo e distribuição da capability não foram ligados ao runtime. A integração precisará emitir a capability exclusivamente após a dependência real de autenticação e a política de autorização de recurso.

O C8 continua sendo a única autoridade editorial de revisão e fencing. C11 não cria revisão por bloco, não substitui CAS e não usa o fence como IAM.

## Revogação e ordenação com commit

O grant sintético armazena ator, trilha, papel, permissões, operações, sessão em digest, epoch e sequência de uso. Preparação sem autorização ou revogação antes da confirmação é rejeitada. Antes de chamar o commit C8, C11 consulta o estado atual. Dentro da mesma sessão/transação C8, o participante faz uma escrita condicional no documento do grant, exigindo o mesmo ator, papel implícito no epoch, sessão, permissão, operação e epoch; essa escrita participa da mesma unidade transacional que revisão/fence C8, alteração sintética do bloco, auditoria, histórico e recibo.

**EXERCITADO:** revogação antes da preparação, depois da preparação e antes do commit, e corrida entre uma revogação feita por outro cliente MongoDB e o commit. Como ambos disputam o documento sintético de autorização, MongoDB serializa a escrita concorrente: ou o commit precede a revogação e o pacote inteiro é confirmado, ou a revogação precede e a confirmação é rejeitada. Não há resultado parcial nos interleavings executados.

Essa ordenação vale somente porque a autoridade sintética e o protocolo editorial participam do mesmo MongoDB/transação neste experimento. Se IAM/sessões reais estiverem em outro store, cache ou serviço, a consulta inicial deixa uma janela de corrida e a transação editorial não ordena a revogação externa. A integração precisará definir epoch/lease de autorização transacional ou uma garantia equivalente; esta fase não cria IAM distribuído.

## Replay interno e consulta externa

O protocolo diferencia dois usos:

* **Reconciliação interna:** `lookup_internal_committed_receipt` exige um passe HMAC emitido pela autoridade interna de teste. O passe está vinculado exatamente a banco C11, namespace C8, trilha e operation ID; tentativa de reutilizar em outra trilha é negada. A leitura usa primary e read concern `majority` e retorna somente `revision`, `parent_revision` e a indicação de replay. Estados ausente, pendente, encontrado e indeterminado não revelam payload nem erro de driver.
* **Consulta externa:** `lookup_external_receipt` exige capability assinada, principal atual, papel e `content.write`, grant/escopo vigente e correspondência de trilha/operação. Depois de revogação, papel divergente, sessão inválida ou capability forjada, a consulta é negada. A chave idempotente não serve como credencial.

Uma operação já confirmada retorna o recibo histórico original sem executar novamente a mutação. O teste exclui o bloco depois do commit e confirma que o replay não o recria nem duplica a auditoria. O recibo não representa nem reconstrói o estado atual do bloco. Um serviço interno pode continuar reconciliando um commit confirmado após revogação, mas o resultado só é um recibo mínimo e deve permanecer atrás de uma identidade de serviço real autorizada.

Os passes internos são escopados, mas não têm expiração nem uso único nesta prova; sua autoridade e chave são objetos/processo de teste. Isso permanece requisito de desenho operacional e de proteção contra uso indevido da fronteira interna.

## Respostas HTTP candidatas

Não foi criada rota C11. Para uma futura API versionada, a C10 propôs `If-Match` forte para revisão esperada, `Idempotency-Key` para identidade estável, recibo mínimo em sucesso/replay, `412` para revisão obsoleta, `409` para conflito de intenção/fence, `403` para autorização negada, `404` para recurso inexistente, `428` para precondição ausente e `503` para confirmação indeterminada. São propostas experimentais, não mudanças aprovadas para o endpoint atual. Autenticação continuaria a produzir `401`; corpo inválido, `422`; erros internos, `500` sanitizado. O mapeamento deve ser deliberado junto à compatibilidade de clientes e ao contrato de versão.

## Minimização, HMAC e estrutura persistida

`build_minimal_intent` aceita somente `title`, `data` e `status` e valida os tipos permitidos. O conteúdo do patch é canonicalizado em memória e substituído na intenção persistida por nomes de campos, versão do payload e HMACs com separação de domínio (`intent`, `resource-reference`, `operation-id`). A referência do bloco é keyed; conteúdo privado não é copiado ao payload C8. A auditoria C11 sintética registra ator sintético, campos alterados, referência keyed e timestamp; recibo contém apenas as duas revisões. Os testes inspecionam a operação, auditoria e recibo e não encontram o valor privado sintético.

| Estrutura/campo | Uso neste experimento | Classificação proposta |
|---|---|---|
| Bloco `content_blocks` | Conteúdo editorial legítimo, alterado pela operação sintética | Sensível; acesso editorial atual; não é duplicado em recibo/intenção. |
| `payload_json` C8 reduzido | Tipo/versão, referência keyed, nomes de campos e HMAC de intenção | Necessário para identidade/integridade; ainda sensível correlacionável; ACL e retenção pendentes. |
| Histórico C8 | Revisões, metadados da operação e payload reduzido passado pela fronteira | Necessário à rastreabilidade; nunca presumir que qualquer chamador C8 minimiza payload. |
| Auditoria `edit_history` C11 | Ator sintético, referência keyed, campos alterados e timestamp | Auditoria funcional; exige ACL/retention próprias, não herdadas do bloco. |
| Recibo | Revisão e revisão-pai | Mínimo; não contém ator, chave, conteúdo ou ID do bloco. |
| Segredo HMAC/capability | Somente memória do processo de teste | Proibido em documentos, recibos, logs e saída externa. |
| Payload bruto, resposta privada, exceção, stack trace | Não incluídos nos registros C11 | Proibidos na intenção minimizada, recibo, log ou resposta externa. |

O adaptador C8 genérico ainda recebe payload arbitrário: a minimização está na fronteira C11, não no adaptador em geral. O HMAC assegura integridade/identidade keyed, não confidencialidade: não criptografa o documento original, não elimina correlação sob a mesma chave e não substitui ACL. Não há logs C11 do payload; isso não prova ausência de logs preexistentes em writer/audit operacional.

## Chaves e rotação experimental

As chaves sintéticas têm ao menos 32 bytes, identificador fechado e são mantidas somente em memória. A canonicalização JSON é limitada por tamanho, profundidade e número de nós. Domínios separados evitam reutilizar o mesmo digest entre IDs de operação, intenção e referência. O registro guarda `algorithm`, `key_id` e digest, nunca segredo. Na rotação, a chave nova é atual; IDs de operação candidatos são calculados com a chave atual e as versões antigas ainda retidas, permitindo encontrar operação confirmada antiga. HMAC antigo é verificável somente enquanto sua versão existir; chave ausente/revogada falha fechada.

**EXERCITADO:** replay da operação criada com a versão anterior enquanto a chave anterior permanece disponível; versão explicitamente indisponível rejeita a verificação. **PENDENTE:** armazenamento seguro, distribuição, rotação operacional, revogação emergencial, período de coexistência, backup de chaves, resposta a perda de chave e retenção/expiração de IDs e recibos. Não foi definida duração nem política legal.

## ACL e retenção propostas

Esta matriz é uma proposta de menor privilégio, não uma descrição de papéis existentes. O código C11 testa predicados explícitos para ela, enquanto o IAM implantado não foi validado.

| Recurso | Acesso candidato | Negado por padrão |
|---|---|---|
| Conteúdo editorial | Editor com escopo vigente ou projeção pública aprovada | Aluno/usuário sem escopo para conteúdo privado; ator revogado. |
| Recibo mínimo externo | Ator autenticado, sessão atual, escopo da trilha, mesma operação | Chave idempotente isolada, ator diferente, sessão inválida ou revogação. |
| Recibo interno para reconciliação | Serviço interno autenticado e limitado a operação/trilha | Usuário externo, permissão global sem escopo explícito. |
| `edit_history` e histórico | Ator com escopo ou serviço/revisor explicitamente autorizado | Público/aluno; concessão não decorre de acesso ao bloco. |
| Fingerprint e intenção C8 | Serviço de integridade estritamente necessário | Editor/cliente, aluno e endpoints públicos. |
| Segredos HMAC/capability | Serviço que assina/verifica, por segredo separado | Banco, documento, cliente e logs. |

Papéis “revisor”, “auditor interno” e “serviço de integridade” são categorias de desenho, não roles existentes confirmados. ADR-004 permanece com política de retenção pendente. Referências válidas, privacidade, requisitos legais, retenção de audit, histórico, recibos, fingerprints e condições de GC continuam sem prazo decidido. A C11 não apaga dados nem cria job de limpeza.

## Cancelamento e resultado indeterminado

**EXERCITADO:** cancelamento durante o callback pré-commit, depois da atualização do bloco na transação e antes da auditoria/commit, propaga `CancelledError` e não confirma revisão, bloco, auditoria, recibo nem incremento de uso do grant. Falha sintética de auditoria também aborta a transação inteira. O teste injeta uma resposta perdida sintética após um commit real; a reconciliação interna recupera o recibo sem nova mutação.

**NÃO EXERCITADO:** cancelamento durante envio/ACK do commit, interrupção de rede real, encerramento de servidor MongoDB, `UnknownTransactionCommitResult` emitido pelo driver e reconciliação simultaneamente indisponível. O teste de resposta perdida não equivale a esses cenários. Não se deduz rollback de um `CancelledError`; se o commit puder ter ocorrido, o cliente deve manter a mesma identidade e reconciliar, e se o estado continuar incerto deve receber resultado indeterminado sem repetir a intenção cegamente.

## Evidências e resultados C11

Código e testes diretamente ligados ao adendo: [gate e capability](../../backend/curriculum_contract/experimental_editorial_authorization.py#L148), [HMAC e builder mínimo](../../backend/curriculum_contract/experimental_editorial_privacy.py#L49), [ACL e consulta de recibo](../../backend/curriculum_contract/experimental_editorial_replay_policy.py#L67), [harness persistente e resolução da trilha](../../backend/integration_tests/editorial_authorization_harness.py#L167), [testes persistentes C11](../../backend/integration_tests/test_editorial_authorization.py#L89) e [testes unitários da política](../../backend/unit_tests/test_experimental_editorial_privacy_policy.py#L44). O verificador confere a URI contra loopback, porta e replica set C11 antes de conectar e exige MongoDB 7, primary, WiredTiger e sessões lógicas.

Ambiente local descartável: MongoDB `7.0.43`, imagem oficial `mongo:7.0.43`, replica set de nó único `rsC11`, WiredTiger, sessão lógica habilitada; PyMongo `4.18.2`, Python `3.11.9`, Pytest `9.1.1`. Container e rede foram exclusivos desta fase, sem volume, bind mount ou porta pública; conexão publicada somente em `127.0.0.1:29131`. Cada caso criou DB `editorial_revision_test_c10_c11_*` com marcador C11 e removeu apenas seu próprio DB após verificar o marcador.

* Integrações persistentes C11: **9 passed, 0 failed, 0 skipped**, repetidas duas vezes (**18 execuções de teste ao longo das duas rodadas**), mais uma execução direcionada aprovada do teste de URI. Cada execução usa clientes async próprios nos cenários de corrida/revogação; o MongoDB continua sendo um replica set local de um nó.
* Testes unitários de privacidade/política: **13 passed**.
* Regressões offline combinadas C1/C5/C6/C2/C10/C11 e PoC de gerações: **136 passed e 38 subtests passed**.
* Ruff: aprovado nos seis módulos/testes novos C11.
* Mypy: aprovado em quatro módulos de produção experimental/harness, com resolução de pacote a partir de `backend`.
* Compilação sintática e `git diff --check`: sem erros.

Durante a primeira execução do teste negativo de URI, PyMongo tentou uma resolução DNS SRV para o domínio reservado `example.invalid` antes de o harness rejeitar `mongodb+srv`; a resolução retornou `NXDOMAIN`. Não houve conexão com MongoDB, API, IAM ou serviço operacional. O harness foi corrigido para rejeitar o esquema antes de chamar o parser, e a regressão passou sem consulta DNS. Essa ocorrência incidental é registrada como desvio da intenção offline, não como acesso a dados/serviços Trilha Code.

Não executadas: testes persistentes C10/C8/C7 com seus próprios endpoints/configurações de fase. O C11 usou sua instância/banco exclusivo e exerceu o adaptador async C10 contra MongoDB 7. Não foram reutilizados bancos de fases anteriores.

## Limitações, gates e próximas decisões

O experimento não prova JWT/sessão/IAM real, política operacional por trilha, grants ou ACL implantados, minimização para qualquer chamador C8, rotação de segredo real, retenção, revogação em store externo, cancelamento durante commit, label real de commit desconhecido, failover multinó, cobertura de writers legados ou baseline de produção. A concorrência da revogação só foi coordenada porque o grant sintético foi gravado no mesmo MongoDB/transação; se essa topologia não puder ser adotada, outra autoridade de autorização versionada precisa ser deliberada.

Gates preservados sem promoção: G1 `PARTIAL`; G2 `NOT_VERIFIED`; G3 `NOT_VERIFIED`; G4 `PARTIAL`; G5 `NOT_VERIFIED`; G6 `PARTIAL`; G7 `PARTIAL`; G8 `NOT_VERIFIED`; G9 `BLOCKED`; G10 `BLOCKED`. ADR-008 permanece bloqueado.

Pendências humanas antes de qualquer integração: regra operacional de escopo por trilha e de administradores globais; source of truth/ordenação para revogação; resposta externa e compatibilidade de replay; versão e rollout da API (`If-Match`/`Idempotency-Key`); ACL/retention de auditoria, histórico, fingerprint e recibo; operação e rotação de chaves; comportamento após expiração ou perda de chave. Essas deliberações e gates não autorizam mudanças funcionais.

**Próximo incremento único recomendado:** obter a decisão de produto/IAM sobre a fonte e o escopo de autorização por trilha, incluindo como sua revogação se ordena com o commit. Sem esse contrato, capability C11 não pode ser conectada com segurança ao IAM real.
