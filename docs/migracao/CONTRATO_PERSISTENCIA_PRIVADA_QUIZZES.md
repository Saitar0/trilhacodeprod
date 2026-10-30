# Proposta — contrato de persistência privada de quizzes

**Estado: especificação, não implementada.** Esta proposta descreve um caminho compatível com os objetos de quiz do backend existente. Não cria coleções, índices, migrações, documentos ou dados.

## Comportamento existente observado

- `backend/schemas/quizzes.py` separa `QuizPublicOut`, `QuizAttemptOut`, `QuizHistoryOut` e `QuizReviewOut`. O payload público de questão contém apenas `question_id`, `order`, `prompt` e `options`.
- `backend/services/quizzes.py::_question_snapshot` aceita múltipla escolha e exige pelo menos duas opções, uma chave válida e uma identidade persistida do bloco. Tipos não suportados, pesos não suportados e chaves inconsistentes são rejeitados.
- O snapshot interno atual mantém `correct_option_id`, explicação, ref da chave e proveniência junto do registro da questão. `_public_question` usa uma allowlist para retirar esses campos.
- `publish_quiz_version` calcula hash do conteúdo e reutiliza a versão de mesmo conteúdo. O serviço preserva versões; o catálogo aponta para a versão publicada ativa.
- O corretor compara respostas no servidor, contabiliza questões com peso uniforme e decide aprovação com `correct_count * 100 >= 70 * total`. O valor exibido pode ser arredondado sem alterar a comparação.
- O serviço aplica até três tentativas por usuário/quiz/versão, preserva melhor nota e histórico, e libera revisão depois da terceira. A estrutura de progresso é isolada por usuário, quiz e versão.
- `backend/indexes.py` declara unicidade em `(quiz_id, content_hash)` para `quiz_versions` e `(user_id, quiz_id, version_id)` para `quiz_progress`. Esses são comportamentos definidos no código; não foram inspecionados em banco nesta etapa.

## Contrato proposto para uma versão

Usar uma identidade externa estável do bundle para relacionar currículo, quiz e questão. Não substituir a identidade externa por `ObjectId`: guardar um mapeamento explícito para IDs internos e usar o `ObjectId` apenas como chave operacional Mongo.

```json
{
  "_id": "ObjectId interno da versão",
  "quiz_id": "ObjectId interno do tópico",
  "curriculum_ref": "fX-...-quiz",
  "version": 1,
  "status": "draft|published|retired",
  "content_hash": "sha256 canônico do conteúdo público e privado",
  "created_at": "timestamp do servidor",
  "created_by": "identidade administrativa",
  "source": {
    "bundle_version": "trilhacode.import_bundle/1.0",
    "source_manifest_ref": "referência estável",
    "source_sha256": "sha256 da fonte",
    "answer_key_ref": "fX-...-answer-key",
    "answer_key_sha256": "sha256 do bloco de gabarito"
  },
  "public": {
    "title": "título aprovado",
    "questions": [
      {
        "question_id": "fX-...-quiz",
        "order": 1,
        "prompt": "Markdown original preservado",
        "options": [{"option_id": "a", "text": "alternativa original"}]
      }
    ]
  },
  "private": {
    "answer_keys": [
      {
        "question_id": "fX-...-quiz",
        "answer_key_ref": "fX-...-answer-key",
        "correct_option_id": "a",
        "explanation": null,
        "source_sha256": "sha256 do gabarito original"
      }
    ]
  }
}
```

O exemplo é estrutural. Os valores de conteúdo são placeholders e não representam uma resposta curricular.

### Identidade e versionamento

- `curriculum_ref` identifica o quiz de forma estável entre conversões.
- Cada questão mantém seu ID curricular estável; cada chave mantém seu próprio ID e `question_ref`.
- `quiz_id` e IDs de blocos persistidos continuam sendo internos. O adaptador precisa resolver cada ref externa e registrar o vínculo sem alterar os IDs do bundle.
- A versão é imutável depois de publicada. Mudança em enunciado, alternativa, ordem, gabarito ou explicação produz novo `content_hash` e uma nova versão.
- O hash canônico cobre os campos públicos, privados e a associação entre questão e chave. Ele não deve ser retornado em API pública nem ser calculável apenas a partir do payload do aluno.
- A reimportação do mesmo conteúdo deve localizar a mesma versão por identidade externa e hash. Uma diferença de hash gera proposta de versão nova; não sobrescreve histórico.

### Separação pública e privada

Recomendação: manter campos `public` e `private` separados no snapshot interno, mesmo que compartilhem o documento de versão já usado pelo serviço. Esse caminho reduz mudanças no armazenamento atual e explicita a fronteira. Uma coleção privada dedicada é uma alternativa com isolamento mais forte, mas exige consistência transacional ou um protocolo de publicação incompleta/confirmada.

Regras de acesso propostas:

1. Leitura pública constrói `QuizPublicOut` somente por allowlist a partir de `public`; nunca serializa o documento Mongo completo.
2. O corretor do servidor lê `private.answer_keys` apenas no serviço de correção.
3. Histórico e recuperação devolvem resultado e tentativa, sem chave, explicação ou contagem correta por questão.
4. Revisão carrega os dados privados apenas depois que o serviço confirma três tentativas válidas para aquela versão.
5. Logs, exceções, telemetria e relatórios registram refs e códigos de erro, não o texto dos gabaritos.
6. O pacote integral do importador e snapshots privados ficam restritos ao processo administrativo; não são payloads do aluno.

### Gate de publicação

Uma versão só poderia ser publicada por operação administrativa autorizada após:

- todas as questões terem tipo suportado pelo avaliador;
- cada questão avaliável ter alternativas não vazias, IDs únicos e ordem preservada;
- existir exatamente uma chave vinculada a cada questão que exige chave;
- a resposta correta apontar para uma opção que existe, sem inferência textual;
- explicações serem copiadas apenas quando existirem na fonte;
- não haver respostas aceitas ou pesos que o avaliador não suporte;
- hashes, refs, origem e contagem de questões validarem;
- um segundo gate editorial aprovar questões hoje ambíguas.

Falha em qualquer condição mantém a versão em rascunho/bloqueada. Não há publicação parcial de um quiz que aparenta completo.

## Histórico e tentativas

O modelo atual de `quiz_progress` associa tentativas ao usuário, quiz e versão. A proposta mantém esse escopo. Cada tentativa aponta para a versão imutável e grava as respostas submetidas, resultado calculado no servidor, nota, aprovação, número da tentativa, horário e hash idempotente.

O progresso avaliativo não deve ser sobrescrito pela importação curricular. O histórico continua append-only, limitado pelas regras de produto vigentes. Uma nova versão inicia seu próprio contador e não recalcula resultados antigos.

`quiz_passed` deve consultar aprovação persistida pelo backend, nota mínima de 70% e versão publicada que satisfaça a regra de versão ativa definida pelo produto. Não aceitar `passed`, `score` ou tentativas enviados pelo cliente como fonte.

## Índices e consistência — proposta

- Preservar a unicidade atual `(quiz_id, content_hash)` em `quiz_versions`.
- Preservar `(user_id, quiz_id, version_id)` em `quiz_progress`.
- Adicionar um vínculo único entre `curriculum_ref` e tópico interno, depois de validar dados antigos e definir namespace de curso.
- Garantir unicidade de chave por `(version_id, question_id)` se as chaves forem armazenadas separadamente.
- Reutilizar a chave idempotente persistida para retries; nunca permitir que retries criem outra tentativa.
- Não criar ou aplicar índices nesta etapa. A migração 0003 e a criação de índices exigem aprovação e validação em banco descartável.

## Decisões ainda pendentes

- Aprovar a forma final de separação `public/private` e quem pode consultar campos privados.
- Definir se chave e versão ficam em um documento ou coleções separadas, considerando topologia e transações reais.
- Aprovar retenção, auditoria administrativa e política de revogação de versões.
- Resolver os 11 gabaritos ambíguos e os 358 outros itens bloqueados antes de criar snapshots avaliáveis.
- Confirmar a regra de `quiz_passed` quando uma versão nova substitui a ativa.

Nenhuma recomendação desta especificação foi implementada ou aplicada ao MongoDB.
