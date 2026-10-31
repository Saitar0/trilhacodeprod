# Beta 6.1 — integração HTTP e persistência

## Execução

Com o gate interno aprovado, o harness executou `backend/tests/test_beta6_learning_journey.py` no banco descartável MongoDB 7. Resultado: **1 passed**. O teste usa a aplicação e as rotas reais por cliente HTTP de teste; a prova de navegador complementar usa Uvicorn real no mesmo runner.

O teste preparou somente uma trilha, unidade, quiz, exercício, aluno, avaliador, escopo e submissão sintéticos no banco da execução. A fixture tornou a trilha de teste legível e publicou-a somente dentro desse banco temporário para exercitar os leitores e atividades versionadas. Nenhum conteúdo curricular original ou coleção operacional foi alterado.

## Fluxo validado por HTTP

* Requisição anônima à unidade: `401`.
* Aluno autenticado consultou conteúdo e atividade publicada de teste.
* Quiz público não continha `correct_option_id`; a tentativa manteve `published_version_id` e o backend retornou o resultado.
* Tentativa do cliente de forjar conclusão manual: `403`.
* Envio manual repetido com a mesma chave de idempotência retornou a mesma submissão, sem duplicá-la.
* Progresso refletiu quiz concluído e exercício aguardando correção.
* Editor sem escopo não listou a fila (`403`), não leu o detalhe (`404`) nem reivindicou a submissão (`404`).
* Avaliador com escopo explícito por trilha abriu critérios restritos, reivindicou e corrigiu.
* Aluno recebeu feedback autorizado; rubrica e resposta de referência continuaram ausentes.
* Outro aluno recebeu `404` ao tentar abrir submissão alheia.
* Progresso do exercício passou a concluído somente após aprovação do avaliador.

## Correção mínima

A execução revelou que `GET /api/submissions` usava a dependência `reviewer_submission_writer`, que também exigia o cabeçalho `Origin` reservado à proteção de mutações. Navegadores e clientes de leitura podem omitir esse cabeçalho; o endpoint seguro de leitura recebia `403` mesmo para avaliador autorizado. A rota agora usa `reviewer_submission_reader`, que mantém `submissions.grade` e a verificação de escopo por trilha feita pelo serviço, sem exigir um cabeçalho de mutação. Os endpoints de claim e grade continuam usando a dependência de escrita.

O teste HTTP confirmou a correção em fluxo real de rota e banco descartável. A autorização continua experimental e não substitui grants e revogação IAM C11–C15.

## O que permanece sem prova

Não foram exercitados nesta fase: expiração de sessão, usuário desativado, alteração concorrente da correção, versão inválida manipulada, escrita perdida após commit indeterminado, recuperação transacional entre submissão e projeção de progresso ou acesso a endpoints em infraestrutura operacional. A reconciliação de progresso segue não atômica como declarado na Beta 6.
