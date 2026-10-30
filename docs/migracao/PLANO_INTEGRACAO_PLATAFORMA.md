# Plano de integração entre contrato intermediário e plataforma

**Estado:** proposta; adaptador não implementado.  
**Base:** commit 147dc68b81169f66b0ba3802fa2f26e5130923a3.

## Princípios e arquitetura

Contrato intermediário 1.2 e manifestos → adaptador puro/determinístico → pacote candidato versionado → validador offline/relatórios → importador futuro.

O adaptador não acessa API, banco ou rede. Preserva refs, hashes, caminhos de origem, ordem, metadados e versão do conversor. Ref curricular é chave externa; ObjectId é chave interna. Tipos sem regra explícita falham com diagnóstico. Ausência no pacote não exclui registro. JSON legado permanece intacto até autorização própria.

Separar conteúdo de autoria/correção, projeção de aluno e estado de tentativa/progresso. Gabarito e solução protegidos não são theory_text nem instructor_note. O endpoint atual dry_run consulta MongoDB; deve haver validação offline real antes de usar qualquer simulação de importação.

## Reimportação idempotente proposta

O importador existente encontra nó por meta.import_ref e bloco por ref composta node_ref/block_ref, conserva ObjectId de nó, mas não compara hashes e não possui índices únicos dedicados às refs externas.

| Classe de diff | Regra proposta |
|---|---|
| Novo | Ref sem registro correspondente |
| Inalterado | Mesma ref/hash e registro compatível com última importação |
| Atualizado | Fonte mudou e registro não divergiu por edição manual |
| Conflito | Registro diverge da última versão importada |
| Ausente | Não veio no pacote; sem mutação |
| Removido explicitamente | Tombstone revisado, fora do fluxo normal |

Auditar duplicatas antes de criar índices. Emitir relatório por ref; permitir interrupção antes de gravar. Título e ordem não identificam conteúdo. Não apagar por ausência.

## Quiz e revelação

Fluxo futuro: GET sem chave; POST de tentativa com ref, resposta e token idempotente; correção autoritativa no backend; registro separado de tentativa/resultado; retorno ao aluno segundo política de revelação; visão docente com autorização.

Decisões de produto: tentativas permitidas, retorno imediato de certo/errado, momento de liberar chave/explicação, retry e efeito em progresso/pré-requisito. Recomendação técnica não aprovada: correção servidor-side, retorno inicial sem chave e explicação liberada conforme regra definida pelo produto.

## Compartilhamento e progresso

Bloco canônico tem uma ou mais colocações com placement_ref, block_ref, subject_ref, ordem e proveniência. Atualizar fonte canônica reflete em todas as colocações; retirar uma colocação não apaga bloco nem progresso.

| Política | Fonte do progresso | Consequência |
|---|---|---|
| A. Global por bloco | Um estado/aluno/conteúdo | Completar num assunto vale em todos; pode alterar bloqueio e percentuais. |
| B. Por colocação | Um estado/aluno/aparição | Contexto preservado, mas pode haver repetição. |
| C. Híbrida | Estado oficial contextual; agregado informativo | Conteúdo único e progresso contextual; requer schema, APIs e índices. |

A/B/C é decisão pendente. Recomendação técnica: C com estado contextual como fonte oficial e agregado apenas visual; não usar agregado para desbloquear. Não migrar progresso sem levantamento/aprovação.

## Projetos

Escopo ligado à unidade; entregas e marcos distintos e apenas quando a fonte os declara; aceites associados ao alvo exato; checklist segue interativo; rubrica preserva múltiplos alvos, dimensões, escala, descritores, pesos e limiar; decisões/cenários/revisões permanecem tipados; stack selecionada não é inventada. Plataforma atual tem correção manual, mas não entidade projeto, workflow de entrega/marco, validação de rubrica completa ou seleção de stack.

## Referências

Links relativos viram refs somente com destino inequívoco. URLs externas permanecem preservadas. Wikilinks ficam intactos até confirmação da raiz do vault. Não criar dependência de guia local não versionado, não criar unidades 47.2/47.3, e seguir a escolha editorial para cópias 37.1/37.2. Referência necessária para tarefa ou pré-requisito sem destino bloqueia o percurso; menção editorial pode continuar texto.

## Plano incremental

| Etapa | Arquivos candidatos / dependências | Risco | Testes e aceite | Rollback |
|---|---|---|---|---|
| 1. Decisões | Documentação; fechar quiz, progresso, privacidade, status e refs | Política conflitante | Decisões assinadas e exemplos autoria/aluno aprovados | Sem efeito em dados |
| 2. Adaptador puro | Novo backend/curriculum_adapter, fixtures e testes | Perda de refs, ordem ou metadata | Golden files, determinismo, sem I/O, refs sem órfãos, desconhecidos falham | Remover apenas módulo isolado |
| 3. Schema/reconciliação | backend/import_payload.py, schemas/content.py, services/imports.py, indexes.py | Duplicatas ou edição manual perdida | Diff por hash/ref; idempotência; ausência sem exclusão; índice após auditoria | Reverter código antes de uso |
| 4. Quiz servidor-side | Schemas/rotas/serviços, services/nodes.py, QuizBlock e testes | Vazamento/acerto falso | GET aluno sem chave; servidor corrige; retry/revelação validada | Feature flag/rota desativada; manter tentativas |
| 5. Shared placements | Nova collection/schema, nodes.py, progress.py, routes_progress.py, indexes.py, NodeReader | Progresso/ordem incorretos | Um bloco com N posições; ordem por contexto; retirada não apaga estado | Desativar nova leitura; não apagar dados |
| 6. Projetos/rubricas | Schemas, submissions, rotas e renderer/editor | Checklist confundido com aceite ou escala alterada | Alvos, ordem, escala, descritores, threshold fiéis; nenhum marco fictício | Desativar feature; conservar fonte |
| 7. Pacote/validador offline | Ferramenta isolada, schemas e testes | Tipo ou link não representável | Saída em diretório novo; validar refs/hashes/BSON/determinismo; JSON legado intacto | Excluir somente candidato temporário |
| 8. Dry-run isolado | Importador e testes com Mongo descartável; autorização futura | Ler banco errado ou gravar | Confirmar ambiente descartável; provar ausência de escrita; diff completo | Descartar somente ambiente temporário |
| 9. Piloto funcional | Testes E2E/roteiro em ambiente isolado; autorização futura | Escrita parcial/impacto em progresso | Falha induzida, relações, quiz, placements, projeto, permissões e restore | Snapshot e compensação ensaiados |
| 10. Importação completa | Pacote e roteiro final; autorização separada | Volume, conflitos e publicação | Diff antes/depois, todas as fases e fluxos aluno/instrutor | Backup e plano compensatório; sem exclusão por ausência |

services/imports.py grava track/nodes/blocks/relations sequencialmente; não há transação global demonstrada. O snapshot de services/versions.py cobre conteúdo estrutural, não progresso/submissions/events. Antes de piloto, confirmar ambiente descartável, duplicatas e mecanismo de compensação; não presumir atomicidade do MongoDB.

## Decisões pendentes

1. Tentativas e revelação de quiz.
2. Política A/B/C de progresso compartilhado.
3. Visibilidade de soluções, rubricas e notas do instrutor.
4. Modelo de entregas/marcos sem inferir etapas.
5. Referências obrigatórias e raiz do vault.
6. Resolução de conflitos com edição manual.
7. Tradução de status/carater para publicação.
8. Responsável pela escolha de variante/stack e persistência.

**Parecer:** próximo passo futuro é o adaptador puro isolado, após decisões que afetam a projeção. Antes de importação, resolver quiz, progresso compartilhado e semântica de projetos. Aceite inicial: pacote determinístico e validado offline, sem perda. Esta proposta não autoriza código, JSON final, banco ou importação.
