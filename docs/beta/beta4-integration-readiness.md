# Beta 4 — prontidão para integração futura

## Resultado por camada

| Camada | Estado observado | O que falta |
|---|---|---|
| Fonte segmentada | 10 unidades lidas em revisão `rascunho`; arquivos do recorte rastreados/limpos na origem | Aprovação editorial para publicação e identificação de fonte canônica. |
| Conversor tipado | Todas as unidades convertidas com avisos; determinístico no teste | Adaptadores para critérios, materiais privados, referências e projeto. |
| Validação de payload | `validate_import_shape` real aceitou lote completo | Rever campos genéricos e contratos para tipos sem destino. |
| Persistência | Importador real em Mongo descartável; replay e retomada sequencial passaram | Atomicidade/recuperação para rede, concorrência, auditoria e integração C8–C16. |
| Leitores | `get_track_tree`/`get_node` reais; draft privado; projeção remove gabarito | HTTP, leitor publicado, ACL instrucional e frontend não exercitados. |
| Aprendizagem | Nenhum fluxo aluno executado | Quiz/tentativa, submissão manual, feedback e progresso vinculados à geração. |
| Projeto 3.5 | 11 materiais reconhecidos e retidos no contrato | Modelo e fluxo de projeto com marcos/rubricas e privacidade. |
| Segurança editorial | Políticas C8–C16 continuam experimentais; C16 comprovou bypass por escrita direta | Autoridade operacional comum para todos os writers, IAM/grants, fencing, auditoria e permissões DB. |

## Menor sequência futura segura

1. Aprovar a revisão curricular e congelar hashes/fontes da fase.
2. Definir destinos versionados para critério de conclusão, feedback/rubricas, descrições de referências e projetos, com ACL de aluno/instrutor.
3. Implementar staging privado e validação de lote que falhe fechado antes da promoção.
4. Integrar importação e promoção ao protocolo editorial aprovado: autorização, revisão, fencing, idempotência e auditoria consistentes.
5. Eliminar/bloquear todo writer concorrente com acesso direto ao estado protegido antes de cutover; C16 mostrou que uma convenção no conversor não contém esses bypasses.
6. Definir leitor HTTP versionado e projeção de aluno que exclua gabaritos/rubricas, validar contratos do frontend e geração.
7. Exercitar quizzes, submissões, progresso, snapshots, publicação e restauração em persistente concorrente; validar E2E e mobile.
8. Obter evidência operacional ADR-008 por procedimento autorizado, plano de rollback e nova autorização específica de integração/implantação.

## Bloqueios de publicação/aluno

Não publicar a trilha Beta 4. A fonte está em rascunho; respostas e rubricas de exercícios não têm ACL operacional comprovada; quiz permanece em draft e nenhum endpoint HTTP foi chamado. Critérios de conclusão não podem ser inferidos; materiais de 3.5 ainda não são atividades interativas. O teste de serviço não prova que uma conta real terá acesso nem que respostas estão protegidas em todas as rotas.

Gates históricos preservados: G1 PARTIAL; G2 NOT_VERIFIED; G3 NOT_VERIFIED; G4 PARTIAL; G5 NOT_VERIFIED; G6 PARTIAL; G7 PARTIAL; G8 NOT_VERIFIED; G9 BLOCKED; G10 BLOCKED. ADR-008 permanece bloqueado.
