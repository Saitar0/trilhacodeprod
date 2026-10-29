# Beta 7 — segurança e integridade da aprendizagem

## Escopo

Esta prova cobre somente os serviços e rotas de aprendizagem na worktree Beta 7, com usuários sintéticos e MongoDB descartável. A autorização por trilha continua sendo o adaptador experimental da jornada; não é integração ao IAM operacional C11–C15.

## Sessões e identidade

Os testes HTTP existentes foram repetidos para expiração do access token, sessão ausente/desconhecida, usuário desativado, logout, revogação por alteração de senha e corrida entre refresh e logout. A mudança de papel é refletida em uma sessão já aberta e a permissão passa a ser negada após a despromoção.

Resultado persistente: `tests/test_auth_sessions.py` (9) e `tests/test_auth_role_refresh.py` (1) passaram dentro do banco descartável Beta 7. Tokens expirados ou revogados receberam `401`; usuário desativado não autenticou nem manteve a sessão. Isso verifica o mecanismo atual de sessões, não revogação distribuída de grants editoriais.

## Fila e escopo do avaliador

O GET da fila usa a permissão de leitura/correção e `authorized_track_ids`; o filtro `track_id` solicitado é intersectado com a lista autorizada antes da consulta. Papel nominal de admin/editor sem concessão por trilha recebeu `403`, inclusive com identificador e paginação manipulados. Na jornada Playwright, usuário sem escopo não viu a fila nem a submissão; avaliador com escopo sintético consultou e corrigiu a atividade.

O detalhe de submissão é filtrado no backend por proprietário ou avaliador com escopo. O aluno não acessa submissão de terceiro (`404`). Um teste persistente remove o grant depois da autorização inicial e antes da segunda checagem; a rota então retorna `404` e mantém a submissão sem correção.

## Concorrência e repetição da correção

`grade_submission` usa revisão CAS da submissão e estado elegível (`submitted`/`in_review`). O serviço revalida o grant imediatamente antes do CAS. O teste persistente sincroniza duas requisições HTTP de avaliadores autorizados antes da leitura concorrente e confirma um único vencedor: um `200` e um `409`, com uma decisão e um registro de histórico. Outro teste revoga o grant depois da primeira checagem e demonstra que a revalidação bloqueia a gravação. Não há lock apenas em memória.

O endpoint aceita `Idempotency-Key`. A repetição do mesmo ID, pelo mesmo avaliador e com o mesmo fingerprint, reproduz a decisão já gravada; o mesmo ID com payload divergente retorna `409`. O frontend conserva a chave enquanto o payload não muda. Sem chave, a CAS ainda evita segunda decisão sobre uma submissão já finalizada. Retenção das operações é limitada a 128 itens; após expiração dessa janela, a operação antiga é rejeitada pelo estado, sem reaplicação.

## Progresso e histórico

O serviço existente marca projeção pendente e usa eventos/projeções com identidade determinística. `test_progress_reliability.py` cobre repetição, conflito, submissões/avaliações e retomada após falha de gravação de evento; a reconciliação repetida não duplica o evento. `test_activity_attempts.py` preserva tentativas distintas. A prova não simula falha exatamente entre a gravação da decisão de correção e todas as gravações da projeção; não há transação única entre submissão, histórico, evento e progresso. A janela e a reconciliação permanecem dependência de homologação.

## Proteção de conteúdo

As respostas HTTP e a tela do aluno foram verificadas sem `correct_option_id`, rubrica restrita ou resposta de referência antes da correção. A tela do avaliador autorizado mostra material restrito; a tela do aluno recebe feedback após a decisão, sem a rubrica. Respostas e erros observados não divulgaram payload privado em cenários testados.

## Teste Docker histórico G2

O teste Docker passou a exigir `TRILHACODE_RUN_G2_DOCKER_CONTRACT=1`; por padrão, fica pulado. O opt-in cria nomes/IDs aleatórios e labels completas de fase, teste, execução e proprietário, usa somente rede bridge interna, imagem Mongo previamente presente e tmpfs em `/data/db` e `/data/configdb`, sem portas, bind mounts ou volumes persistentes. Antes da limpeza, revalida ID, nome, labels, membros da rede e opções de armazenamento; qualquer divergência preserva o recurso. Prova opt-in: 6 aprovados; prova offline do guard: 5 aprovados. A suíte normal observou 39 skips, incluindo este teste quando não optado.

## Limites

* A autorização por trilha usa grants sintéticos no banco isolado e não integra IAM operacional.
* A revogação antes da segunda checagem foi exercitada. Ainda existe uma janela entre a checagem final e o CAS: grant e submissão vivem em documentos diferentes e essa fronteira não é uma transação atômica.
* Não foi provada transação global entre correção, auditoria e progresso.
* C8–C16 continuam sem contenção global de escritores com acesso direto ao banco.
* Nenhum conteúdo foi promovido ou publicado; a autorização é somente experimental.

## Veredito da Frente A

**SEGURANÇA E CONSISTÊNCIA DA APRENDIZAGEM VALIDADAS EM AMBIENTE ISOLADO**, limitada às rotas e cenários acima. A atomicidade de revogação entre coleções e os limites operacionais continuam bloqueados para integração/homologação.
