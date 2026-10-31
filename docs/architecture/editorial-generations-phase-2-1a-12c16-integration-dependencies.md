# C16 — Dependências para conter writers antes de integração

## Regra de contenção

O limite não é “um endpoint” nem “um arquivo”: é o conjunto de operações que podem mutar a mesma autoridade editorial, conteúdo, referências, snapshots ou estado de publicação. Antes de ativar qualquer writer cooperativo, cada caminho concorrente precisa participar da autoridade compartilhada ou estar comprovadamente bloqueado no escopo atingido. Scripts, seeds, retomadas de job e workers contam como caminhos de escrita.

## Menor conjunto relevante identificado

Para uma alteração de conteúdo de uma trilha, o núcleo que deve ser coordenado ou bloqueado é:

* W-07 — conteúdo/blocos;
* W-05, W-08 e W-01 — estrutura, relações e metadados/ordenação que podem influenciar o snapshot e sua interpretação;
* W-04 e W-12 — publicação, snapshot, versão e reconciliação;
* W-10 e W-11 — importação e restauração por batches/jobs;
* W-02 e W-06 — cascades, exclusão e duplicação;
* W-03 — duplicação de trilha;
* W-13 e W-14 — seed e operações administrativas/migrações capazes de atingir o escopo;
* W-16 — helper de auditoria funcional, que deve participar da mesma sessão;
* W-09/W-15 — bloquear a ativação quando taxonomia/immutable publication influenciem o escopo ou quando o call graph permaneça indeterminado.

Essa relação é um conjunto de dependência do inventário versionado, não uma afirmação de que cada operação sempre altera exatamente o mesmo documento. A seleção de coleções e grants concretos depende do writer/call graph atual e de uma integração futura autorizada.

O estado de progresso, submissões e tentativas é adjacente ao conteúdo e deve ser preservado segundo os contratos pedagógicos: sessão vinculada à geração original enquanto válida, progresso/histórico de aprendizagem e tentativas preservados, correções auditáveis, retirada emergencial possível e sem revogação negativa automática de credenciais. C16 mostrou que uma transação pode apagar conteúdo e learner state juntos; não validou a política de retenção correta.

## Dependências entre famílias

| Família | Depende de | Ordem/proteção necessária | Bloqueio atual |
|---|---|---|---|
| Edição de bloco (W-07) | track revision/fence, auditoria, relação bloco-nó-trilha | CAS comum e audit transacional | W-07 real não usa protocolo integrado |
| Estrutura e relações (W-01/W-05/W-08) | resolução de trilha, integridade referencial, snapshots | mesma revisão quando altera material de trilha | writers não convertidos e autorização por trilha não aplicada |
| Publicação/snapshot (W-04/W-12/W-15) | conteúdo, nós, relações, versão fonte, leitores/head | snapshot de uma revisão identificada; validar antes da ativação; audit/receipt idempotentes | atual call graph e lifecycle W-15 indeterminados; C16 somente composição sintética |
| Importação (W-10) | estrutura, conteúdo, relações, taxonomia, snapshots, audit | job lease mais fence compartilhado; lote atômico ou recuperação explícita; repetir por identidade idempotente | importação sequencial não é uma transação global C8/C10 |
| Restauração (W-11) | versão/chunks, estrutura, conteúdo, relações, progresso | troca de snapshot consistente, fence contra worker antigo e política de learner state | batches e retomada real não comprovados sob protocolo |
| Exclusão/duplicação (W-02/W-03/W-06) | relações, snapshots/publicação, progresso/tentativas e referências | exclusão como operação composta e semântica explícita de tombstone/retirada | não se pode ativar enquanto cascade puder apagar histórico de aluno sem contrato |
| Taxonomia (W-09) | catálogo global e múltiplas trilhas/snapshots | decidir autoridade global/versionamento e blast radius | D na C13; não assumir revisão por trilha suficiente |
| Seed/admin/migrações (W-13/W-14) | namespaces, schemas, coleções e escopo do deploy | limitar à identidade/ambiente, classificar cada mutação; ordem de release | credenciais/execução implantadas não verificadas; lock não é fencing editorial |
| Auditoria (W-16) | todas as famílias que exigem registro funcional | mesma sessão transacional, ACL/retention aprovada | helper ativo sem session compartilhada, segundo inventário C13 |

O grafo do núcleo é: revisão/fence e grant → writers de estrutura/conteúdo/relations → snapshot/version → publicação ativa. Import e restore tocam múltiplas dessas famílias e precisam de exclusão mútua comum. Delete/duplicate podem cruzar learner state e geração. Audit, histórico e receipt são dependências finais de toda mutação obrigatória. Taxonomia/global catalog requer decisão separada.

## Ordem futura de implementação — sem execução nesta fase

1. **Fechar políticas:** aprovar governança de grants, escopo admin, delegação, emergência e retenção; especificar versão de IAM/papel/sessão e os responsáveis.
2. **Validar ambiente autorizado:** fechar ADR-008 por processo próprio; validar driver, replica set, topology, roles, session lifecycle, índices e schema implantados com autorização própria.
3. **Estabelecer identidade do writer:** separar credenciais de serviço e provar quais rotas, jobs, seeds e comandos usam cada uma. Não emitir capability baseada apenas em header, papel ou fence.
4. **Implementar coordenação comum:** num futuro change set autorizado, atualizar serviço/API de edição, auditoria compartilhada, CAS/fence, autorização transacional e idempotência, ainda sem cutover enquanto caminhos bypass puderem escrever.
5. **Proteger caminhos do núcleo:** estrutura, relações, exclusão/duplicação, importação e restauração; todos convertidos ou bloqueados em cada escopo ativável.
6. **Proteger snapshot e publicação:** ligar snapshot e manifest a uma revisão, testar mix de cardinalidade igual, publicar de forma idempotente e tratar falha/rollback sem alterar a geração usada por sessões já válidas.
7. **Restringir seed, admin e migrações:** classificar operações mutantes, identity/roles e release steps; remover escrita direta concorrente no escopo que entrar no cutover.
8. **Validar alunos/lectores:** progresso, tentativas, sessões, gerações, queries de leitura, restauração e retirada emergencial sob regressões específicas.
9. **Cutover por escopo somente com autorização:** canary e observabilidade passiva não substituem bloqueio de bypass; deve haver matriz de prova negativa de cada writer antigo.

Dependência impeditiva: passos 4–8 não podem abrir um escopo enquanto qualquer caminho de escrita capaz de alterar as coleções/invariantes daquele escopo estiver não adaptado ou não bloqueado.

## Rollback futuro

Rollback não pode apagar auditoria, receipts ou revisões já confirmadas nem reabrir grants revogados. Deve suspender a entrada nova, manter bloqueados os writers antigos para o escopo já migrado, reconciliar recibos/commits indeterminados, corrigir conteúdo por uma nova revisão auditada e retornar clientes por contrato compatível. Restaurar snapshot antigo é uma mutação editorial nova, não rollback de banco destrutivo. Recuperação de acesso/grant exige trilha de auditoria e aprovação separada.

Pontos potencialmente irreversíveis: publicação que já foi consumida, versão externa/snapshot exportado, efeitos de alunos, entrega de respostas HTTP e credenciais/roles em uso. Uma flag sozinha não remove esses efeitos nem previne calls administrativas/jobs.

## Critérios para reconsiderar primeira onda

Um recorte só pode ser proposto se:

* a cobertura de mutações concorrentes no conjunto protegido for demonstrada ou os caminhos não conformes estiverem efetivamente bloqueados;
* autorização por trilha, revogação papel/sessão/grant e roles de serviço tiverem fronteira de confirmação definida;
* snapshot/publicação e efeitos em sessões, progresso e tentativas forem cobertos quando alcançados;
* CAS/fence, audit, receipt, replay e erro de commit indeterminado tiverem testes persistentes e concorrentes;
* compatibilidade HTTP/leitores e rollback tiverem aprovados owners de produto/segurança/operação;
* ADR-008 e evidência de topologia/privilégios estiverem resolvidos em procedimento autorizado;
* houver autorização específica de implementação e depois de implantação.

**Conclusão C16:** a prova cooperativa reduz incerteza sobre a autoridade C8/C10, mas o caso B comprovou que o menor recorte operacional ainda não pode ser aberto enquanto a escrita antiga direta permanecer possível. A C14 continua correta em bloquear uma primeira onda operacional com as evidências atuais.
