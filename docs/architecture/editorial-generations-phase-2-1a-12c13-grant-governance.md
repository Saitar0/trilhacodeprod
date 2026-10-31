# Fase 2.1A.12C.13 — Proposta de governança de grants editoriais

**Estado:** proposta experimental, não implantada nem aprovada para uso operacional.
**Base de análise:** commit `ff9cf18d0751d06d3362716372b4ea88d143a0b6`.
**Runtime implantado:** não verificado.

## Como ler esta proposta

As afirmações abaixo distinguem: **código versionado** (o que os arquivos implementam), **evidência experimental** (o que testes isolados anteriores exercitaram), **proposta** (modelo recomendado para deliberação) e **pendência** (decisão que não deve ser presumida). A política C13 não cria papéis, grants ou endpoints no backend.

## IAM versionado observado

O backend declara três papéis e uma matriz estática em [`constants.py`](../../backend/constants.py#L5-L16). `admin` possui `content.read`, `content.write`, `content.publish`, `content.delete`, `taxonomy.manage`, `users.manage`, `progress.write` e `submissions.grade`; `editor` possui todas as permissões de conteúdo, inclusive exclusão e publicação, e também `progress.write` e `submissions.grade`; `student` possui `progress.write`. A igualdade desta matriz foi verificada pelo contrato offline C13; isso não confirma as atribuições existentes no banco ou no ambiente implantado.

[`security.py`](../../backend/security.py#L33-L68) emite tokens de acesso de 15 minutos com `sub`, `email`, `ver`, `sid`, `type` e expiração; [`current_user`](../../backend/security.py#L75-L110) valida token, sessão, usuário ativo, `token_version` e e-mail verificado, depois calcula as permissões a partir do papel atual. Sessões são persistidas com expiração e revogação em [`services/sessions.py`](../../backend/services/sessions.py#L13-L83). A alteração de papel passa por `users.manage` e atualiza `users.role`, seguida de auditoria em [`routes_auth.py`](../../backend/routes_auth.py#L281-L283) e [`services/auth.py`](../../backend/services/auth.py#L221-L228).

`has_permission` só verifica a permissão global do papel; `can_view_track` é regra de leitura pública/visibilidade e não concede escrita por trilha ([`permissions.py`](../../backend/permissions.py#L9-L31)). Não foi encontrado contrato operacional de grant editorial por trilha. O código encontrado não prova cache de permissão na aplicação ativa, nem sincronização com provedores externos. O estado efetivo do runtime continua fora desta análise.

### Controles atuais versus proposta

| Papel versionado | Permissões globais atuais | Grant por trilha atual | Delegar/revogar grants editoriais | Tratamento proposto |
|---|---|---|---|---|
| `admin` | Conteúdo completo, `taxonomy.manage`, `users.manage`, progresso e notas | Não encontrado | Não existe permissão de grant identificada | Não implica escopo editorial universal. Exige escopo global explicitamente provisionado ou grant individual, além da permissão global aplicável. |
| `editor` | Leitura, escrita, publicação e exclusão de conteúdo; progresso e avaliação | Não encontrado | Não existe permissão de grant identificada | Permissão global é necessária, mas insuficiente; exigir grant da trilha e operação específica. |
| `student` | `progress.write` | Não encontrado | Não | Não pode receber capability editorial por inferência de papel ou de fence. |

As permissões não demonstram papéis mais estreitos para revisão, publicação, importação ou administração de taxonomias. Não se devem criar essas permissões por analogia nesta fase.

## Política proposta de concessão e responsabilidade

1. Uma edição exige identidade autenticada, sessão vigente, conta ativa, permissão global do papel e autorização explícita para a trilha e operação. O recurso e sua trilha são resolvidos pelo servidor; `track_id` enviado pelo cliente não escolhe a autoridade.
2. Uma autoridade de governança designada concede o primeiro grant de responsável editorial para cada trilha. O criador técnico da trilha não se torna proprietário permanente por causa de `created_by`.
3. Um responsável editorial pode delegar apenas operações e trilhas incluídas em sua própria delegação. Não pode autoconceder privilégios, ampliar seu próprio escopo, conceder globalidade ou delegar autoridade de governança.
4. Revogação pode ser exercida por autoridade de governança. Um perfil de emergência, se aprovado, deve ser revogador *deny-only*: não cria grants, não altera papel e não contorna a auditoria.
5. Alteração de operações, transferência de responsabilidade e nova concessão após revogação incrementam um epoch monotônico e deixam eventos de auditoria próprios. Revogar o delegante invalida as delegações derivadas; a semântica deve ser testada antes de implementação.
6. Expiração automática, prazo de grant, retenção, break-glass, dupla aprovação e processo de recuperação são decisões humanas pendentes. Nenhum valor padrão é proposto como política final.

Os nomes “responsável editorial”, “editor delegado”, “autoridade IAM”, “auditor” e “revogador de emergência” descrevem funções conceituais, não papéis existentes no backend.

### Matriz proposta de papel, operação e governança

| Operação | Permissão global observada na entrada atual | Grant futuro sugerido | Escopo necessário | Pode delegar/revogar? | Auditoria exigida no desenho |
|---|---|---|---|---|---|
| Criar/editar/reordenar blocos, nós ou trilha | `content.write` | `block.edit` / `structure.edit` / `track.edit` | Trilha resolvida pelo recurso | Não, salvo delegação explícita do responsável editorial | Alteração confirmada e ator |
| Remover bloco | `content.write` na rota atual | `block.delete` | Trilha do bloco | Não | Exclusão, motivo controlado e identidade |
| Remover nó/trilha | `content.delete` | `structure.delete` / `track.delete` | Trilha; cascata e estado do aluno sujeitos a política | Não | Auditoria durável e decisão de preservação do aluno |
| Duplicar nó/trilha | `content.write` | `structure.duplicate` / `track.duplicate` | Grant de leitura da origem e criação no destino | Não | Uma intenção, origem/destino e recibo idempotente |
| Publicar/despublicar | `content.publish` na rota de publicação; despublicação direta não foi confirmada | `track.publish` / operação específica a decidir | Trilha e generation/head | Não; pode exigir segunda aprovação como decisão pendente | Auditoria de publicação e head confirmado |
| Restaurar versão | `content.publish` | `track.restore` | Trilha e revisão-base | Não | Auditoria de restauração e origem da versão |
| Importar | `content.write` | `track.import` | Trilha de destino e escopo global de catálogo quando toca tags | Não | Resumo mínimo, operação idempotente e recuperação |
| Alterar taxonomia/tipo de bloco | `taxonomy.manage` | Autoridade de catálogo separada | Catálogo global, não uma trilha arbitrária | Somente autoridade de catálogo designada | Mudança global e impacto de compatibilidade |
| Criar/remover tag | `content.write` atualmente | Autoridade de catálogo; permissão atual parece ampla | Catálogo global; remoção modifica vários documentos | Não | Impacto transversal em nodes/tracks |
| Gerenciar grants e escopo global | Nenhuma permissão específica encontrada; `users.manage` só altera papel | `grant.manage` / `admin_scope.manage` como propostas | Trilha explícita ou escopo global provisionado | Autoridade de governança; sem autoconcessão | Toda concessão, alteração, transferência, revogação e negação relevante |
| Consultar histórico/auditoria | Rotas de versões usam `content.read`; ACL separada não comprovada | Permissão de leitura de histórico a decidir | Trilha e classe do registro | Não | Acesso protegido pode exigir trilha de auditoria própria |

Essa tabela relaciona operações futuras às permissões das rotas existentes; não cria permissões nem confirma comportamento de implantação. A matriz fechada com os mapeamentos observados está em [`editorial_grant_governance_c13.json`](../../backend/curriculum_contract/editorial_grant_governance_c13.json).

## Administradores, ownership e recuperação

**Recomendação:** escopo administrativo global explicitamente provisionado (alternativa B), com grants individuais por trilha como alternativa C para o trabalho cotidiano. Escopo global implícito pelo nome do papel (`admin`) é rejeitado. Essa combinação é mais auditável e reduz impacto de um papel amplo. O código atual tem `admin` e `users.manage`, mas não tem grant global ou trilha de concessão/revogação editorial; portanto, esta é somente uma proposta.

O provisionamento global deve exigir autorização humana explícita, ator distinto do alvo (sem autoconcessão), justificativa controlada, auditoria durável, epoch e procedimento de revogação testado. Se dupla aprovação ou break-glass forem adotados, o aprovador não deve depender da mesma capability do executor. Recuperação deve ser feita por autoridade independente predefinida e auditada; não se deve desbloquear com atualização manual que ignore o epoch.

“Ownership” de uma trilha é responsabilidade de negócio, não inferência do `created_by`. Transferência deve revogar delegações antigas e emitir grants novos sob revisão de autoridade, conservando auditoria. Serviços automatizados usam identidade própria e grant de operações limitadas; não reutilizam sessão humana.

## Fonte de autoridade e ordenação de revogação

O código versionado usa o mesmo módulo `database.db` para usuários/sessões e entidades editoriais ([`database.py`](../../backend/database.py#L1-L8), [`security.py`](../../backend/security.py#L75-L104)). Isso não prova que o runtime utiliza uma topology/URI apta a transações entre esses estados. A C12 testou documentos sintéticos no mesmo replica set descartável; não verificou os schemas ou grants operacionais.

**Direção recomendada para estudo futuro:** uma autoridade primária para grants por ator/escopo, com epoch monotônico; não manter dois serviços capazes de conceder contraditoriamente o mesmo acesso. A fonte de autenticação global e papel permanece a fonte atualmente definida pelo projeto até decisão de migração. Para prometer a regra “revogação confirmada antes do commit impede a edição”, grant, estado ativo/papel ou epoch de política, estado/epoch da sessão e escopo administrativo revogável precisam ser lidos e condicionalmente participar da fronteira transacional do commit. Uma projeção eventual ou segunda consulta remota reduz janela, mas não a elimina.

O schema de grants deve permanecer sem nome operacional nesta fase. Campos conceituais mínimos: `actor_id`, escopo (`track_id` ou escopo global explicitamente tipado), conjunto fechado de operações, estado, epoch, concessor/revogador e timestamps de auditoria. Deve existir unicidade para identidade+escopo e índices de leitura; chaves e índices definitivos dependem de consulta, volume, roles do banco e avaliação operacional.

Regra de ordenação experimental preservada da C11/C12:

* Revogação confirmada antes do commit editorial: negar a edição.
* Edição confirmada antes da revogação: preservar operação, revisão e auditoria históricas; revogação não apaga a edição.
* Corrida: ordenar usando a mesma autoridade transacional (escrita condicional/epoch) e retries de conflito; nunca depender apenas de token previamente emitido.
* Papel/global permission: a matriz atual é Python estático. Para ordenar mudança de política com operações in-flight, a futura integração precisa de epoch/versionamento ou de um protocolo de release que drene operações antigas. Esse ponto não foi validado para runtime.
* JWT: autenticidade e expiração do token não substituem sessão atual, conta ativa, papel atual, grant e fencing de writer.

### Alternativas de fonte de grant

| Alternativa | O que pode garantir | Limite / condição |
|---|---|---|
| Grant autoritativo no mesmo MongoDB/limite transacional editorial | Com escrita condicional no mesmo registro de grant (e participação de usuário/sessão quando necessário), a transação pode ordenar grant revogado e commit. C11/C12 exercitaram esse mecanismo com registros e clientes sintéticos. | Não está provado que topologia, schemas, database roles ou deployment reais permitem a transação. É preciso evitar duplicar a autoridade de concessão em IAM e Mongo editorial. |
| IAM externo consultado antes da edição | Mantém fonte no IAM atual e pode negar se indisponível. | Não ordena revogação e commit: a revogação pode confirmar após o check e antes da transação editorial. Uma segunda consulta apenas desloca a janela; cache torna a decisão potencialmente stale. |
| Epoch/projeção ou coordenador versionado | Projeção pode reduzir leitura remota; epoch pode detectar mudança se sua versão for atual e tiver participação condicional no commit. Um coordenador linearizável pode emitir ordem explícita. | Projeção assíncrona não garante revogação imediata. Um coordenador introduz nova autoridade/disponibilidade/recovery e precisa de sua própria prova de linearização. Não foi implementado em C13. |

**Recomendação sob condição:** escolher uma única autoridade primária de grants, e então fazer a confirmação editorial depender da versão atual dessa autoridade no mesmo limite transacional ou em mecanismo coordenado com prova de ordem equivalente. Se nenhum mecanismo puder oferecer isso no baseline operacional, a garantia “revogação antes do commit bloqueia a edição” deve ser reduzida explicitamente ou o cutover fica bloqueado; não prometer a garantia com um check externo.

## Ameaças à fronteira editorial

| Ameaça | Impacto | Pré-condição | Mitigação proposta | Evidência e estado |
|---|---|---|---|---|
| `content.write` global aplicado a trilha sem grant | Alto | Papel editor/admin com permissão global, recurso conhecido | Resolver trilha server-side e exigir grant exato | `permissions.py` tem permissão global; grant por trilha não encontrado |
| Capability reutilizada depois de revogação | Alto | Capability antiga ainda aceita no commit | Epoch e participação condicional na transação; invalidar/revalidar capability | Ordering sintético C11/C12; runtime não provado |
| JWT válido com sessão invalidada | Alto | Request ou operação iniciou antes da invalidação | Checar sessão atual e ordenar sua versão com commit quando essa garantia for exigida | Código `current_user` verifica sessão por request; corrida com commit não é coordenada no fluxo ativo |
| Papel muda durante operação | Alto | Principal é carregado antes de mudança | Versionar política/role e participar do epoch no commit ou drenar writers por protocolo de release | Role é armazenado em `users`; matriz estática; ordenação operacional ausente |
| Grant revogado durante edição | Alto | Check remoto/preparação precede revogação | Transação toca condicionalmente autoridade de grant | Demonstrado só com grant C11/C12 sintético no mesmo Mongo |
| Cliente troca `track_id` | Alto | Servidor confia no escopo do request | Resolver bloco/nó para trilha e comparar; negar divergência | Política C11/C12 sintética; rota atual não implementa grant por trilha |
| Capability ou admin global forjado | Alto | Cliente escolhe credencial/scope; papel admin vira wildcard | Capability server-issued; escopo global explícito e auditado; sem autoconcessão | Sem endpoint/capability ativa encontrado |
| Fence usado como autorização | Alto | Token de escritor tratado como identidade/permissão | Manter IAM, grant, capability e fence como contratos distintos | Contrato C8/C11 separa; integração ausente |
| Replay de chave de outro ator | Alto | Chave vira credencial ou recibo não tem escopo ator/operação | Escopar recibo por ator, trilha, operação e intenção; exigir autorização externa atual | C11 sintético cobre política; não aplicado a HTTP ativo |
| Replay após bloco removido vaza conteúdo | Alto | Recibo reconstrói estado privado após remoção/revogação | Recibo mínimo; replay não recria bloco; consulta externa autorizada no momento atual | C10/C11 prova sintética; ACL operacional pendente |
| Escritor legado contorna CAS/fence/audit | Crítico para consistência de cutover | CLI/import/restore/route segue gravando mesma coleção | Bloquear/migrar todos writers por coleção antes de cutover | W-01..W-16 da matriz; runtime e tools externas não verificados |
| Auditoria ausente após confirmação | Alto | Mutation e `edit_history` falham/confirmam separadas | Auditoria obrigatória dentro do mesmo commit | C7 demonstrou writer parcial; C8–C12 só experimental |
| Commit com resultado indeterminado | Alto | Resposta/commit não observado | Reconciliar por identidade estável; não repetir sem recibo | C11 simulou resposta perdida; erro real do driver/network não comprovado |
| Histórico/recibo expõe dado privado | Alto | Payload/summary acessível além do escopo | Minimização, ACLs separadas e retenção deliberada | C11 sintético minimiza; ACL atual/real não verificada |
| Cache/projeção de autorização stale | Alto | Commit lê grant antigo após revogação | Não usar projeção eventual como autoridade de commit; epoch coordenado | Contraexemplo em evidência C12, com projeção sintética |
| Confusão identidade × permissão × grant × fence | Alto | Um controle é aceito no lugar de outro | Contratos tipados, fail-closed e testes negativos separados | Código e protótipo demonstram distinção conceitual; API não integrada |

Os níveis são qualitativos e descrevem impacto/precondição, não probabilidade numérica. Falta de prova operacional é indicada como pendência, não pontuada como risco baixo.

### Capability e fencing

Capability experimental só pode ser construída em uma fronteira confiável após validar principal, sessão, papel/permissão, trilha resolvida, operação e epochs relevantes. Não aceitar capability do request. A capability não concede escopo sozinha, não é recibo, não deve conter payload e deve ser invalidada/revalidada no commit. O fencing token é autoridade temporal do escritor C8; não atesta identidade nem permissão. A chave idempotente identifica intenção e também não é credencial.

## Auditoria de governança

Auditoria de governança registra quem concedeu, delegou, alterou ou revogou acesso; auditoria editorial registra o que mudou. São finalidades diferentes, potencialmente com ACL/retention distintas. O helper atual [`audit.py`](../../backend/audit.py#L7-L11) grava ator, nome, entidade, ação, resumo e timestamp em `edit_history`; vários writers o chamam depois da mutação. Ele não prova trilha imutável de concessão de grants nem uma ACL separada.

Contrato proposto para eventos de governança: tipo fechado, ator e alvo lógico, escopo de catálogo/trilha, operações antes/depois, epochs antes/depois, decisão, timestamp UTC e código de motivo. Proibidos: JWT, segredos de sessão/capability, fence, payload curricular/aluno e mensagem bruta de exceção. Mudança de grant deve falhar se sua auditoria obrigatória não puder persistir. Entrega de eventos de negação e política de disponibilidade continuam pendentes; observabilidade passiva não é auditoria.

## Decisões ainda necessárias

1. Qual pessoa/órgão do projeto é a autoridade que concede o primeiro grant por trilha e nomeia responsáveis?
2. Qual regra, se houver, permite escopo administrativo global, quem o aprova e quem recupera acesso?
3. Como a matriz global de permissões será versionada para mudanças concorrentes?
4. A fonte de grant poderá participar da mesma transação do conteúdo no runtime comprovado pelo ADR-008?
5. Quais operações de catálogo são globais e qual é seu impacto sobre gerações existentes?
6. Qual política de dupla aprovação, expiração, delegação, revogação e break-glass será aprovada?
7. ACL e prazos de auditoria, recibos e histórico; conteúdo privado; consultas por administradores/auditores.
8. Compatibilidade HTTP, erro de autorização por recurso e política de replay após revogação.

## Evidência e limite

Os testes C11/C12 anteriores usaram principal, sessão, grant, capability, tokens e dados sintéticos em replica set MongoDB 7 descartável e mostraram ordering quando os registros sintéticos participam da mesma transação. Contraexemplos mostraram que checagem externa ou projeção desatualizada podem permitir commit após revogação. C13 valida offline a consistência desta proposta com a matriz atual de permissões; não reexecuta testes persistentes e não valida concessões reais. Nenhum gate histórico é promovido.

Referências: [decisão C12](editorial-generations-phase-2-1a-12c12-iam-authority-decision.md), [prontidão C12](editorial-generations-phase-2-1a-12c12-integration-readiness.md), [política C11](editorial-generations-phase-2-1a-12c11-authorization-replay-policy.md).
