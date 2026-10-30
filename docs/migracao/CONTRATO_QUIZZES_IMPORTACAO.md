# Contrato proposto — quizzes e gabaritos na importação

**Status: proposta; não implementada.** Origem: `trilhacode.import_bundle/1.0`, SHA-256 `43e3619dc9caaa92c2e9dd8bf3bea45f2a2934e73458c297fe9206e27b1281c2`.

## Inventário verificado

- 506 questões: todas `format=other` e sem alternativas estruturadas.
- 501 exigem gabarito. Cada uma possui resposta esperada em texto livre; 99 também possuem explicação. Não há resposta correta por índice/alternativa nesse conjunto.
- Cinco perguntas R1–R5 do projeto 16.3 não têm gabarito. São revisão das decisões do projeto, não devem ser pontuadas por regra inventada.
- O serviço atual `backend/services/quizzes.py` aceita `multiple_choice`, exige pelo menos duas opções e gabarito avaliável. Portanto nenhuma das 501 questões textuais é compatível com o corretor atual.

## Contrato de dados proposto

Separar conteúdo público e chave privada por versão:

```json
{
  "quiz_ref": "fN-...",
  "version_ref": "sha256:<hash-canônico-do-conteúdo-avaliativo>",
  "curriculum_ref": "fN-...",
  "title": "...",
  "questions": [
    {
      "question_ref": "fN-...",
      "order": 0,
      "format": "multiple_choice | true_false | short_answer | ordering | fill_code | unscored_review",
      "prompt_markdown": "<texto original integral>",
      "options": [{"option_ref": "...", "order": 0, "text_markdown": "..."}],
      "provenance": {"source_file": "...", "source_id": "...", "source_sha256": "..."}
    }
  ],
  "private_answer_keys": [
    {
      "answer_key_ref": "fN-...",
      "question_ref": "fN-...",
      "correct_option_ref": null,
      "accepted_answers": [],
      "expected_answer_markdown": "<resposta original integral>",
      "explanation_markdown": null,
      "provenance": {"source_file": "...", "source_id": "...", "source_sha256": "..."}
    }
  ],
  "assessment": {"mode": "server_scored | manual_review | unscored", "policy_ref": "..."}
}
```

Os campos são propostos como separação de autoria/API, não como schema final. Um campo vazio não autoriza completar conteúdo. A presença de `expected_answer_markdown` não torna a resposta automaticamente avaliável.

### Invariantes

1. IDs curriculares estáveis são preservados; `question_ref` e `answer_key_ref` não são regenerados por ordem de leitura.
2. Uma chave deve apontar para exatamente uma questão e cada questão marcada como exigindo chave deve ter exatamente uma chave válida.
3. `order` vem da fonte; reordenação é alteração de conteúdo versionado.
4. O hash da versão cobre enunciado, alternativas, chave, explicação, ordem e política avaliativa, mas o hash de conteúdo privado não é enviado ao payload público.
5. O endpoint de aluno recebe allowlist sem resposta, explicação ou metadados de correção. Revisão só é montada pelo backend sob política aprovada.
6. A chave e as explicações ficam em armazenamento/coleção privada, com autenticação e autorização; não entram em bloco de leitura genérico, logs, erros ou OpenAPI público.
7. Markdown original integral é preservado como conteúdo-fonte. Extração de alternativas exige marcadores literais inequívocos e reconstrução byte/texto validada; não se converte automaticamente resposta livre em opção.
8. Qualquer duplicidade de marcador, pergunta sem correspondência, alternativa sem ordem clara, chave para outro ID ou fronteira ambígua bloqueia aquela versão.

## Correção e política de tentativas

A política já aprovada para o endpoint existente — três tentativas por usuário/versão, melhor nota, aprovação a partir de 70%, gabarito/explicação após a terceira tentativa — permanece aplicável a quizzes objetivamente avaliáveis no formato suportado. A expansão para resposta textual exige regra adicional aprovada.

- `multiple_choice`/`true_false`: correção determinística somente se os IDs das alternativas e chave forem explícitos e válidos.
- `short_answer`/`fill_code`: não pontuar por comparação aproximada, prompt de IA ou inferência. Sem regra/critério existente, bloquear o modo `server_scored`; considerar `manual_review` apenas após decisão e suporte funcional aprovados.
- `unscored_review`: não tem gabarito, não consome tentativa avaliativa e não pode satisfazer `quiz_passed`.
- Pesos só são aceitos se presentes e validados na fonte; nenhum peso presumido.

## Ambiguidades e bloqueios dos 501 pares textuais

No pacote, `format=other`, `options=[]` e `expected_answer` livre. Não há alternativas ou mecanismo de avaliação textual associado a esses dados. A conversão estrutural pode preservar pergunta, resposta e explicação em entidades separadas, mas a publicação como quiz corrigível fica bloqueada até decisão sobre correção/avaliação. Não usar o endpoint atual, não expor as respostas e não sintetizar opções.

Critérios de bloqueio: texto original sem seletor único; mais de uma resposta plausível sem rubrica; explicação que não define resposta verificável; divergência entre ID da questão/chave; pergunta sem resposta requerida usada como avaliativa; erro de hash/proveniência; formato não suportado pelo avaliador.

## Matriz editorial das cinco perguntas sem gabarito

Todas são R1–R5 de `16.3_Projeto_de_fase_Trilho_B`, no arquivo `01_projeto_trilho_b/Q01_revisao_decisoes.md`. O conteúdo não contém resposta de gabarito e nenhuma é atribuída automaticamente.

| ID de origem | ID curricular | Pergunta original (trecho) | Tratamento proposto |
|---|---|---|---|
| R1 | `f4-16-3-01-projeto-trilho-b-q01-revisao-decisoes-question-r1` | “Qualquer pessoa consegue dizer qual tipo foi escolhido, qual regra o distingue e como a evidência prova essa regra?” | Revisão sem pontuação automática; confirmar uso pedagógico. |
| R2 | `f4-16-3-01-projeto-trilho-b-q01-revisao-decisoes-question-r2` | “O índice foi proposto a partir da consulta e do plano, ou apenas adicionado por expectativa?” | Revisão sem pontuação automática; não inventar resposta. |
| R3 | `f4-16-3-01-projeto-trilho-b-q01-revisao-decisoes-question-r3` | “Os dados de exemplo são suficientes para a pergunta e permitem conferir o relatório?” | Revisão sem pontuação automática; não inventar resposta. |
| R4 | `f4-16-3-01-projeto-trilho-b-q01-revisao-decisoes-question-r4` | “As conclusões de desempenho estão limitadas às condições realmente medidas?” | Revisão sem pontuação automática; não inferir critérios de aprovação. |
| R5 | `f4-16-3-01-projeto-trilho-b-q01-revisao-decisoes-question-r5` | “O tipo só foi marcado na cobertura depois do aceite correspondente?” | Revisão sem pontuação automática; preservar relação ao aceite original. |

**Decisão pendente:** confirmar se R1–R5 são prompts de revisão formativa não avaliativa ou se têm avaliação humana associada. O contrato não acrescentará respostas, critérios nem rubrica.

## Compatibilidade e testes exigidos antes da implementação

Implementação futura deve testar correspondência exata de refs, ordem, serialização determinística, proteção do gabarito em leitura/histórico/logs, versões imutáveis, bloqueio de formatos ambíguos, revisão só após autorização e não satisfação de `quiz_passed` por `unscored_review`. O payload do aluno deve continuar incompatível com campos como `correct_index`, `expected_answer`, `accepted_answers` ou explicações protegidas.
