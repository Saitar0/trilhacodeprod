# Contrato executável de atividades tipadas

## Escopo

O módulo `backend/curriculum_contract/typed_activities.py` é uma camada experimental, estrita e independente dos modelos de produção e do contrato intermediário versionado. Ele converte atividades em memória e não acessa MongoDB, endpoints de importação ou publicação.

## Tipos discriminados

O campo `type` é um discriminador fechado:

| Tipo | Conteúdo público | Dados privados | Avaliação nesta etapa |
|---|---|---|---|
| `multiple_choice` | Enunciado e alternativas ordenadas | Chave original e opção resolvida, se inequívoca | Compatível com avaliador somente quando validado |
| `short_answer` | Enunciado e instruções existentes | Resposta esperada, aceites e explicação de origem | Indecidida; sem correção automática |
| `discursive` | Enunciado e instruções existentes | Resposta de origem, critérios/rubricas se existirem | Indecidida; sem correção automática |
| `matching` | Enunciado e listas de lados quando comprovadas | Pares corretos se comprovados | Indecidida; não suportada pelo avaliador atual |
| `ordering` | Enunciado e itens quando comprovados | Ordem correta se comprovada | Indecidida; não suportada pelo avaliador atual |
| `review` | Pergunta de revisão | Chave arquivística privada somente quando a fonte a possui | Sem pontuação |

Um discriminador desconhecido é rejeitado. Não há conversão genérica para `theory_text`.

## Registro interno

Cada `TypedActivityRecord` contém identidade curricular estável, tipo, fase, ID de origem, Markdown original, projeções pública e privada, versão da fonte do enunciado, estados de validação e publicação, compatibilidade do avaliador, política de avaliação, proveniência, hashes e diagnósticos.

O registro mantém `source_markdown` integral para auditoria. Esse campo e o objeto privado não fazem parte da projeção pública.

## Serialização

- `public_payload()` retorna somente o modelo público allowlisted: identidade, versão, título, ordem, prompt, instruções, referências e campos do tipo.
- `private_payload()` é uma operação separada e explícita para consumidores internos autorizados. Contém dados de correção quando existentes.
- `canonical_activity_json()` é serialização interna determinística do registro completo, incluindo gabaritos privados. Não deve ser enviada ao aluno, gravada em logs comuns nem tratada como pacote de publicação.
- `typed_activity_csv()` contém apenas metadados de classificação, estados, proveniência do enunciado e códigos diagnósticos; omite prompts e dados privados.

## Versões e integridade

`version_ref` segue `question-source-sha256:<64 hex>` e identifica a proveniência do enunciado público. O hash da fonte da chave e o hash canônico do payload privado permanecem no envelope interno. Isso permite detectar alterações nos dados privados sem expor o gabarito pela projeção pública. O ID operacional da versão persistida ainda depende de uma futura decisão de armazenamento.

Hashes de payload são SHA-256 de JSON UTF-8 canônico, ordenado por chave e sem espaços variáveis. A validação compara os hashes com os modelos efetivamente presentes.

## Estados

`validation_state`: `valid`, `incomplete`, `ambiguous` ou `pending_review`.

`publication_state`: `draft`, `pending_review`, `structurally_validated`, `publishable` ou `published`.

Os conversores desta etapa nunca produzem `publishable` ou `published`. O estado `structurally_validated` indica que o modelo tipado e, para múltipla escolha objetiva, o schema/corretor existentes aceitaram a representação. Não concede autorização editorial ou operacional.

## Políticas de avaliação

As políticas são modelos discriminados:

- `objective_server_policy`: exatamente três tentativas, aprovação em 70%, melhor tentativa válida e revelação depois da terceira. Aplicada somente aos 143 candidatos de múltipla escolha validados.
- `unscored`: revisão sem pontuação.
- `undecided`: nenhuma correção automática autorizada.

O contrato rejeita a política objetiva em resposta curta, discursiva, associação, ordenação ou revisão. Associação e ordenação só podem ser marcadas estruturalmente válidas se listas públicas e chave privada completa e consistente forem fornecidas. O protótipo 14D não produziu esses dados para as oito ocorrências.

## Referências e proveniência

Referências tipadas distinguem links internos, externos, Obsidian e editoriais. Links externos exigem URL HTTP(S) absoluta; links internos exigem `target_ref`; Obsidian/editorial preservam `raw_text`. A validação de coleção verifica alvos internos conhecidos. O conversor não inventa referências: `QuizBlock` não tem campo dedicado de refs, portanto a lista estrutural fica vazia e texto inline permanece no Markdown.

## Validações principais

- IDs e versão de origem com formato válido.
- Identidade e versão iguais nas projeções pública e no envelope.
- Tipos público/privado compatíveis.
- Hashes de payload e proveniência coerentes.
- Opções e itens sem IDs duplicados.
- Chave correspondente à atividade.
- Opção resolvida presente na lista pública.
- Pares/ordem apontando para itens existentes, quando fornecidos.
- Objetivo avaliável somente quando a chave é única e compatível com o corretor.
- Duplicação de identidades e referências internas não resolvidas diagnosticadas em nível de coleção.
- Estados publicáveis exigem estrutura validada.

## Projeção ao avaliador existente

`backend_question()` adapta somente atividade objetiva validada para `QuizQuestionOut`. `backend_grader_record()` é uma projeção privada explícita para `grade_quiz_questions`; nunca é payload público. As outras formas rejeitam essa adaptação em vez de degradar silenciosamente.
