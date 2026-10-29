# Fase 2.1A.12C.14 — Seleção da primeira onda

## Decisão

**PRIMEIRA ONDA NÃO SELECIONÁVEL COM AS EVIDÊNCIAS ATUAIS.** A C14 não escolhe uma integração operacional. A razão não é a quantidade de arquivos: não há, hoje, um recorte de escritores sobre um estado editorial comum que possa ser migrado sem deixar writers capazes de contornar CAS, fencing, autorização por trilha ou auditoria.

## Candidatos comparados

| Candidato | Benefício | Dependências e cobertura | Risco / bloqueio | Julgamento |
|---|---|---|---|---|
| **A. Edição de blocos (W-07)** | Fluxo pequeno e muito estudado; protocolo C8/C10/C11 tem provas isoladas de CAS, fencing, audit e idempotência; sem alteração curricular. | Tem de cobrir W-07 e todo writer que escreve/retira/restaura/publica o mesmo bloco: track/node delete e duplicate (W-02/W-03/W-06), publication (W-04), import (W-10), restore (W-11), seed (W-13) e outras ferramentas/entradas ainda não reconciliadas. Precisa contrato HTTP, grant authority, ACL/retention, baseline ADR-008 e containment comprovado. | **CRITICAL:** uma edição protegida coexistindo com import/restore/publicação/exclusão livre deixa bypass. Atual `DELETE /blocks` usa `content.write`; clients não mandam revisão/idempotency no contrato ativo. Publicação e restore são multi-coleção. | **Não selecionado.** Mesmo `update_block` isolado não é um piloto seguro. |
| **B. Gestão isolada de grants sem converter writers** | Poderia preparar o lifecycle de autorização antes da edição. | Requer fonte única, permissionamento de grantor/revoker, admin global, delegação, auditoria, epoch, relação com `users`, `auth_sessions` e policy estática. Não protege writer que continua consultando apenas `content.write`. | Pode criar autoridade paralela e falsa sensação de enforcement; mudanças live de grant sem writers consumidores não fecham bypass. | **Não selecionado como primeira integração.** Só após decisões e como parte de uma fronteira completa; evitar grant operacional sem consumidor autorizado. |
| **C. Validação de contrato / evidência passiva sem mutação ativa** | Baixo risco, pode validar matriz, imports e contratos estáticos sem alterar request ou dados. | C14 já executa validação offline de JSON/inventário e recupera teste snapshot. Não protege autorização, revisão ou gravação; observabilidade pode perder eventos. | Não é integração de writer nem prova de cobertura dinâmica. Instrumentação passiva não substitui enforcement ou auditoria. | **Adequado apenas como preparação**, não como onda de integração operacional. |
| **D. Publicação/snapshots** | Resolveria consistência visível ao aluno e reader generation. | Requer todos os writers de fonte, snapshot da mesma revisão, geração imutável, head atômico, quiz/publication e leitores pinados (ADR-005/006). | **CRITICAL:** estados parciais atuais e reader mixed-generation; pode afetar tentativas/sessões. Snapshot unitário não prova atomicidade/publicação. | **Não selecionado.** É uma onda posterior às fontes e leitores. |

## Por que ainda não há subconjunto seguro de `content_blocks`

O inventário C13 e as fontes atuais mostram vários caminhos tocando os mesmos documentos ou conteúdo derivado:

* W-07 cria, edita, ordena e exclui blocks.
* W-04 `publish_track` atualiza status de blocks e outras coleções, grava quizzes/publicações e snapshot antes do CAS final da track.
* W-10 import atualiza/inclui blocks e nodes/relations/tracks em fases; lock/job cobre o próprio import, não o writer global.
* W-11 `apply_snapshot` exclui e insere lotes; lease/job não é fence aplicado a cada escrita.
* W-02 e W-06 exclusões/duplicações atravessam blocks e dados de progresso/tentativas.
* W-03 copia uma trilha composta; W-13 seed escreve conteúdo inicial sem principal editorial.
* W-12 snapshot helpers leem conteúdo e persistem versões/chunks; precisam se vincular à revisão de origem.

O scan estático C14 também encontrou writers de **estado do aluno** em `services/progress.py`, `services/activities.py`, `services/submissions.py` e `learning.py`. Eles não editam conteúdo editorial e não são adicionados como novos `W-*`, mas exclusão/publicação deve preservar o estado que gravam. O runtime de todos permanece não verificado.

As referências detalhadas por símbolo, operação, coleção, permissão, classificação e aceitação futura estão em [matriz de writers C13](editorial-generations-phase-2-1a-12c13-writer-coverage-matrix.md), revalidada em C14 pelo teste offline `test_editorial_writer_inventory.py`. Isso confirma estrutura do checkout, não chamadas externas, deployment, jobs implantados ou operação efetiva.

## Critérios de entrada antes de selecionar uma onda

Todos precisam estar satisfeitos para o escopo específico. O estado atual segue a [matriz de prontidão](editorial-generations-phase-2-1a-12c14-readiness-matrix.md):

| Critério | Estado C14 | Evidência necessária |
|---|---|---|
| Fonte primária de grants e relação com IAM | PENDING_DECISION | Decisão assinada de owner/IAM sobre fonte, lifecycle e evitar dupla autoridade. |
| Governança grant/revoke/delegação/recovery | PENDING_DECISION | Responsáveis e separação de deveres nomeados; anti-escalonamento aprovado. |
| Scope administrativo global | PENDING_DECISION | Scope explícito, provisionamento e revogação independentes; sem wildcard por papel. |
| Semântica de revogação de grant, role, permission, session e conta | PENDING_DECISION / BLOCKED | Política aprovada e ordem testável; matriz `PERMISSIONS` exige epoch ou drenagem coordenada. |
| Baseline/transação compatível (ADR-008) | BLOCKED | Evidência autorizada de SHA/digest, route, readiness, schema, driver, topology, concerns, roles e indexes. |
| Capability server-issued e IAM/fence separados | SATISFIED_IN_ISOLATION | C11/C12 negativos sintéticos; falta fronteira real validada. |
| Revisão monotônica/CAS/fencing/audit/idempotência | SATISFIED_IN_ISOLATION | Conformidade persistente isolada por C8–C12; não representa writer completo. |
| Todos os escritores que disputam o escopo | BLOCKED | Call-site/operator/runtime reconciliado; cada bypass convertido, bloqueado ou incapaz de alcançar o scope. |
| API/clients antigos, revision, null, receipt/replay | PENDING_DECISION | Contrato versionado, período de compatibilidade e resposta de conflitos aprovados. |
| ACL/retention/HMAC e privacidade | PENDING_DECISION | Matriz por record class e lifecycle de chaves aprovados. |
| Testes relevantes | SATISFIED_IN_ISOLATION / PENDING_TEST | Unit, persistência, falha e concorrência no alvo compatível; testes específicos de publicação/leitores ainda necessários. |
| Progresso, tentativas e gerações do aluno | PENDING_DECISION | Semântica de exclusão, restore, emergência e sessão pinada aprovada e testada. |
| Rollback ensaiado | BLOCKED | Pausa de entrada e bloqueio de writers antigos, reconciliação de receipts e recuperação sem reabrir bypass. |
| Autorização específica da implementação | PENDING_DECISION | Nova autorização exata depois de gates satisfeitos; C14 não inclui essa execução. |

## Critérios de saída de uma futura onda

Separar provas por tipo; nenhum resultado unitário substitui o seguinte:

1. **Unit/contrato:** input ausente versus `null`, patch vazio, campos extras, revisão esperada, operação e chave idempotente; ausência de payload em receipt/log; permission/grant/capability negativos; API não muda por inferência.
2. **Integração persistente:** sessão/grant/user estado relevante, CAS editorial, fence, mutação, auditoria, histórico e recibo no boundary aprovado; auditoria falha aborta tudo; resultado ambíguo reconcilia sem executar mutação de novo.
3. **Concorrência/falha:** clientes independentes, edição-versus-revogação, writer antigo concorrente, import/restore/publicação, rollback/cancelamento; sem stale commit, publicação parcial ou duplicação. Barriers explícitos, não sleeps.
4. **Snapshots/publicação/leitores:** geração representa uma revisão de fonte, candidato incompleto não fica público, troca de head é atômica, leitores ficam presos à geração correta e tentativas/sessões históricas são preservadas.
5. **Validação operacional autorizada:** executar no baseline real aprovado, com identidade de runtime, roles, índices, topology, routing/readiness e plano de monitoração verificados por processo ADR-008. Nenhum teste local pode ser rotulado operationalmente verificado.
6. **Aprovação humana:** decisões de governança, privacidade, API, suporte e rollback registradas; autorização explícita para implementar aquela onda.

Condição transversal de aprovação: não há alteração confirmada sem audit obrigatório; revisão obsoleta e fence stale são rejeitados; nenhum writer antigo consegue confirmar fora da autoridade; edição sem grant é negada; replay não duplica efeito e respeita autorização atual; conteúdo privado não é exposto; snapshots, publicação, progresso e tentativas permanecem íntegros; mudanças HTTP são aprovadas; regressões aplicáveis passam.

## Sequência futura condicional

Preservar a ordem C13: (0) owner/IAM decidem grants, admin, delegação, revogação, privacy; (1) baseline autorizado ADR-008; (2) validar lifecycle/grant no limite possível; (3) capability e contrato HTTP; (4) inventariar e conter writers por coleção/scope; (5) integrar uma família de escrita somente após containment de todos os concorrentes; (6) estrutura/relações; (7) catálogo/import; (8) snapshots/restore/publicação e readers; (9) expansão/cutover. Cada etapa exige nova autorização.

## Rollback específico da futura primeira onda

O rollback começa por pausar novas entradas de edição para o scope e impedir que instâncias, CLI, seed, worker, import, restore ou cliente antigo escrevam por caminho não protegido. Uma flag de rota sozinha não contém esses paths. Operações em resultado desconhecido ficam suspensas até reconciliação por identidade persistida. Confirmados, auditoria, revisão, grants revogados, receipts e histórico são preservados; correção de conteúdo é nova revisão, nunca exclusão da revisão confirmada para simular rollback. Não reabrir escritor legacy sem CAS/fence. Public head só retorna a generation validada por procedimento próprio. Apagar track/node, publicar conteúdo e expor dados são pontos potencialmente irreversíveis; política de retirada e progresso precisa ser aprovada antes de incluí-los.

**Resultado:** nenhuma onda de mutação é aprovada nesta fase. Próximo passo específico: registrar decisões do owner e autoridade IAM para D-03 a D-10, depois solicitar baseline ADR-008 pelo processo autorizado; então atualizar a matriz de readiness antes de propor o piloto novamente.
