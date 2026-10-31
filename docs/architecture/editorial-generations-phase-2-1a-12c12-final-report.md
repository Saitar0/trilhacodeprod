# TRILHA CODE — Fase 2.1A.12C.12 — Relatório final

**Veredito: FONTE DE AUTORIDADE IAM EDITORIAL ANALISADA — MODELO EXPERIMENTAL VALIDADO; INTEGRAÇÃO NÃO AUTORIZADA.** A análise do IAM versionado e os testes em MongoDB 7 descartável demonstraram como revogações de papel, sessão e grant podem ser ordenadas com uma confirmação editorial quando os estados participam da mesma transação. Isso não comprova equivalência com o IAM ou runtime implantado.

## A. Resultado executivo

O backend versionado autentica por JWT, verifica uma sessão persistida, recarrega o usuário e calcula permissões a partir de uma matriz estática por papel. A escrita editorial exige `content.write`, mas não foi encontrado grant de escrita por trilha no caminho inspecionado. A política de leitura `can_view_track` não equivale a autorização de escrita por recurso.

Foi criado um modelo estritamente experimental de principal, sessão e grants por trilha. No MongoDB 7 descartável, a transação C8/C10 foi composta com atualizações condicionais desses três estados, a alteração sintética do bloco, auditoria, revisão e recibo. Revogações concluídas antes da confirmação invalidaram a capability sem estado editorial parcial. Corridas coordenadas demonstraram uma ordem serializada entre o commit que já havia tocado o registro de autorização e a revogação concorrente. Contraexemplos persistentes mostraram que consultas prévias ou projeções de autorização desatualizadas mantêm janela de TOCTOU.

## B. Git e isolamento

| Item | Resultado |
|---|---|
| Commit-base | `a9b9c69eccf50f3d5713e4b55533b39210785635` |
| Branch | `codex/fase2-1a-12c12-editorial-iam-authority` |
| Worktree | `C:\Users\Joao\.codex\worktrees\trilhacode-fase2-1a-12c12-editorial-iam-authority\trilhacodeprod` |
| Commit desta fase | Commit local criado após as verificações; SHA informado na entrega |
| Checkout original | Não modificado |
| Outras worktrees | Não modificadas |
| Diretórios do curso e migração | Não materializados nem modificados |
| Operações remotas | Nenhuma; sem push, PR, merge ou rebase |

A worktree foi criada com `git worktree add --no-checkout`; sparse-checkout foi configurado antes da materialização. O commit final tem como parent o commit-base listado e a worktree foi verificada limpa após o commit.

## C. IAM real

O código versionado apresenta esta cadeia: token em cookie `access_token` ou `Authorization: Bearer`; `decode_token` valida assinatura/expiração/tipo; `current_user` valida a sessão, carrega `users` pelo `sub`, verifica conta e `token_version`, então calcula as permissões para o papel atual. O detalhe de implementação e as referências de linha estão no [documento de decisão C12](editorial-generations-phase-2-1a-12c12-iam-authority-decision.md).

`create_access_token` define expiração de 15 minutos; a sessão de servidor tem TTL de sete dias e é consultada por digest. Logout/revogação marca `revoked_at`. Mudanças de papel atualizam `users.role`; o teste versionado de role refresh confirma que o papel recarregado muda para uma sessão existente. Não foi observada invalidação automática de sessão por alteração de papel. JWT, sessões, permissões e papel foram testados apenas com identidades sintéticas.

## D. Fontes de autoridade

O estado atual versionado separa `users` e `auth_sessions`; a política global de permissões estática reside em `constants.PERMISSIONS`. O código de escrita observado não contém autoridade de grants por trilha. Nenhum comportamento do ambiente implantado foi verificado.

Foram comparadas três opções:

1. **Grant no mesmo MongoDB transacional:** pode ordenar grant/epoch, sessão, estado do usuário/política, revisão, fence, bloco, auditoria e recibo se os registros relevantes participarem da unidade transacional e da topologia real permitir transações. É a única alternativa diretamente demonstrada neste escopo, com documentos sintéticos. Exige decisão de autoridade/ownership, schemas, índices, roles e compatibilidade; duplicar autoridade sem regra de precedência criaria grants contraditórios.
2. **IAM externo consultado antes do commit:** mantém a autoridade existente, mas deixa uma janela entre a resposta positiva e a confirmação. Uma segunda consulta ainda termina antes do commit e não fecha atomicamente essa janela. Falha ou indisponibilidade deve negar/indeterminar, nunca conceder.
3. **Época/projeção coordenada:** versão de autorização, fencing de autorização ou projeção podem ajudar apenas se a atualização/revogação e a confirmação editorial compartilham um mecanismo de ordenação. Projeção eventualmente consistente ou cache stale não fornece revogação imediata; epoch não coordenado também não remove a corrida. Uma autoridade distribuída/coordenador seria trabalho separado e não foi implementado.

Nenhuma fonte oficial futura foi escolhida. O documento de decisão lista opções, ameaças, consequências e dependências para aprovação humana.

## E. Modelo de ameaças

A matriz C12 analisa 16 ameaças com pré-condições, impacto qualitativo, mitigação e evidência: `content.write` sem grant; capability reutilizada; JWT com sessão revogada; alteração de papel; revogação de grant; `track_id` divergente; capability forjada; fence confundido com IAM; replay entre atores; replay após remoção; escritor legado; falta de auditoria; commit ambíguo; vazamento de histórico/recibo; cache/projeção stale; e confusão entre identidade, permissão, grant e fencing.

Riscos qualitativos `HIGH` foram atribuídos quando há caminho plausível para escrita fora de escopo, perda de ordenação, vazamento ou confirmação ambígua, com critérios descritos no documento de decisão; não foi usado score numérico arbitrário.

## F. Alternativas arquiteturais

A alternativa A, grants na mesma fronteira transacional, foi exercitada. A alternativa B, IAM externo, foi refutada como garantia forte por contraexemplo determinístico: uma revogação ocorrida depois da última consulta, inclusive com revalidação, mas antes da confirmação, não impede o commit. A alternativa C foi analisada; epochs e projeções são úteis apenas sob coordenação comprovada, não como substitutos de atomicidade. Não se fez afirmação de performance ou prontidão de produção.

## G. Grants por trilha

O schema experimental fechado registra ator, trilha ou wildcard explicitamente autorizado para admin global, operações permitidas, estado, epoch, concedente/revogador e timestamps UTC. Identidade é derivada de ator + trilha; valores desconhecidos e formatos inválidos são rejeitados. As coleções `c12_track_grants`, `c12_iam_principals` e `c12_iam_sessions` existem somente no banco C12 descartável, não são schemas operacionais.

## H. Revogação

Política testada: revogação efetivada antes da confirmação invalida a capability; confirmação anterior permanece como fato histórico, e a revogação subsequente não desfaz auditoria, revisão ou recibo. Grant, papel/permissão e sessão possuem epochs/estado separados. A transação toca condicionalmente cada registro e só então executa o participante editorial C8/C10; conflito/revogação aborta sem mudança de bloco, revisão, auditoria ou recibo.

Com revogação mantida em outro serviço/armazenamento, não se pode afirmar que “revogação antes do commit sempre vence” sem mecanismo de coordenação que ordene ambos os lados. A mesma transação garante apenas os estados nela incluídos e sob a semântica/topologia testadas.

## I. JWT e sessão

Testes unitários chamaram `security.decode_token`, `security.current_user` e `services.sessions.require_active_session` carregados do código versionado com `settings`, banco e usuários sintéticos. Cobriram token válido/expirado/malformado, sessão revogada, conta desativada, versão revogada e recarga de papel. São testes locais com doubles; não são teste de endpoint, JWT ou sessão implantada.

## J. Capabilities

A capability experimental é assinada pelo servidor de teste e vinculada a ator, digest da sessão, papel, trilha resolvida, operação, escopo do grant e epochs de principal, sessão e grant. A assinatura e o selo emissor são verificados antes de compor o participante transacional. A capacidade não inclui fence: fencing continua no protocolo editorial como controle de escritor obsoleto, não como permissão. O teste rejeita capacidade forjada e escopo global não provisionado explicitamente. Objetos Python, chave sintética e verificador C12 não constituem segurança operacional.

## K. Transações

O harness reutiliza o adaptador assíncrono experimental C10 e sua autoridade editorial única por trilha. As transações usam leitura `snapshot` e `writeConcern: {w: "majority", j: true}`; o harness valida replica set, primary, sessões lógicas e WiredTiger. Os updates condicionais dos registros de autorização são participantes na sessão transacional da revisão, auditoria e recibo.

O replica set era de nó único: `majority` nessa topologia não demonstra resiliência multinó, failover nem operação implantada. O teste também não prova grants Mongo ou índices existentes no ambiente real.

## L. Concorrência

Foram exercitados CAS de duas operações concorrentes, rejeição de fence obsoleto, revogações pré-commit e corridas coordenadas com comandos reais concorrentes por clientes independentes. Nas corridas, um listener Mongo observou o início do update da revogação; o teste liberou o commit já suspenso dentro da transação e verificou a serialização no mesmo registro. Isso demonstra o interleaving observado, não uma prova formal de linearizabilidade para todas as agendas possíveis.

Contraexemplos determinísticos com uma e duas verificações a IAM externo confirmaram que uma revogação pode ocorrer após a última leitura e antes de `commit`. O teste de projeção stale também confirmou que uma permissão desatualizada pode permitir a operação. Essas arquiteturas não satisfazem a regra forte sem ordenação adicional.

## M. Escritores legados

O inventário C4 identifica famílias W-01–W-12, além de W-13 (PoC); a execução no runtime continua não confirmada. CRUD/reordenação, duplicação/exclusão, publicação/snapshot, taxonomias, importação/restauração e scripts podem gravar sem a autoridade comum, conforme evidência estática C4. C12 não reexecutou writers nem demonstra cobertura total. Antes de integração, cada writer capaz de alterar as coleções abrangidas deve ser convertido, desabilitado no escopo ou comprovadamente removido do runtime; dual-write com bypass não é uma estratégia segura.

## N. Integração incremental

O [plano de prontidão C12](editorial-generations-phase-2-1a-12c12-integration-readiness.md) separa decisões sobre autoridade/grants/admin e revogação; evidência operacional ADR-008 e compatibilidade de topology/roles; adaptador IAM; capability na fronteira HTTP; composição transacional C8/C10; cobertura de writers; testes/observabilidade; publicação e leitores; rollback/cutover. Cada etapa exige autorização futura específica. Pré-requisitos obrigatórios incluem uma fonte sem concessões contraditórias, ordenação de papel/sessão/grant, runtime/topologia comprovados e cobertura ou bloqueio de todo writer capaz de bypass no escopo.

## O. Rollback

Uma confirmação editorial não deve ser desfeita removendo auditoria ou recibo; correções futuras seriam novas revisões. Revogação não deve ser reaberta como compensação de rollback. Resultado indeterminado exige reconciliação por identidade estável, sem repetição cega. Uma flag não impede outros writers de contornar o protocolo. A estratégia de cutover e recuperação depende do baseline ADR-008, dos writers confirmados no runtime e de ensaio futuro.

## P. Testes

Ambiente descartável identificado antes de escrever: imagem oficial `mongo:7.0.43`, digest `sha256:1f995ad6fdb93244a1addab1b58f934a0bc2f5643c38e02f5e9d7f0c7d227a7b`, replica set `rsC12`, primary, WiredTiger, loopback `127.0.0.1:29132`, sessões lógicas habilitadas (timeout reportado de 30 minutos), AsyncMongoClient/PyMongo `4.18.2`, venv Python 3.11 dedicado. A configuração padrão reportou `readConcern: local` e `writeConcern: majority`; as transações do adaptador explicitam `readConcern: snapshot` e `writeConcern: {w: "majority", j: true}`. Cada execução criou banco com prefixo `editorial_revision_test_c10_c11_c12_`, marcador C12 e dados sintéticos; URI foi definida explicitamente no comando de teste.

| Verificação | Resultado |
|---|---|
| Integração persistente C12, primeira execução | 18 aprovados, 0 falhas, 0 skips; 4,23 s de pytest |
| Integração persistente C12, segunda execução | 18 aprovados, 0 falhas, 0 skips; 4,19 s de pytest |
| Regressões offline combinadas | 114 aprovados + 26 subtests aprovados; 0 falhas/skips; 1,03 s |
| Ruff nos cinco arquivos Python criados | Aprovado |
| Mypy nos três módulos experimentais/de harness | Aprovado; sem erros |
| Compilação sintática | Aprovada (`compileall`) |
| `git diff --check` | A verificar após stage |

Uma tentativa preliminar falhou porque o teste de expiração referenciava `datetime` sem importá-lo. O erro estava na própria fixture, não no código do adaptador. O import foi corrigido e as duas execuções persistentes completas passaram. Não houve skips nas suítes C12 finais.

## Q. Regressões

As regressões offline cobriram testes C12 unitários, protocolo em memória C1, adaptador offline C2, contrato API C10, privacidade C10, observabilidade C5 e PoC de gerações. A suíte persistente própria C12 também reutilizou o adaptador Async C10 em seu MongoDB exclusivo. Suítes persistentes próprias de C11/C10/C8/C7 não foram executadas nem reutilizadas, para manter o isolamento de recursos por fase.

## R. Segurança

Não foram usados dados reais, credenciais operacionais ou configurações `.env`. Nenhuma conexão foi feita a banco externo, staging, produção, Coolify ou GHCR. O container C12 foi identificado por nome e labels de fase/owner antes da conexão; URI sem credenciais restringida ao loopback e replica set esperado. O harness criou clientes somente para esse URI e bancos sintéticos com marcador. Módulos C12 não são importados por rotas, serviços ou startup ativos. Nenhum arquivo operacional foi alterado.

## S. Gates

Estados históricos preservados, sem promoção: G1 `PARTIAL`; G2 `NOT_VERIFIED`; G3 `NOT_VERIFIED`; G4 `PARTIAL`; G5 `NOT_VERIFIED`; G6 `PARTIAL`; G7 `PARTIAL`; G8 `NOT_VERIFIED`; G9 `BLOCKED`; G10 `BLOCKED`. ADR-008 permanece bloqueado. C12 produz evidência experimental para a ordenação de autorização no escopo sintético, não cobertura dos writers ou readiness operacional.

## T. Limpeza

Ao final dos testes, o harness removeu cada banco somente após validar o marcador C12; a lista não mostrou bancos com prefixo C12. O container `trilhacode-c12-iam-mongo` foi confirmado pelas labels `trilhacode.phase=2.1a.12c12` e `trilhacode.owner=codex`, e removido. Também foram removidos a rede dedicada `trilhacode-c12-iam-network` e o volume anônimo exato criado pela imagem oficial em `/data/configdb` (`96ba18e25d86ea18d29c9f62cf01021cc06bf28cc549746b79f3dd23fe4a5b54`), após confirmar que apenas o container C12 o utilizava. `/data/db` era tmpfs; nenhum volume de dados operacional foi montado. A ausência dos três recursos foi verificada após a remoção.

## U. Arquivos

1. `backend/curriculum_contract/experimental_editorial_grants.py`
2. `backend/curriculum_contract/experimental_editorial_iam_authority.py`
3. `backend/integration_tests/editorial_iam_authority_harness.py`
4. `backend/integration_tests/test_editorial_iam_authority.py`
5. `backend/unit_tests/test_editorial_iam_authority.py`
6. `docs/architecture/editorial-generations-phase-2-1a-12c12-iam-authority-decision.md`
7. `docs/architecture/editorial-generations-phase-2-1a-12c12-integration-readiness.md`
8. `docs/architecture/editorial-generations-phase-2-1a-12c12-final-report.md`

Todos são novos e estão no escopo experimental/documental permitido.

## V. Limitações

JWT/sessão/grants são sintéticos no C12 persistente; os testes reais de código IAM usam doubles. A atualização de papel no código versionado atualiza o documento de usuário sem incrementar `token_version`, mas o papel é recarregado em cada request. Não foi estabelecido se grants ou papel devem ser fonte autoritativa em outro serviço, nem como versionar a política estática global. Falham como evidência operacional: topologia implantada, grants e roles Mongo, cache IAM, failover multinó, writers externos/legados no runtime, ACL e retenção. Não há prova formal de linearizabilidade, nem teste de falha de rede/commit desconhecido real.

## W. Próximo incremento

Deliberar com os responsáveis pelo IAM e pelo produto a **fonte oficial do grant por trilha e o ponto de linearização de sua revogação com papel/sessão**, incluindo quem pode conceder escopo global administrativo. Essa decisão desbloqueia a escolha de armazenamento e os critérios de integração; não iniciar implementação operacional antes dela.

## X. Veredito

**FONTE DE AUTORIDADE IAM EDITORIAL ANALISADA — MODELO EXPERIMENTAL VALIDADO; INTEGRAÇÃO NÃO AUTORIZADA.** As provas são locais e sintéticas. Não há autorização de integração ao runtime nem de alteração dos estados dos gates.
