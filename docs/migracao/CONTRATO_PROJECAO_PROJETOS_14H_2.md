# Contrato técnico — projeção offline de projetos (14H.2)

**Estado:** implementação isolada de leitura. Não é contrato de API, persistência ou publicação.

## 1. Modelos de origem reutilizados

Não há um segundo modelo de domínio. A projeção reutiliza os tipos definidos em `backend/curriculum_contract/models.py`:

- `ProjectSpec`: `ref`, `unit_ref`, título/escopo, flags formais, entregas, marcos, variantes, refs de checklist/rubrica, opções/seleção de stack, `source_metadata` e proveniência.
- `ProjectDelivery` e `ProjectMilestone`: identidade própria, título, corpo Markdown opcional, ordem, referências a aceite/checklist/rubrica/conteúdo e proveniência.
- `ProjectVariant`: ID e descrição originais, ordem, entregas associadas, stack opcional e proveniência.
- Blocos tipados: `AcceptanceCriteriaBlock`, `ChecklistBlock`, `RubricBlock` e os demais membros de `ContentBlock` referenciados por `content_refs`.
- `CurriculumNode` fornece a unidade proprietária; a validação exige `kind == "submodule"`.

A versão do contrato permanece `trilhacode.intermediate/1.2`. Não existe `project_version`, `delivery_version`, data de publicação ou seleção individual na fonte; esta projeção não os cria.

## 2. Interface offline

`build_project_index(contract_or_contracts)` recebe um `IntermediateContract`, mapping de contrato ou sequência de contratos de fase. Cada contrato é validado por `validate_contract` e copiado para um snapshot imutável. IDs de entidades repetidos entre contratos também são rejeitados.

`ProjectIndex` oferece:

- `project_refs` / `project_count`: inventário determinístico.
- `for_project(project_ref)`: snapshot para um projeto existente.
- `for_unit(unit_ref)`: projetos de uma unidade existente do tipo `submodule`; unidade sem projeto retorna tupla vazia.

Falhas de estrutura usam `ProjectProjectionValidationError`, com diagnósticos existentes ou códigos específicos. Erros de lookup usam `ProjectReferenceError`. Mensagens não incluem corpos de Markdown, descritores de rubrica ou texto de critérios.

## 3. Snapshot interno

`ProjectInternalProjection` contém:

```text
contract_schema_version  # versão real do contrato de origem
source_manifest          # manifesto real da fase
project                  # ProjectSpec integral, passos ordenados por (order, ref)
owner_unit               # CurriculumNode submodule integral
referenced_blocks        # mapa deduplicado ref -> ContentBlock integral
```

O projeto continua contendo listas distintas de `deliveries`, `milestones` e `variants`. A ordem é explicitada por `order`; desempate de leitura usa `ref`. A ordenação do snapshot não altera o contrato original.

`serialize_internal_project` e `serialize_project_index` são serializadores determinísticos para auditoria interna. Eles incluem conteúdo potencialmente sensível — rubricas, checklists, critérios e proveniência — e **não devem** ser usados em payloads públicos, logs ou snapshots distribuídos a alunos.

## 4. Resolução de referências

| Origem/campo | Tipo de destino exigido | Relação adicional exigida |
| --- | --- | --- |
| `ProjectSpec.checklist_refs` | `ChecklistBlock` | `owner_ref == project.ref` |
| `ProjectSpec.rubric_refs` | `RubricBlock` | O alvo explícito inclui `project.ref` |
| passo `acceptance_refs` | `AcceptanceCriteriaBlock` | `delivery_ref` ou `milestone_ref` e `owner_ref` identificam o passo correto |
| passo `checklist_refs` | `ChecklistBlock` | `owner_ref == step.ref` |
| passo `rubric_refs` | `RubricBlock` | Lista/alvo explícito inclui `step.ref` |
| passo `content_refs` | qualquer `ContentBlock` conhecido pelo contrato | bloco existe e `owner_ref == step.ref`; tipo e payload permanecem tipados |

Referências obrigatórias ausentes ou de tipo/alvo incompatível falham. Listas de referência com duplicatas falham. Campos opcionais que a fonte deixou vazios permanecem vazios; o adaptador não preenche destino, alvo ou relação ausente. Um mesmo bloco pode ser citado em contextos válidos diferentes, mas é deduplicado pela identidade dentro do mapa de blocos da projeção.

O validador do contrato também verifica IDs, estrutura, alvos de rubrica, projeto/unidade, flags de entregas/marcos e proveniência. Hashes de proveniência são validados quanto ao formato. O adaptador não abre os caminhos de origem nem recalcula hashes de segmentos; para verificação de bytes, o código existente `verify_source_hash(provenance, source_bytes)` requer bytes explicitamente fornecidos.

## 5. Projeção pública conservadora

`public_project_projection` e `public_project_payload` constroem a saída por allowlist positiva, sem `model_dump()` genérico:

```text
project_ref, unit_ref, title, scope,
deliveries[{ref,title,body,order}],
milestones[{ref,title,body,order}]
```

O texto de origem permanece Markdown literal. Não são projetados `source_metadata`, proveniência, `checklist_refs`, `rubric_refs`, referências de aceite/conteúdo, `variants`, opções/seleção de stack, estados administrativos, notas de aluno, tentativas, notas ou progresso.

Os payloads de checklist, rubrica e critério de aceite permanecem internos, pois o contrato não contém uma classificação de audiência para esses campos. `stack_options` são preservadas na projeção interna, mas não entram na pública enquanto seleção e apresentação ao aluno não forem aprovadas. Não há estado `published` criado.

O escopo e os corpos literais de projeto/entrega/marco são tratados aqui como texto instrucional do pacote curricular. A projeção não é servida por API. Uma ativação pública futura exige gate editorial/audiência explícito; esta allowlist offline não autoriza publicação.

## 6. Identidade e versionamento futuro

Agora:

- ID curricular é `ProjectSpec.ref`; entregas, marcos, variantes e blocos conservam seus próprios refs.
- Unidade é `unit_ref` e é um `submodule` existente.
- A proveniência e o hash do conteúdo vêm de cada registro de origem; não se inventa uma revisão de projeto.

[PROPOSTA — não aprovada] Uma futura persistência pode publicar snapshots imutáveis de projeto que pinem entregas, marcos, opções, rubricas e referências por hash. Alterações criariam nova versão, mantendo refs curriculares estáveis e histórico anterior. Ainda é necessário decidir se a versão do projeto engloba todos os componentes ou se componentes versionam separadamente e como tentativas/submissões fixam essa versão.

## 7. Limites

Este módulo não cria registros de submissão, evidência, revisão, aprovação, nota, tentativa, estado de checklist, conclusão ou progresso. Não escolhe stack, cria variante, transforma critério de aceite em rubrica, converte quiz, salva em MongoDB ou chama importador. O mapeamento do bundle para o importador permanece bloqueado até haver modelo destino sem perda.
