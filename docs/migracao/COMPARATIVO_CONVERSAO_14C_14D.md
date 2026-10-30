# Comparativo da conversão de quizzes — 14C e 14D

## Totais

| Resultado | Etapa 14C | Etapa 14D | Diferença |
| --- | ---: | ---: | ---: |
| Questões com gabarito analisadas | 501 | 501 | 0 |
| Candidatas estruturais | 142 | 143 | +1 |
| Bloqueadas por alternativas/formato | 348 | 347 | -1 |
| Bloqueadas por referência de gabarito | 11 | 11 | 0 |
| Questões sem gabarito fora da contagem | 5 | 5 | 0 |

A 14C informou 359 questões bloqueadas. Na 14D, as 359 estão reconciliadas: uma foi recuperada e 358 continuam bloqueadas. Todos os 142 candidatos antigos permanecem candidatos.

## Mudança única de status

O item `f3-8-1-01-tipos-primitivos-anotacoes-02-quiz` (origem `Q1`) estava bloqueado por `DUPLICATE_OPTION_TEXT`. A regra anterior aplicava comparação sem distinção de caixa e colapsava `String` e `string`. Na fonte são textos diferentes, aparecem como código e têm IDs de alternativa diferentes; o gabarito associa uma única letra. A regra agora normaliza apenas espaços. O item virou candidato sem reescrever a questão, alternativas ou resposta.

Não há outros itens alterados de status. Os 142 candidatos continuam; os 358 casos restantes mantêm bloqueio.

## Composição dos casos restantes anteriormente bloqueados

- 314 respostas abertas sem opções, não suportadas pelo corretor objetivo.
- 23 exercícios que pedem justificativa ou produção discursiva.
- 1 pergunta sob cabeçalho de revisão.
- 8 formatos de associação/ordenação que o avaliador atual não representa; o detalhe por item é `matching_unsupported` ou `ordering_unsupported` no CSV.
- 1 múltipla escolha explicitamente rotulada sem alternativas no bloco original.
- 11 gabaritos sem associação inequívoca a uma das alternativas, mesmo com o vínculo da chave ao quiz estruturalmente correto.

Soma: 358. Nenhum desses itens recebeu alternativa ou resposta criada.

## Comparação individual por ID

[CLASSIFICACAO_QUIZZES_14D.csv](CLASSIFICACAO_QUIZZES_14D.csv) é o cruzamento completo por `(phase, quiz_ref)` para as 501 questões com gabarito. Para cada ID registra status 14C, status 14D, mudança, categoria, diagnóstico, fonte migrada, página Markdown original, linhas de questão/resposta, proveniência e hashes. O CSV não contém texto de enunciado, resposta ou explicação. A coluna `publishable` é `no` para todas as linhas.

Resumo da comparação por ID:

| Mudança | Quantidade |
| --- | ---: |
| Candidato 14C mantido como candidato | 142 |
| Bloqueado 14C recuperado como candidato | 1 |
| Bloqueado 14C que permanece bloqueado | 358 |
| Regressões de candidato anterior | 0 |

## Limites

“Candidato” significa que a questão pode ser projetada em memória para o schema de múltipla escolha e passa o corretor puro com sua chave privada. Não significa que tenha identidade interna resolvida, versão persistida ou autorização editorial para publicar. Nenhum ID foi criado no MongoDB e nenhum gabarito foi exposto em payload público ou relatório.
