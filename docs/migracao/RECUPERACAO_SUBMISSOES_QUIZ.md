# Recuperação de submissões de quiz

## Contrato implementado

O endpoint autenticado `POST /api/quizzes/{quiz_id}/recovery` consulta o estado do usuário autenticado para um `quiz_id` e `version_id`. Opcionalmente, recebe `idempotency_key`. A chave é transformada em SHA-256 antes da comparação com o histórico persistido; a chave em texto não é devolvida. A consulta é somente de leitura e não reserva nem consome tentativa.

| Estado | Significado |
|---|---|
| `confirmed` | A chave fornecida corresponde a uma tentativa persistida para esse usuário, quiz e versão. O resultado dessa tentativa é retornado. |
| `latest_confirmed` | Sem chave, existe uma tentativa concluída mais recente para esse usuário, quiz e versão. Isso identifica o último resultado, mas não prova que corresponda a uma intenção específica perdida no navegador. |
| `unknown` | Não foi encontrada tentativa correspondente. `may_still_be_processing: true` sinaliza que uma submissão pode ainda estar em trânsito ou não ter chegado ao servidor; o estado não afirma falha definitiva. |

O serviço atual grava contador, tentativa e resultado em uma única atualização atômica no documento de progresso. Não existe reserva persistente separada; portanto, não há estado durável `pending` que possa ser consultado. `unknown` é a resposta conservadora enquanto o resultado não aparece. Uma consulta posterior pode encontrar a tentativa já persistida.

IDs inválidos ou versões que não pertencem ao quiz retornam `404`. O endpoint usa a autenticação normal, verifica acesso ao nó, aplica o limite de consultas de histórico e consulta somente o registro associado ao usuário autenticado. A recuperação não retorna gabarito, explicações ou dados administrativos.

## Comportamento do renderer

Antes do envio, a intenção fica em `localStorage` no escopo do usuário e quiz, contendo versão, chave de idempotência e respostas selecionadas. Não contém gabarito, explicação ou nota. A leitura migra, quando possível, o formato antigo em `sessionStorage`.

Ao abrir o quiz, o renderer consulta a API. Com a intenção ainda armazenada, envia a mesma chave à recuperação e só limpa a intenção quando o servidor confirma o resultado. Se não houver armazenamento local, consulta a última tentativa concluída da versão ativa e a apresenta explicitamente como o último registro do servidor, não como prova de uma intenção perdida. Se nada for encontrado, informa o estado desconhecido e não inicia uma tentativa automaticamente. O aluno pode consultar novamente; uma nova submissão continua sendo uma ação explícita.

A revisão continua sendo solicitada ao endpoint protegido, cuja autorização é verificada pelo servidor em cada consulta. O renderer não libera respostas por inferência local e não envia aprovação ao endpoint genérico de progresso.

## Garantias e limites

- Recuperação exata após perda da resposta HTTP, reload ou reabertura do mesmo perfil usa a chave de idempotência persistida e retorna a mesma tentativa.
- Sem a chave — por exemplo, após limpar os dados do site, trocar de perfil ou dispositivo — o servidor pode informar a última tentativa concluída daquela versão, mas não consegue associá-la a uma intenção ainda não persistida ou identificar uma submissão em trânsito. O estado desconhecido permanece honesto; não se consome nova tentativa automaticamente.
- A chave de recuperação não é credencial: autenticação e escopo de usuário/quiz/versão continuam obrigatórios.
- A API não mantém um registro independente de requisições em processamento. Consultas durante a atualização atômica podem observar `unknown`; uma consulta posterior é necessária.
- Esta implementação não altera a política de tentativas, a correção, o progresso curricular, o renderer genérico ou a feature flag.

## Evidência de teste

Cobertura adicionada ao backend para recuperação exata repetida sem consumir tentativa, consulta sem chave, estado desconhecido antes da gravação, confirmação após persistência, usuário diferente e versão inválida. E2E usa API e MongoDB descartável para perda de resposta, perfil sem armazenamento anterior, reabertura, reinício da API, limite de tentativas e proteção da revisão.

