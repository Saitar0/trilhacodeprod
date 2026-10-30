# Arquitetura de integração da Trilha Code

**Estado:** proposta; não implementada. **Base examinada:** commit `147dc68b81169f66b0ba3802fa2f26e5130923a3`, branch `migracao-estrutura`.
**Escopo:** leitura do backend, frontend, JSON, testes e árvores migradas. Não houve importação ou alteração de dados.

## 1. Resumo

A plataforma não tem modelos distintos para fase, módulo, unidade, assunto ou projeto. Persiste uma trilha em MongoDB e representa a hierarquia por documentos genéricos `nodes`; conteúdos são documentos `content_blocks`. A hierarquia padrão em `backend/constants.py` é `phase → module → submodule → topic`.

A árvore migrada cabe sem criar nível: fase → `phase`, módulo → `module`, unidade → `submodule`, assunto → `topic`; cada arquivo educacional vira bloco ordenado do assunto. Entregas formalmente existentes podem ser tópicos filhos da unidade-projeto. Projetos sem marcos formais não ganham marcos artificiais.

O importador não reconhece todo o semântico da árvore: `answer_key`, posicionamentos compartilhados, rubricas de projeto e aceite formal não têm representação completa. Não converter desconhecidos em texto genérico. O JSON atual permanece legado e intacto.

**Decisão de compatibilidade já aprovada:** até uma tarefa futura e separada de extensão do importador/renderer, os gabaritos continuam no JSON legado em blocos `theory_text`, como limitação conhecida. A proposta de chave privada descrita adiante só vale para uma versão futura, após implementação e decisão de produto; ela não altera o comportamento nem o arquivo atual.

## 2. Implementação real

| Conceito | Evidência | Limite atual |
|---|---|---|
| Trilha/curso | `db.tracks`, `TrackIn` em `backend/schemas/content.py`, `backend/services/tracks.py` | O domínio chama a raiz de track; não há modelo de fase/curso separado. |
| Fase, módulo, unidade, assunto | `db.nodes`, `NodeIn`, `DEFAULT_HIERARCHY` | Níveis genéricos e um `parent_id` por nó. |
| Blocos | `db.content_blocks`, `BlockIn`, `backend/services/blocks.py` | Um `node_id`, `type`, `data`, `order` e `status`. |
| Relações | `db.relations`, `RelationIn`, `backend/services/relations.py` | Nó-a-nó; não liga um bloco a vários assuntos nem define posição. |
| Tipos/taxonomias | `backend/seed.py`, coleções `block_types` e taxonomies | Import valida contra catálogo cadastrado. |
| Progresso | `backend/services/progress.py`, `backend/schemas/progress.py`, `backend/indexes.py` | Identidade de progresso: aluno+nó+bloco; checklist persiste índices marcados. |
| Submissões | `backend/services/submissions.py`, `backend/schemas/submissions.py` | Tipos com capability submission; quiz não tem essa capability. |
| Snapshot/restore | `backend/services/versions.py`, `backend/integrity.py` | Snapshot estrutural não abrange progresso, submissões ou eventos do aluno. |

## 3. Mapeamento da árvore para a plataforma

| Fonte migrada | Destino proposto | Regra |
|---|---|---|
| Página da fase | Nó `phase` | ID e ordem da página/manifesto. |
| Módulo | Nó `module` filho da fase | Título e ordem curricular aprovados. |
| Unidade | Nó `submodule` | Preservar ID e slug original. |
| Pasta de assunto | Nó `topic` | Slug aprovado e ordem do manifesto. |
| Arquivo teoria/avaliação/referência | Bloco no nó assunto | ID estável, tipo explícito, ordem e proveniência. |
| Objetivo, resumo, critério, conexões e referências da unidade | Bloco(s) ou metadado no nó unidade | Mapear cada arquivo comum individualmente; README é índice, não nó. |
| Entrega/marco formal | Nó `topic` filho do projeto | Somente entrega literal da fonte; critérios e rubrica vinculados. |
| Projeto sem marcos formais | Unidade-projeto e blocos/tópicos de apoio existentes | Não inferir entregas de cenários ou checklists. |
| Arquivo `90_integracao/` | Bloco canônico e colocações/referências | Exige extensão para exibir em vários assuntos sem duplicar. |

O JSON `docs/courses/trilhacode/trilha-code-bulk-import.json` usa `track/options/nodes/relations`; a auditoria global registrou 10 nós phase, 53 module, 131 submodule, nenhum topic, 1.691 blocos e 50 relações. Portanto, não representa a árvore migrada atual.

A mesma auditoria reconciliou 2.890 arquivos migrados, 131 unidades (15 projetos), 4.311 registros de mapeamento, 2.879 destinos físicos mapeados e 2.890 IDs únicos. Foram encontrados 133 Markdown de origem. Esses números são a linha de base documental; não foram regenerados neste trabalho.

## 4. Importador: comportamento e limites

Endpoint: `POST /api/import/track` em `backend/routes_import.py`. `dry_run` é padrão. `backend/import_payload.py` valida forma JSON, UTF-8, profundidade e tamanho BSON. `backend/services/imports.py` valida refs, hierarquia, tipos, taxonomias, relações e ciclos.

Limites comprovados:
* Envelope sem `schema_version`.
* Tags ausentes podem ser criadas (`create_missing_tags` default true).
* Nós ausentes no pacote são relatados como intocados; não há política explícita de exclusão de blocos/relações omitidos.
* Reimportar refs evita duplicação, mas atualiza documentos/timestamps; não compara hashes nem classifica inalterado/conflito.
* A escrita completa não é uma transação atômica.
* `TRACK_FIELDS` e montagem do nó são allowlist; metadados da fonte não são copiados automaticamente. Nó novo recebe meta com `import_ref`; bloco usa referência composta.
* Não há índices únicos específicos para `nodes.meta.import_ref`, `content_blocks.meta.import_ref` ou identidade de relação.
* `GenericBlock` em `BlockRenderer.tsx` é fallback visual, não comprovação de compatibilidade semântica.

Testes identificados: `backend/tests/test_import_workflow.py` (dry-run/import/reimport); `backend/unit_tests/test_import_payload_shape.py` (forma/BSON); `frontend/e2e/admin-import.spec.ts` (UI); `backend/tests/test_phase2.py` (campos de resposta ocultos). Não cobrem conversão das árvores, conteúdo compartilhado nem rubricas de projeto.

O serviço de submissões mantém tentativas, respostas e estados (rascunho, enviada, em correção, corrigida/devolvida), com grading/feedback do instrutor. Progresso genérico incrementa `attempts` quando recebe estado `completed`; não verifica por si só a correção pedagógica de `data.correct` enviada pelo cliente.

## 5. Gabaritos e revelação

`quiz` persiste `question/options/correct_index/explanation` conforme `backend/seed.py`. `backend/services/nodes.py::_student_block` remove `answer`, `correct_index` e `explanation` da leitura do aluno; `test_student_node_payload_hides_assessment_solutions` confirma. Porém `QuizBlock` em `frontend/src/components/blocks/BlockRendererParts.tsx` usa esses campos para calcular/exibir correção. A seleção envia `correct` calculado no cliente ao endpoint genérico de progresso; quiz não é submetível pelo serviço existente. Isso comprova incompatibilidade no caminho do código.

Proposta: manter answer_key separado na fonte/manifesto e associá-lo ao quiz por ref. Compilar como chave privada de um quiz lógico; corrigir a tentativa no servidor; registrar a tentativa e devolver somente resultado autorizado. Não confiar no valor de acerto do browser. Decisão de produto pendente: depois do envio revelar apenas certo/errado ou também resposta/explicação. Recomendação: não expor a chave antes da tentativa.

`instructor_note` não é canal privado de gabarito; é renderizável e não foi encontrada regra de ocultação. A função de detalhe de submissão também retorna o bloco e precisaria sanitização caso seja reutilizada para quiz.

## 6. Conteúdo compartilhado e progresso

Cada arquivo `90_integracao/` é físico único e pode atender vários assuntos. Na plataforma, bloco tem um `node_id`; relações são entre nós e não carregam ordem de exibição.

| Opção | Avaliação |
|---|---|
| Bloco canônico em tópico de integração + relações | Menor extensão; contexto, ordem e progresso não ficam definidos. |
| Coleção proposta `content_placements` com refs ao bloco canônico e a cada assunto | Um conteúdo, várias aparições ordenadas. Exige API, leitor, validador e integridade referencial. Recomendada se precisa aparecer em cada assunto. |
| Duplicar o bloco | Rejeitada: risco de conteúdo divergente, IDs múltiplos e sincronização. |

Uma colocação teria `placement_ref`, `block_ref`, `node_ref`, `order` e origem. Recomenda-se progresso contextual por colocação, pois o progresso atual é por aluno+nó+bloco. Progresso compartilhado requer decisão de produto. Remover colocação não apaga bloco nem progresso automaticamente.

## 7. Projetos

Projeto não é entidade própria. Proposta: unidade genérica como contêiner, entrega formal como nó filho, aceite/checklist/rubrica/limiar vinculados somente conforme a fonte. `checklist` é interativo, não aceite formal. `practical_challenge` tem lista `acceptance`. Correção manual oferece critérios booleanos e score opcional, mas não impõe escala, descritores, pesos ou limiar. Preservar escalas existentes e não inferir novas. Projetos sem marcos formais permanecem sem marcos.

Inventário de projetos já confirmado na auditoria global:

| Escala de origem | Projetos |
|---|---|
| 0–4 | 3.5, 8.5, 8.6, 24.3, 24.4, 31.4, 31.5 |
| Sem escala numérica | 16.2, 16.3 |
| 0–2 | 39.2, 39.3, 46.2, 46.3, 52.1, 52.2 |

Há 56 arquivos de marco/entrega nos 14 projetos com quatro etapas formais. 39.2 é projeto sem marco formal e não deve ser convertido em quatro entregas por analogia.

## 8. Identidade, reimportação e rollback

Usar refs estáveis derivadas dos IDs do manifesto e namespace da trilha/fase/unidade/assunto. Título e ordem são mutáveis, não identidade. Guardar `meta.import_ref` operacional e `meta.source` com `arquivo_id`, caminho relativo, SHA-256, metadados originais e versão do conversor.

O plano futuro classifica refs como nova, inalterada, atualizada, ausente ou explicitamente removida. Comparar hash da origem aplicada, estado atual no banco e novo hash; divergência vira conflito. Ausência no pacote significa “não observado”, nunca exclusão. Exclusão só por tombstone revisado. Índices únicos requerem auditoria prévia de duplicatas.

Snapshots atuais cobrem estrutura, não estado do aluno. Rollback deve restaurar conteúdo estrutural sem reverter progresso/submissões implicitamente. Como o importador não é atômico, o piloto precisa ensaiar falha parcial.

## 9. Links e pendências

`docs/migracao/RELATORIO_AUDITORIA_GLOBAL.md` registra 2.785 links Markdown locais válidos; 556 externos identificados por sintaxe, sem consulta remota; 94 wikilinks preservados, raiz do vault não confirmada; 18 links para guia de projetos rastreado. Menções 47.2/47.3 são texto sem destino confirmado. Cópias 37.1/37.2 da origem da Fase 7 diferem das fontes oficiais da Fase 8 e foram mantidas.

Política: converter links internos para refs/rotas somente com destino inequívoco; preservar URLs externas; não inventar destinos para wikilinks; manter menções sem destino como texto; não fundir cópias. Wikilinks bloqueiam apenas publicação que prometa navegação por eles, até resolver raiz/plugin.

## 10. Gates antes da importação

1. Aprovar hierarquia e destino dos arquivos comuns.
2. Aprovar contrato versionado e metadados.
3. Resolver correção/revelação de quiz e privacidade de soluções.
4. Definir colocações compartilhadas e escopo de progresso.
5. Definir representação funcional de projetos, rubricas, aceite e limiares.
6. Definir status original versus publicação.
7. Resolver referências que precisam navegar e confirmar vault se wikilinks forem requisito.
8. Só então gerar candidato e validar; dry-run/importação experimental requer autorização futura.

### Arquivos consultados

`backend/constants.py`; `backend/schemas/content.py`; `backend/schemas/progress.py`; `backend/schemas/submissions.py`; `backend/database.py`; `backend/seed.py`; `backend/indexes.py`; `backend/routes_import.py`; `backend/import_payload.py`; `backend/services/imports.py`; `backend/services/tracks.py`; `backend/services/nodes.py`; `backend/services/blocks.py`; `backend/services/relations.py`; `backend/services/progress.py`; `backend/services/submissions.py`; `backend/services/versions.py`; `backend/integrity.py`; `frontend/src/components/blocks/BlockRenderer.tsx`; `BlockRendererParts.tsx`; `frontend/src/components/common/Markdown.tsx`.
