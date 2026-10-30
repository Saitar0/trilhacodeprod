# Especificação técnica do fluxo seguro de quizzes

## Escopo e estado

Este documento registra o fluxo diagnosticado na Etapa 13B e a política aprovada e implementada no backend na Etapa 13C.1. A Etapa 13B foi somente especificação. A 13C.1 adicionou endpoints, persistência versionada e testes de integração isolados. O renderer continua sem alterações e ainda não consome a nova API.

## Fluxo atual comprovado

- O tipo de bloco quiz em backend/seed.py:53-55 armazena question, options, correct_index e explanation.
- A leitura do tópico passa por GET /api/nodes/{node_id} (backend/routes_content.py:132-136) e por get_node/_student_block (backend/services/nodes.py:23-34, 79-91). Para blocos avaliativos, o serviço remove answer, correct_index e explanation da resposta enviada a estudantes.
- O componente QuizBlock em frontend/src/components/blocks/BlockRendererParts.tsx:42-74 ainda lê correct_index, calcula a correção no navegador, grava selected e correct pelo callback de progresso, mostra explanation e permite tentar novamente. Com a filtragem atual, o renderer não recebe a chave nem a explicação que espera.
- POST /api/progress é declarado em backend/routes_progress.py:28-30. ProgressIn (backend/schemas/progress.py:6-10) aceita status e data genéricos; services/progress.py:29-52 persiste os dados enviados pelo cliente. Portanto, esse caminho não fornece correção autoritativa.
- POST /api/submissions/submit é declarado em backend/routes_submissions.py:38-40 e usa AnswerIn/submit_answer. O serviço exige que o tipo tenha capacidade submission; quiz não está no conjunto SUBMITTABLE de backend/seed.py. Não foi identificada uma rota de tentativa de quiz com correção automática no servidor.
- A rota de correção manual de submissões exige submissions.grade. Ela atende submissões existentes, não corrige o quiz no browser.

A incompatibilidade observada é funcional e concreta: o serviço oculta o gabarito e o renderer tenta corrigir localmente com esse gabarito.

## Correspondência com o contrato intermediário

O pacote backend/curriculum_contract/models.py já distingue QuizBlock de AnswerKeyBlock. O quiz tem referência para a chave; a chave retorna question_ref. A função student_quiz_view constrói uma apresentação com campos permitidos e não inclui a referência à chave.

A conversão futura deve preservar:

- QuizBlock.ref como identidade curricular externa.
- Identificador interno da plataforma como identidade própria, mapeada explicitamente.
- Ordem da questão e das alternativas.
- Referência recíproca entre quiz e AnswerKeyBlock.
- Resposta correta e explicação apenas no contexto de correção autorizado.
- Proveniência e hash da fonte.
- Revisão publicada imutável, associando enunciado, opções, gabarito, explicação e avaliador.
- Colocação curricular quando o quiz for compartilhado.

Gabaritos continuam tipados como answer_key. Não devem ser convertidos em theory_text.

O contrato intermediário permite múltiplos formatos, mas um avaliador seguro precisa conhecer a semântica de cada um. O escopo inicial de testes cobre multiple_choice; os demais formatos devem ser rejeitados até existir avaliador explícito e testado. Não aproximar respostas abertas, ordering ou fill_code como múltipla escolha.

## Contratos propostos

### Quiz público do aluno

Pode conter referência externa, revisão, título, ordem, enunciado, formato e alternativas. Não pode conter referência ao gabarito, respostas corretas/aceitas, resposta esperada, explicação protegida, pontuação, correção ou conclusão.

### Envio de tentativa

Contém revisão do quiz, contexto curricular quando aplicável, resposta tipada e chave de idempotência. A identidade do aluno vem da sessão autenticada. O payload não aceita user_id, correct, is_correct, score ou completed.

### Resultado corrigido

É produzido pelo servidor. Retorna pontuação agregada, aprovação, contadores e melhor nota; não retorna a contagem de respostas corretas por questão, a chave nem a explicação. Chave e explicação só aparecem no endpoint de revisão após três tentativas válidas. A tentativa não marca automaticamente o tópico como concluído.

### Histórico

É filtrado pelo usuário autenticado e preserva tentativa, revisão e ordem. Retorna pontuações e aprovação, mas não as respostas submetidas, a contagem de acertos, a chave ou as explicações; não pode servir como rota indireta para obter um gabarito ainda protegido.

### Correção administrativa

É uma representação administrativa separada, com autorização e trilha de auditoria próprias. Não reutiliza o DTO público do aluno.

Os exemplos de request/response e os erros propostos estão em docs/migracao/CONTRATOS_API_QUIZZES.md.

## Regras técnicas implementadas na Etapa 13C.1

1. Validar sessão, visibilidade, bloqueios curriculares e versão publicada antes de aceitar uma tentativa.
2. Validar a resposta contra o snapshot imutável. O avaliador atual aceita múltipla escolha com uma resposta correta; formatos sem avaliador são rejeitados.
3. Corrigir no servidor usando somente o gabarito privado da versão submetida.
4. Exigir o cabeçalho `Idempotency-Key`. Repetir a mesma chave e o mesmo corpo devolve o resultado persistido; reutilizar a chave com outro corpo gera conflito.
5. Reservar o número da tentativa com compare-and-set atômico no documento agregado de progresso, protegido por um índice único por usuário/quiz/versão.
6. Preservar cada tentativa válida. Publicar conteúdo avaliativo alterado cria outro snapshot; o histórico antigo continua ligado à versão usada.
7. Manter tentativas e aprovação separadas do endpoint genérico de progresso.
8. Na publicação, aceitar o formato legado `question`/`options`/`correct_index` e a projeção tipada de `QuizBlock` + `AnswerKeyBlock`, validando referências entre questão, gabarito e alternativa correta. Isso cobre a fronteira por fixture; a importação curricular continua fora do escopo.

## Política de produto aprovada

| Decisão | Valor aplicado |
|---|---|
| Tentativas máximas | 3 por usuário, quiz e versão |
| Aprovação | Pelo menos 70%, comparado antes de arredondar |
| Pontuação | Uniforme por questão; pesos explícitos são rejeitados porque o modelo atual não os valida |
| Nota considerada | Melhor nota válida |
| Histórico | Todas as tentativas válidas são preservadas |
| Revelação | Respostas corretas e explicações somente após a terceira tentativa válida |
| Aprovação antecipada | Não encerra tentativas nem libera gabarito |
| Tentativas restantes | Não são consumidas automaticamente |
| Versões | Snapshot imutável; cada versão mantém limite e histórico próprios |

O `GET` público expõe apenas enunciados, alternativas, metadados permitidos e estado resumido. O `POST` corrige no servidor e retorna nota/aprovação, sem alternativa correta, contagem de acertos ou explicação antes do esgotamento. A revisão é um endpoint separado, que revalida a elegibilidade no servidor em toda requisição. Como a política aprovada retorna pontuação agregada, quizzes de uma única questão podem permitir inferir o resultado daquela questão; impedir essa inferência exigiria alterar a política de produto sobre a divulgação imediata da nota.

O resultado do quiz não atualiza a conclusão curricular. A integração com progresso permanece fora do escopo.

Permanecem pendentes a adaptação do renderer, a integração futura com progresso, a administração/auditoria de versões e a avaliação de formatos além de múltipla escolha. Esses itens não reabrem as decisões de tentativas e revelação registradas acima.

## Segurança, concorrência e reimportação

- Autenticar pela sessão atual e autorizar acesso/tentativa no servidor; reutilizar a proteção existente de acesso ao conteúdo onde couber.
- Adotar limites de payload e respostas que não permitam enumerar chaves. O rate limiting dos endpoints de quiz foi implementado na Etapa 13C.1A e está documentado em `RELATORIO_ETAPA_13C1A.md`; a pontuação agregada imediata continua permitindo inferência em quizzes de uma questão.
- Não incluir gabaritos em logs de aluno, objetos genéricos de progresso ou respostas de leitura do quiz.
- Definir permissão administrativa própria para visualizar chaves; o nome quiz.answer_key.read usado nos testes é ilustrativo.
- Persistência deve impor unicidade apropriada à chave de idempotência e realizar gravação concorrente com operação condicional. Não presumir transação global entre coleções.
- Os novos endpoints reutilizam o grafo curricular para visibilidade e bloqueios de pré-requisito. Resultado, aprovação, contador e elegibilidade de revisão vêm exclusivamente da correção do snapshot e de `quiz_progress`; não são lidos nem escritos a partir de `POST /api/progress`. Como o endpoint legado ainda aceita status escolhido pelo cliente, a conclusão de pré-requisitos não-quiz permanece uma limitação que exige endurecimento separado.
- Reimportação deve criar ou atualizar revisão com política explícita. Ausência de um quiz na fonte não autoriza apagá-lo nem apagar tentativas.
- Tentativas antigas continuam ligadas à revisão antiga; uma revisão nova não torna a antiga resposta “errada” retroativamente.

## Etapas futuras

1. Adaptar o renderer para obter quiz público, enviar tentativas e representar resultado/revisão.
2. Integrar aprovação ao progresso somente após decisão específica de produto.
3. Planejar o uso da nova API nos quizzes migrados, sem revelar gabaritos pelo endpoint legado.
4. Validar comportamento em ambiente de homologação e definir rollback operacional.
