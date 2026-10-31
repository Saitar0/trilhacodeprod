# Beta 6 — exercício manual, correção e progresso

## Fluxo alterado

O aluno autenticado pode salvar rascunho ou enviar resposta nos endpoints existentes `/api/submissions/draft` e `/api/submissions/submit`. `AnswerIn` permite somente campos textuais previstos e limita payload. A rota associa o usuário autenticado no servidor, exige `progress.write` e valida origem. O envio aceita `Idempotency-Key`; a mesma chave e intenção reapresentam o mesmo resultado, enquanto reutilização divergente resulta em conflito.

O avaliador consulta `/api/submissions`, abre `/api/submissions/{id}`, inicia correção com `/claim` e registra resultado com `/grade`. As ações exigem `submissions.grade` e escopo ativo específico de trilha. Revision/CAS rejeita claim ou correção concorrentes. Resultado `returned` exige feedback; envio por si só jamais equivale a aprovação.

## Progresso e recuperação

Uma submissão salva sua revisão de atividade e contexto restrito para correção. O status muda primeiro para projeção pendente; eventos de aprendizagem têm identidade determinística e `set_progress` recebe operation ID estável. Repetir a reconciliação pode reparar evento/progresso depois de falha entre gravações. A tentativa mais recente não apaga as anteriores; alterações retornadas preservam histórico. A projeção do cliente não pode marcar como concluído um bloco com capacidade de submissão manual. Uma aprovação registrada pode prevalecer a uma projeção de cliente obsoleta.

Isso é um padrão de reconciliação por etapas, não uma transação única. A prova persistente Beta 6 não foi executada. Não alegar atomicidade ou ausência de todos os estados parciais até teste no banco descartável.

## Privacidade

Projeção de aluno retorna a própria resposta, estado, feedback liberado e resultado, mas remove rubrica/critério privado, contexto, histórico interno de avaliação, fingerprints e campos desconhecidos. Projeções de avaliador têm allowlist separada. A resposta da rota HTTP será verificada no teste persistente, ainda pendente.

## Interface e lacunas

O frontend já possui formulário de exercício, tela de estudo e painel de correção. Beta 6 garante instruções públicas no componente e reuso da chave de idempotência após falha de rede. Foram acrescentados testes do componente e typecheck/lint. A fila HTTP, feedback real, progresso após reload e fluxo de avaliador ainda não foram exercitados em browser.
