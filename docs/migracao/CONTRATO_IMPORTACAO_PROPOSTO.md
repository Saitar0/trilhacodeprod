# Contrato de importação proposto

**Estado:** proposta para revisão; não é o JSON executável atual.  
**Base:** commit `147dc68b81169f66b0ba3802fa2f26e5130923a3`.  
**Restrição:** não substitui nem altera `docs/courses/trilhacode/trilha-code-bulk-import.json`.

## 1. Objetivos

O contrato futuro deve ter versão explícita; preservar IDs, metadados, ordem e proveniência; refletir fase/módulo/unidade/assunto; manter gabarito separado na fonte e oculto até regra aprovada; armazenar conteúdo compartilhado uma vez; vincular projeto, entrega, aceite, checklist e rubrica; e reportar conflito sem apagar conteúdo/progresso.

O payload atual é `track/options/nodes/relations`, sem versão de schema. Campos propostos requerem validador novo; o importador legado não deve ignorá-los silenciosamente.

**Compatibilidade vigente:** até uma tarefa separada estender importador e renderer, o JSON legado continua recebendo gabaritos em `theory_text`, conforme decisão já aprovada. A estrutura `private_answer_key` abaixo é proposta para o contrato futuro e não é serializada agora.

## 2. Envelope versionado proposto

Fragmento ilustrativo, não executável:

```json
{
  "schema_version": "trilhacode.import/2.0",
  "converter_version": "trilhacode-markdown-converter/1",
  "source": {
    "manifest": "docs/migracao/mapa_de_migracao_fase1.yml",
    "revision": "commit-ou-hash-da-fonte",
    "generated_at": "timestamp-UTC"
  },
  "track": {
    "ref": "trilhacode",
    "slug": "trilha-code",
    "title": "Trilha Code",
    "hierarchy": ["phase", "module", "submodule", "topic"],
    "meta": {"source_system": "markdown-manifest", "source_schema_version": 1}
  },
  "options": {
    "create_missing_tags": false,
    "missing_content_policy": "report_only",
    "conflict_policy": "fail_on_local_divergence"
  },
  "nodes": [],
  "relations": [],
  "content_placements": [],
  "tombstones": []
}
```

`schema_version`, `converter_version`, `content_placements` e `tombstones` não existem hoje; são extensões propostas.

## 3. Referências e ordem

* Refs de nós, blocos, relações e colocações são únicas no pacote e namespaced pela trilha.
* Manter prefixos f1–f10 e IDs dos manifestos. Exemplo conceitual: `trilhacode/f1/unit/3.1/subject/slug/block/q01`.
* Título, nome do arquivo e posição não definem identidade.
* `order` é inteiro explícito do manifesto, nunca ordem alfabética.
* Bloco registra caminho relativo, arquivo_id, hash do segmento, papel e versão do conversor.
* Quiz e answer_key têm origens distintas, ligados por `answer_key_ref`, mas identidade lógica estável do quiz.

## 4. Exemplo — unidade convencional

Fragmento ilustrativo da unidade 3.1; valores ausentes não devem ser inventados:

```json
{
  "ref": "trilhacode/f1/unit/3.1",
  "kind": "submodule",
  "parent_ref": "trilhacode/f1/module/3",
  "title": "Git local",
  "order": 1,
  "status": "draft",
  "pedagogical_type": "solo",
  "requirement": "obrigatorio",
  "depth": "media",
  "tags": [],
  "meta": {
    "source_id": "3.1",
    "source_slug": "Git_local",
    "source_key": "valor-original-se-existente",
    "source_status": "valor-original",
    "source_metadata": {},
    "source_files": []
  },
  "blocks": [],
  "children": [
    {
      "ref": "trilhacode/f1/unit/3.1/subject/01_registrar_e_ignorar_mudancas",
      "kind": "topic",
      "title": "Registrar e ignorar mudanças",
      "order": 0,
      "meta": {"source_slug": "01_registrar_e_ignorar_mudancas"},
      "blocks": []
    }
  ]
}
```

Campos ausentes são omitidos ou diagnosticados conforme regra aprovada. Status original (ex. rascunho/revisado no inventário) fica em `meta.source_status`; publicar não é automático. `estimated_minutes` só recebe valor existente.

## 5. Exemplo — quiz e answer_key separados

A fonte mantém dois arquivos; o contrato associa a chave e guarda-a privadamente:

```json
{
  "ref": "trilhacode/f1/unit/3.1/subject/slug/quiz/q01",
  "type": "quiz",
  "title": "Q1",
  "order": 10,
  "data": {
    "question": "Enunciado literal da fonte.",
    "options": ["Alternativa literal A", "Alternativa literal B"],
    "private_answer_key": {
      "answer_key_ref": "f1-id-do-gabarito",
      "correct_index": 1,
      "explanation": "Explicação literal do gabarito.",
      "reveal_policy": "after_submission"
    }
  },
  "source_files": [
    {"path": "caminho/quiz.md", "role": "question"},
    {"path": "caminho/gabarito.md", "role": "answer_key"}
  ]
}
```

A forma aninhada é proposta, não aceita pelo schema atual. Uma rota futura corrige no servidor; não confiar em acerto enviado pelo browser. Produto decide se após tentativa revela apenas certo/errado ou também alternativa/explicação. Recomendação: chave não sai antes da tentativa.

## 6. Exemplo — prática com solução

```json
{
  "ref": "trilhacode/f2/unit/4.1/subject/slug/practice/p01",
  "type": "practical_challenge",
  "title": "P1",
  "order": 20,
  "data": {
    "prompt": "Enunciado literal da prática.",
    "language": "valor original, se existir",
    "starter_code": "código original, se existir",
    "acceptance": ["Critério literal existente"],
    "private_solution": {
      "solution_ref": "f2-id-da-solucao",
      "body": "Solução literal existente."
    }
  },
  "source_files": [
    {"path": "caminho/pratica.md", "role": "practice"},
    {"path": "caminho/solucao.md", "role": "solution"}
  ]
}
```

`private_solution` não é protegido hoje. Só soluções presentes na fonte são incluídas.

## 7. Exemplo — compartilhado sem duplicação

```json
{
  "shared_blocks": [
    {
      "ref": "trilhacode/f1/unit/1.2/integration/p02",
      "type": "practical_challenge",
      "title": "P2",
      "data": {"prompt": "Enunciado literal compartilhado."},
      "source_files": [{"path": "90_integracao/P02.md", "role": "practice"}]
    }
  ],
  "content_placements": [
    {
      "ref": "trilhacode/f1/1.2/p02-at-subject-a",
      "block_ref": "trilhacode/f1/unit/1.2/integration/p02",
      "node_ref": "trilhacode/f1/unit/1.2/subject/subject-a",
      "order": 8,
      "progress_scope": "placement"
    },
    {
      "ref": "trilhacode/f1/1.2/p02-at-subject-b",
      "block_ref": "trilhacode/f1/unit/1.2/integration/p02",
      "node_ref": "trilhacode/f1/unit/1.2/subject/subject-b",
      "order": 4,
      "progress_scope": "placement"
    }
  ]
}
```

Hoje `BlockIn` possui um `node_id`. Essa extensão evita cópia. Progresso por colocação é proposta recomendada; compartilhar estado precisa de decisão.

## 8. Exemplo — projeto com entrega, aceite e rubrica

```json
{
  "ref": "trilhacode/f10/unit/52.1",
  "kind": "submodule",
  "title": "Título literal do projeto",
  "meta": {
    "project": true,
    "rubric_scale": {"min": 0, "max": 2},
    "threshold": {"value": 13, "out_of": 16, "source_present": true}
  },
  "children": [
    {
      "ref": "trilhacode/f10/unit/52.1/delivery/01",
      "kind": "topic",
      "title": "Título literal da entrega 1",
      "order": 0,
      "blocks": [
        {"ref": "f10-delivery-01-acceptance",
         "type": "acceptance_criteria",
         "data": {"items": ["Critério literal existente"]}}
      ]
    }
  ],
  "blocks": [
    {
      "ref": "f10-project-rubric",
      "type": "project_rubric",
      "data": {
        "scale": {"min": 0, "max": 2},
        "dimensions": [{"name": "Dimensão literal", "descriptors": {}}],
        "threshold": {"value": 13, "out_of": 16}
      }
    },
    {"ref": "f10-project-checklist", "type": "checklist",
     "data": {"items": ["Item literal existente"]}}
  ]
}
```

Dados são esquemáticos; não afirmam que essa escala/limiar pertençam juntos a projeto real. `acceptance_criteria` e `project_rubric` não existem no catálogo atual. Sem marco na fonte, não criar nó de entrega.

## 9. Campos e validação

Nó obrigatório: `ref`, `kind`, `title`, `order`; contextuais: parent_ref, status, estimated_minutes, taxonomias, tags, meta, blocks, children. Bloco obrigatório: `ref`, `type`, `order`, `data`; contextuais: title, status, source_files e campos privados. Relação: refs, tipo, enforced, note e origem. Colocação: ref, block_ref, node_ref, order e política de progresso. Proveniência: caminho, arquivo_id, source_hash, manifesto e converter_version.

Rejeitar schema desconhecido, IDs/caminhos duplicados, refs órfãs, tipos sem regra, pares quiz/gabarito quebrados, soluções sem prática, aceite/rubrica sem projeto/entrega e colocações sem bloco. Validar hierarquia, ordem, campos, UTF-8 e BSON antes de planejar escrita. Metadados não podem ser descartados silenciosamente.

## 10. Resposta do validador/importador proposta

O endpoint atual devolve campos como `dry_run`, `ok`, `errors`, `warnings` e `summary`. A resposta futura deve manter o fluxo atual reconhecível e acrescentar versão, ações por ref e erros tipados:

```json
{
  "schema_version": "trilhacode.import/2.0",
  "dry_run": true,
  "ok": false,
  "errors": [
    {
      "code": "UNRESOLVED_REFERENCE",
      "path": "relations[3].to_ref",
      "source_ref": "trilhacode/f1/unit/3.1/subject/example",
      "message": "A referência não existe no pacote."
    }
  ],
  "warnings": [],
  "actions": [
    {
      "ref": "trilhacode/f1/unit/3.1",
      "action": "unchanged",
      "source_hash": "sha256:...",
      "current_hash": "sha256:..."
    }
  ],
  "summary": {
    "nodes_create": 0,
    "nodes_update": 0,
    "blocks_create": 0,
    "blocks_update": 0,
    "placements_create": 0,
    "relations_create": 0,
    "unchanged": 1,
    "conflicts": 0,
    "missing_in_source": 0,
    "explicit_tombstones": 0
  }
}
```

Os nomes dos códigos e campos acima são proposta. O modo dry-run futuro deve ser sem escrita, inclusive sem criação de tags ou índices.

## 11. Compatibilidade com o JSON legado

JSON legado permanece intacto. O conversor futuro gera pacote candidato temporário versionado, valida e explica o delta; só adaptar ao formato legado por regra versionada sem perda. Nenhum fragmento acima é executável.
