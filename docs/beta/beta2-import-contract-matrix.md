# Beta 2 — matriz dos contratos de importação

## Contratos identificados

### Importador C16

`POST /api/import/track` aceita o envelope `track/options/nodes/relations`. A rota exige `content.write` e usa `dry_run=true` por padrão. O serviço `backend/services/imports.py::run_import` valida a forma, planeja e executa importações com jobs, lock/lease, referências estáveis e retomada. A execução é por fases e **não é uma transação global**. O importador grava auditoria própria ao final; falha parcial é possível e precisa ser tratada pelo mecanismo de retomada.

Refs estáveis do payload viram `meta.import_ref`; `_id` é `ObjectId`, enquanto `track_id` e `node_id` são strings. O importador cria trilha em `draft`; status de blocos deve ser enviado explicitamente para evitar o default legado `published`. A prova envia também visibilidade `private`.

### Contrato tipado da migração

Na worktree `migracao-estrutura`, o código local apresenta Pydantic `IntermediateContract` (`trilhacode.intermediate/1.2`) com nós, blocos tipados, relações, placements, projetos, proveniência por arquivo/hash, manifestos e diagnósticos. `CurriculumImportBundle` (`trilhacode.import_bundle/1.0`) agrega dez contratos de fase e exige IDs globais únicos. O bundle não embute uma projeção semântica para o endpoint legado e o relatório local registra que o endpoint não aceita essa versão.

Esses módulos são locais/dirty, não dependências rastreadas da base Beta 2. O conversor desta fase é um adaptador estreito para uma unidade e o contrato C16; não é uma cópia nem substituto do contrato tipado.

## Correspondência da unidade 1.1

| Fonte curricular | Destino C16 usado/avaliado | Resultado e ressalva |
|---|---|---|
| `key`, título, estado | `node.ref`, `node.title`, estados `draft` | Refs reprodutíveis; status `rascunho` não publica |
| `tipo`, `carater`, `profundidade` | `node.pedagogical_type`, `requirement`, `depth` | Campos existem e o importador valida chaves na taxonomia; validado com cópias sintéticas das chaves reais do seed |
| Tags, estimativa | `node.tags`, `estimated_minutes` | Persistência do importador usa `tag_ids`; conversão executada |
| Objetivo | `node.description` | Preservado, mas não existe um bloco `objective` legado |
| Teoria | `theory_text.data.body` | Preservada em um bloco; segmentação em cinco tópicos não preservada |
| Resumo | `summary.data.body` | Compatível |
| Perguntas e alternativas | `quiz.data` versionado | `normalize_quiz` reconhece `activity_schema_version=1`, `prompt`, opções com IDs, `correct_option_id` e feedback. A metadata do `block_types` legado não declara todos esses campos: o importador alerta que serão armazenados e não editáveis pelo editor genérico |
| Gabarito do quiz | Campos privados da definição versionada | Não devem aparecer na projeção pública. `normalize_quiz`/`public_activity` e `_student_block` foram testados offline; a unidade não foi publicada nesta prova |
| Enunciado e critérios de autocorreção | `exercise_open.data.prompt/criteria`, `grading=manual` | Representa exercício com correção manual; critérios enviados são visíveis na leitura comum do bloco |
| Solução de exercício | Sem destino privado demonstrado | O conteúdo do gabarito fica no objeto tipado em memória, é reportado como não mapeado e não é persistido pelo conversor |
| Referência | `reference.data.citation/url` | Título e URL preservados; descrição da referência não tem campo equivalente e não é persistida |
| Critério de conclusão | Sem destino semântico comprovado no C16 | Mantido na saída tipada e manifesto, ausente do payload persistido |
| Conexões internas | `relations` exigem refs resolvidas e tipos de taxonomia | Não mapeadas no piloto: alvos fora do payload e resolução de wikilinks não ratificada |
| Gerações/placements e escopo de progresso | Sem representação no payload legado | Requer adaptador próprio e decisão de produto; não inferir placement compartilhado |

## Observações de segurança e leitura

O teste de persistência chama o `run_import` real em banco descartável com metadados sintéticos de `block_types` e taxonomias. Ele não chama a rota HTTP, não usa IAM real, não usa o seed completo e não publica. Os leitores reais `nodes.get_track_tree` e `nodes.get_node` retornam a árvore para um ator sintético staff. A leitura de estudante é negada porque a trilha fica privada e em rascunho.

A chave de idempotência interna do importador deriva do payload completo. Repetir o mesmo payload sintético recuperou o job concluído sem duplicar trilha, nó, blocos ou auditoria. Isso valida o serviço legado em condições exercitadas, não sua integração à autoridade editorial transacional C8–C16.
