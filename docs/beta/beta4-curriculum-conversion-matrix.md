# Beta 4 — matriz de conversão curricular

Os estados abaixo descrevem o destino do payload experimental do importador atual, não uma futura integração aprovada.

| Campo de origem | Contrato intermediário | Destino atual no backend | Estado | Tratamento e risco |
|---|---|---|---|---|
| Identidade, módulo, ordem e objetivo | Metadados tipados da unidade | Nós, descrição, ordem e `meta.import_ref` | `SUPPORTED_WITH_TRANSFORMATION` | Hierarquia derivada de IDs; estado permanece draft/private. |
| Tópicos e segmentos Markdown | `TheoryTopic` / `TheorySegment` com origem e SHA-256 | Nós `topic` e blocos `theory_text` ordenados | `SUPPORTED_WITH_TRANSFORMATION` | 30 tópicos e 42 segmentos preservados individualmente. |
| Resumo | Texto da unidade | Bloco `summary` | `SUPPORTED_WITH_TRANSFORMATION` | Ordem e corpo preservados. |
| Questões, opções e resposta correta | `QuizQuestion` tipada | Blocos `quiz` em draft | `SUPPORTED_WITH_TRANSFORMATION` | O serviço real de leitura para aluno aplica `_student_block`, mas publicação/endpoint HTTP não foram exercitados. Gabarito no banco de teste não prova ACL operacional. |
| Explicações de quiz | Campo de explicação na questão | Campo de feedback do bloco draft | `SUPPORTED_WITH_TRANSFORMATION` | Projeção de aluno do helper remove `feedback`/`explanation`; política temporal de quando mostrar feedback segue pendente. |
| Enunciado/instruções de exercício | `ManualExercise` | Bloco `exercise_open`, correção manual | `SUPPORTED_WITH_TRANSFORMATION` | 26 exercícios; submissão e feedback humano não foram exercitados nesta prova. |
| Respostas de referência e rubricas | `RestrictedMaterial` separado | Nenhum destino ACL comprovado; não vai no payload | `REQUIRES_ADAPTER` | O material permanece apenas na representação experimental restrita em memória; não é persistido. |
| Checklists/aceite de marcos | Material de origem separado | Nenhum destino tipado com visibilidade | `REQUIRES_ADAPTER` | Classificação público/instrutor precisa de decisão e ACL. |
| Critérios de conclusão | `CompletionCriterion` com formulação original | Sem destino semântico no importador | `REQUIRES_ADAPTER` | O texto é preservado no contrato; não vira regra automática nem é enviado ao payload. |
| Relações/conexões | `CurricularRelation` e linhas não resolvidas | Coleção `relations` para destinos da fase | `SUPPORTED_WITH_TRANSFORMATION` / `REQUIRES_ADAPTER` | 21 relações internas persistidas como não enforced; alvos externos e linhas livres mantidos no contrato. |
| Referência: título, URL, ordem | `ReferenceItem` | Bloco `reference` | `SUPPORTED_WITH_TRANSFORMATION` | 39 referências, títulos/URLs persistidos. |
| Descrição de referência | Campo tipado e rastreável | O tipo aceita `citation`/`url`, sem descrição | `REQUIRES_ADAPTER` | Não foi descartada do contrato; falta destino semântico. |
| Brief/marcos/projetos | `ProjectMaterial` com origem e hashes | Sem schema operacional de projeto por marcos | `REQUIRES_ADAPTER` | 11 artefatos ficam fora do payload; 3.5 não é experiência de projeto jogável. |
| Gabaritos, rubricas ou conteúdo privado em leitor | Projeções públicas/restritas experimentais | `get_track_tree`/`get_node` reais, trilha privada e draft | `NOT_VERIFIED` para publicação | Leitura staff e negação ao estudante em draft foram observadas; endpoint publicado e ACL instrucional não foram validados. |

## Regra de integridade

Nenhum artefato Markdown de origem desaparece da proveniência: `source_artifacts` mantém caminho, hash, tipo, IDs de origem e ordem. Material privado fica fora do manifesto e do payload; somente hashes/identificadores/contagens são públicos no pacote de evidências. Um campo sem destino aparece em `field_dispositions`, nunca como perda silenciosa.

## Compatibilidade da estrutura real

O payload passou pelo `validate_import_shape` do serviço real e o `run_import` foi chamado em MongoDB descartável. O harness criou somente as taxonomias e tipos de bloco mínimos esperados pelo código. Isso valida o formato atual de importação e leitores de serviço, não schemas de produção, rotas HTTP, publicação, frontend ou política de acesso a respostas restritas.
