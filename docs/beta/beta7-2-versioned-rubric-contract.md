# Beta 7.2 — contrato de rubrica versionada

Implementação: `backend/curriculum_contract/beta7_2_rubric.py` e `beta7_2_assessment.py`.

Uma `VersionedRubric` fixa ID do projeto/rubrica, versão imutável, estado editorial, proveniência (revisão, caminho, artefato, hash e seção), critérios, descritores, regra de decisão e registro humano de aprovação. O hash canônico exclui apenas o campo que armazena o próprio hash.

Estados suportados: `DRAFT`, `PROPOSED`, `PEDAGOGICALLY_APPROVED`, `RETIRED`. Rubricas propostas/rascunho não podem conter aprovação ou regra decisória ativa. O estado aprovado exige registro identificável de aprovação, regra conhecida e critérios definidos com descritores. Isso é uma barreira estrutural; a aplicação precisa receber o registro de decisão de um responsável autorizado. O código desta fase não cria aprovação para a rubrica real.

`proposed_rubric_from_project` lê os descritores 0–4 da rubrica do pacote existente e os vincula aos quatro marcos. Como a fonte não especifica obrigatoriedade/agregação final, os critérios permanecem `SOURCE_DEFINED_BUT_AMBIGUOUS`, `required=None`, e a rubrica fica `PROPOSED`, sem regra de decisão.

A proveniência da rubrica aponta para o artefato original da rubrica; cada critério por marco mantém adicionalmente a proveniência do respectivo arquivo de instruções. As seções-fonte `Evidência` e `Verificação`, quando presentes, são copiadas para `observable_evidence` sem serem convertidas em condição automática de aprovação. A validação exige que todas as proveniências compartilhem revisão e estado editorial, preservando caminho, ID e SHA-256 próprios do artefato.

A frase-fonte que impede aceitar os marcos 3 e 4 enquanto credencial real ou dado pessoal estiver versionado é preservada como `RubricConstraint` tipada, classificada `SOURCE_DEFINED`, ligada a M03/M04 e marcada como impeditiva quando violada. Isso mantém a restrição concreta sem inventar como provar ausência de segredo ou como agregar os marcos para aprovar o projeto.

Uma avaliação grava versão do projeto e da rubrica, hash da rubrica, avaliador, aluno, submissão/tentativa, resultados por critério, evidência, feedback, estado anterior/seguinte, chave de operação e data. Uma nova versão não altera o registro histórico.

O único caminho de aprovação demonstrável offline usa uma rubrica marcada `synthetic_fixture=true`, com dados explicitamente sintéticos. Ela não é gravada como rubrica do projeto 3.5 real nem entra no endpoint de criação/edição de rubrica.
