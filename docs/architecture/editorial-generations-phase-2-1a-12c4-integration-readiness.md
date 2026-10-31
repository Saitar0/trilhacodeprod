# Fase 2.1A.12C.4 — Prontidão e plano de integração

**Base:** `afe84afc964bbb0fec3c4466b1b27a451ff2b65a`
**Natureza:** plano; nenhuma integração autorizada ou executada.

## Conclusão executiva

O adaptador da Fase 12C.3 oferece uma referência persistente isolada para revisão, CAS, fencing, recibo e idempotência. Os escritores reais examinados ainda alteram coleções próprias sem compartilhar essa revisão ou token. Não existe uma adaptação “por chamada” que, sozinha, feche o risco: se escritor legado puder continuar gravando as mesmas coleções, ele contorna o protocolo. A publicação e restauração também abrangem várias coleções e não são resolvidas pelo CAS da revisão isoladamente.

**Prontidão para integração de runtime: bloqueada.** O inventário é do código no commit-base, sem comprovação de completude operacional. O baseline implantado continua parcialmente comprovado e ADR-008 bloqueado. Não modificar os gates históricos por esta análise.

## Compatibilidade concreta com o adaptador isolado

| Necessidade observada | Contrato isolado | Lacuna para integração |
|---|---|---|
| Escritas CRUD em várias coleções | A operação preparada contém `track_id`, writer, operation id, revisão esperada, fence e payload canônico no protocolo de domínio | Um comando editorial que represente alteração coerente ainda precisa cobrir conjunto de documentos, relações, quizzes e efeitos correlatos. CRUD atual não envia essa identidade e muta coleções ao vivo diretamente. |
| Importações até 32 MiB | O import aceita payload até 32 MiB em [`routes_import.py`](../../backend/routes_import.py#L5-L30); o adaptador tem limite padrão menor (4 MiB) e máximo configurável documentado no contrato isolado | Exige definir envelope de payload (ou apenas fingerprint/referência a staging), não ampliar limite sem sizing, memória, latência e testes. Não foi medido throughput. |
| Serviços assíncronos | Backend usa cliente Mongo assíncrono em [`database.py`](../../backend/database.py#L1-L8); adaptador isolado é síncrono PyMongo | Chamada direta em rota assíncrona pode bloquear o event loop. Futura integração precisa fronteira async compatível ou isolamento explícito em worker; medição e revisão arquitetural necessárias. |
| Revisão e publicação | `tracks.version` serve no publish; não é a revisão editorial comum. | Separar `editorial_revision`, `published_version` e eventual `generation_id`; não reutilizar campos ou IDs com semântica diferente. |
| Idempotência | Adaptador persiste recibo/fingerprint no seu namespace de teste | `operation_id` do import é local ao import; não há identidade unificada para CRUD, restore, publish e retries HTTP. Definir escopo `(track, command, operation_id)` e autorização antes de mapear. |
| Identidade de escritor | Adaptador aceita capability/identidade sintética própria | Não equivale a usuário autenticado, permissão `content.write/publish/delete`, identidade de serviço nem papel MongoDB. Precisa resolver principal autenticado → autorização para comando/trilha → identidade de processo → fence emitido por autoridade confiável. |
| Persistência e transações | C3 exercitou MongoDB 7.0.43, replica set descartável de nó único e transações | Isso sustenta apenas o ambiente de teste. Topologia/concerns do runtime, índices, roles, concorrência entre processos do app e failover real não foram demonstrados. |
| Leituras e snapshot | Publicação privada de geração permanece inelegível se a origem for inconsistente | Revisão CAS não cria, por si só, snapshot coerente de dados que escritores legados alteram fora do fence. |

Fontes C1–C3 foram consultadas nos relatórios históricos; esta fase não altera o adaptador nem repete seus testes. Ver [relatório de validação persistente 12C.3](editorial-generations-phase-2-1a-12c3-persistent-validation.md), [contrato do adaptador C2](editorial-generations-phase-2-1a-12c2-mongodb-adapter.md) e [protocolo isolado C1](editorial-generations-phase-2-1a-12c1-revision-protocol.md).

## Contrato futuro entre identidade e confirmação

Este é um fluxo proposto, ainda não implementado:

```mermaid
sequenceDiagram
  participant U as Usuário autenticado
  participant A as API/serviço de comando
  participant Z as Autorização editorial
  participant F as Autoridade de fence
  participant R as Repositório de revisão
  U->>A: comando + expected_revision + operation_id
  A->>Z: validar principal, ação e trilha
  Z-->>A: decisão autorizada/negada
  A->>F: obter identidade e fence vigente do processo
  F-->>A: writer_id + fencing_token
  A->>R: preparar e confirmar com CAS + fingerprint
  R-->>A: recibo confirmado ou conflito/fence rejeitado
  A-->>U: resultado explícito; draft preservado em conflito
```

O token não substitui autorização do usuário; a autorização não substitui fencing do processo. O incremento do fence e o commit editorial precisam compartilhar coordenação atômica no armazenamento responsável, conforme contrato C1/C2, e não depender apenas de lease/heartbeat. Um comando de domínio deve declarar sua fronteira: todos os documentos editoriais afetados pela operação lógica entram na revisão, ou o comando é bloqueado até ser modelado.

## Matriz de cobertura e estratégia futura

| Família de escritor | Protegido pelo protocolo hoje? | CAS / fence / idempotência futuros | Estratégia proposta |
|---|---|---|---|
| CRUD interativo de track/node/block/relation | Não observado; bypasses diretos no código | Sim para cada comando editorial lógico; idempotência em escrita/retry | Migrar para uma autoridade de comando única, preservando draft no conflito. Bloquear endpoint legado no cutover, sem caminho alternativo. |
| Reordenação | Não; atualização sequencial por documento | Revisão da coleção/escopo afetado; fence; chave de comando | Tratar ordenação como um único comando e validar conjunto/ordem antes do commit. |
| Duplicação e exclusão | Não; múltiplas coleções e efeitos sobre progresso | CAS/fence; idempotência forte; transação ou preparação recuperável | Modelar como comandos de trilha/subárvore; excluir por fluxo controlado e com política de retenção, não reaproveitar cascata física no cutover. |
| Taxonomia/tag/block type | Não; catálogo global e mutação em massa | Revisão de catálogo independente ou revisão das trilhas afetadas; fence; idempotência | Classificar semântica e escopo. Não forçar todo catálogo global dentro de uma revisão por trilha. Gate ADR-003. |
| Importador | Parcialmente protegido por lease/marker; não por fence comum | CAS em revisão, fence de processo em cada confirmação lógica, operation ID + fingerprint | Importar para staging privado; validar; confirmar comando composto. Não permitir que import escreva ao vivo em coexistência com novo writer sem coordenação única. |
| Restore | Lease/job, sem fence aplicado a cada mutação de snapshot | CAS/fence para origem; idempotência de job/restore; geração nova no modelo final | Tratar restauração como nova revisão e, posteriormente, nova geração. Antes disso serializar/bloquear concorrência incompatível. |
| Publish atual | CAS apenas no `tracks.version` final | revisão de origem coerente; idempotência; depois CAS distinto do head da geração | Desabilitar a publicação legada no cutover; publicação por geração pertence ao ADR-006 e exige ADR-001+005. |
| Seed, migrations, scripts, workers | Cobertura/execução não confirmadas | Fence ou janela operacional de bloqueio explícita; idempotência própria | Inventariar invocadores e restringir acesso de escrita; rotinas incompatíveis devem ser bloqueadas/removidas antes da ativação. |
| Preparador imutável / PoC | Armazenamento privado isolado; não ativa | Necessita prova da revisão de origem e política de acesso | Manter inelegível até a fonte ser consistente; a PoC não é writer integrado. |

## Coexistência e ordem de migração

Recomendação: uma única autoridade de comandos editoriais e transição por cobertura fechada. Não usar dual-write de “coleção legada + protocolo” como estado normal: duas fontes podem divergir após timeout, falha parcial ou corrida e não há reconciliação atômica demonstrada.

1. **Baseline e superfície de execução (bloqueante):** evidência sanitizada da implantação, artefatos, serviços/rotas e linha de release; autorizar separadamente qual branch/release recebe código.
2. **Inventário fechado e autorização (bloqueante):** adicionar caminhos externos/operacionais e mapear actor, escopos e permissões de cada entrada.
3. **Especificação do comando editorial e observabilidade passiva:** medir apenas contagens/identificadores não sensíveis; nenhum payload/conteúdo, bloqueio ou escrita dupla. Coletar cobertura dos escritores sem transformar métrica em fence.
4. **Autoridade persistente e comando piloto atrás de fronteira isolada:** demonstrar CAS/fence/idempotência no armazenamento da linha selecionada; sem expor a alunos e sem publicar. Se piloto compartilhar as coleções legadas, deve haver exclusão mútua demonstrada e rota antiga correspondente desabilitada na janela de teste.
5. **Cobertura por família:** migrar interativos, reordenação, duplicação/exclusão, import, restore, catálogo global e scripts, com regressão e observação por caminho. Nenhum cutover enquanto houver writer capaz de bypass nas mesmas entidades.
6. **Snapshots privados e validação:** derivar de uma revisão estável; qualquer writer legado ou alteração sem incremento invalida elegibilidade.
7. **Publicação/leitores:** somente após ADR-005 e ADR-006, apontar head por CAS único; leitores fixam geração e falham fechado. Não fazer fallback para documentos vivos.
8. **Cutover/rollback:** por ambiente autorizado, gates e baseline comprovados. Rollback deve parar novas mutações/publicações com protocolo incompatível; não reativar leitor legado inseguro como fallback automático.

Não há gate de runtime satisfeito por este inventário. O ADR-008 continua bloqueado pela ausência de identidade comprovada de produção, digest ativo, proveniência completa, rota/tráfego e linha de integração/releases.

## Matriz de riscos por família

| Família | Bypass / consistência | Privacidade / histórico | Publicação | Dependência operacional / teste | Nível |
|---|---|---|---|---|---|
| CRUD estrutural, reorder, duplicação/exclusão | Writes diretos sem revisão comum; operações compostas podem parar no meio | Exclusão pode atingir progresso/histórico | Alteração de conteúdo vivo | Cobertura de endpoints e teste concorrente por comando | HIGH |
| `publish_track` + snapshot | Efeitos preparatórios antes do CAS final; snapshot usa contagem | Definições de quiz em coleção pública de publicação (classificação requer ADR-005) | Potencial mudança pública parcial em coleções legadas | Falhas entre operações, retry e dois publishers | HIGH |
| Import | Lease não aplicado como fence universal; sequência multi-coleção | Tags e metadados compartilhados; snapshots de backup | Marca `_import_state`, mas CRUDs não compartilham protocolo | Processos concorrentes import/CRUD/publish/restore | HIGH |
| Restore | Delete + inserts em batches; owner não compõe cada write | Efeito sobre progresso/notas requer regra e retenção | Substitui dados que leitores atuais consultam | Recuperação após falha e concorrência com import | HIGH |
| Taxonomia global | Sem revisão de catálogo; `delete_tag` atualiza em massa | Pode mudar rótulos/semântica histórica | Reinterpretação pública transversal | Inventário de referências e clientes consumidores | HIGH |
| CLI/startup/migrations/seeds | Escritas potenciais fora de requests | Pode criar/alterar estrutura editorial ou metadados | Execução no startup descrita em compose, mas deployment não comprovado | Evidência operacional e acesso operacional | NOT_VERIFIED operacionalmente; potencial HIGH |
| Preparação imutável isolada | Origem declarada não verificada, ativação bloqueada | Área privada exige grants reais ainda não verificados | Não ativa head | Testes de origem e autorização de armazenamento | MEDIUM |

As classificações refletem impacto no código, não probabilidade de execução em produção. A probabilidade operacional para ferramentas/jobs não comprovados permanece `NOT_VERIFIED`.

## Plano incremental e gates

| Incremento futuro | Entrada / dependências | Testes e evidência de saída | Bloqueio / recuperação | Autorização separada |
|---|---|---|---|---|
| I0 — observar invocações dos escritores sem capturar payload | Linha de release identificada; aprovação de instrumentação; política de métricas sem PII | Contagens por família/entry point; testes que mostram ausência de alteração de resposta/estado | Bloquear se path desconhecido, custo/PII ou baseline não definido; remover instrumentação sem afetar dados | Sim, código e depois deployment por ambiente |
| I1 — contrato identidade/autorização/fence | I0 + mapear principal, serviço e grants; topologia DB disponível | Negativos de não autorizado, fence obsoleto e cross-track; adapter compatível async | Sem bypass e sem fallback; reverter isolando wrapper sem liberar old-writers com novo head | Sim |
| I2 — comandos estruturais piloto sem leitores públicos | I1; cobertura/isolamento da família delimitada | Concorrência, falha parcial, retry, histórico e operação legada simultânea bloqueada | Parar piloto; manter dados sob caminho antigo apenas antes do cutover controlado, nunca misturar gravação nos dois modelos | Sim |
| I3 — importação e restauração | I2 + política de serialização/recuperação; ADR-004/retention | Import-restore-publish interleavings, recovery em cada fase | Bloquear se qualquer worker obsoleto puder continuar; janela de bloqueio operacional | Sim |
| I4 — construção privada e comparação shadow | I1–I3 + segregação e classificação de taxonomia | Hash/consistência, comparação sem impacto público, não exposição | Descartar candidato incompleto; ponteiro público nunca alterado | Sim, dados de teste/sombra devem ser autorizados |
| I5 — leitores e publicação por geração | ADR-005/006; G1–G9 satisfeitos para escopo; G10 resolvido | Testes de pinning, no-mix, fail-closed, sessão/tentativa e rollback | Parar cutover; não fallback a coleções mutáveis; escalonar se rollback compatível não existir | Sim, integração e cutover independentes |

Os nomes I0–I5 são rótulos deste plano, não fases aprovadas. Nenhuma alteração funcional é autorizada por esta documentação.

## Gates preservados

| Gate | Estado histórico | Evidência desta fase | Estado após análise |
|---|---|---|---|
| G1 — cobertura de escritores | PARTIAL | Inventário estático com caminhos e bypasses; completude operacional não provada | **PARTIAL** |
| G2 — CAS/revisão/fencing | NOT_VERIFIED | C3 validou adaptador isolado; escritores ativos ainda não integrados | **NOT_VERIFIED** |
| G3 — snapshot coerente | NOT_VERIFIED | `snapshot_track` compara contagens; isso não satisfaz revisão coerente | **NOT_VERIFIED** |
| G4 — fronteira público/privado | PARTIAL | Nenhum grant/runtime revisado nesta fase; preparação imutável continua inelegível | **PARTIAL** |
| G5 — publicação atômica | NOT_VERIFIED | Publicação legada possui writes antes do CAS final | **NOT_VERIFIED** |
| G6 — leitores/sessões | PARTIAL | Sem mudanças; o escopo desta fase não validou leitores | **PARTIAL** |
| G7 — compatibilidade | PARTIAL | Mapeadas incompatibilidades, sem validação contra runtime | **PARTIAL** |
| G8 — shadow comparison | NOT_VERIFIED | Nenhuma execução | **NOT_VERIFIED** |
| G9 — retenção | BLOCKED | Exclusões e referências cruzadas foram identificadas; política segue pendente | **BLOCKED** |
| G10 — baseline operacional | BLOCKED | Nenhuma consulta à infraestrutura; ADR-008 continua bloqueado | **BLOCKED** |

## Primeiro incremento recomendado

O primeiro incremento técnico, quando autorizado e após o gate de baseline, é **instrumentação passiva de invocação em todas as famílias já listadas**, sem capturar conteúdo, gabaritos, payloads, IDs de aluno ou credenciais; sem rejeitar/escrever/alterar o comando; sem dual-write. Deve contar família/rota e resultado categorizado, usando correlação não sensível apenas se sua necessidade e retenção forem aprovadas.

Esse passo fornece evidência de quais caminhos são exercitados antes de migrar todos os escritores, mas não protege concorrência, não satisfaz G1/G2 e não libera cutover. Se cobertura de telemetria não puder ser instrumentada em todos os entrypoints ou o baseline não for escolhido, não há primeiro incremento de runtime seguro; a próxima dependência é a entrega sanitizada pedida ao administrador na Fase 12B.4B e a decisão humana da linha oficial.
