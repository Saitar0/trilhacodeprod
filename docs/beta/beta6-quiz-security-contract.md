# Beta 6 — segurança de quiz

O backend mantém o fluxo versionado de atividades existente (`/api/activities/{activity_id}/attempts` e subrotas). A definição pública de publicação fornece prompt e rótulos de alternativas, e a avaliação é feita no servidor com a definição versionada; o cliente não envia gabarito nem pontuação. A resposta HTTP de uma tentativa usa os modelos existentes.

As mudanças Beta 6 protegem principalmente a superfície compartilhada de submissões manuais: entrada estrita, resposta pública allowlisted e remoção de contexto de correção e histórico técnico. O serviço de nós também usa allowlist para blocos avaliativos legados. Nenhuma alteração expõe staging ou publica a unidade 1.1.

Limitação importante: os testes HTTP negativos de quiz (sem sessão, sessão inválida, recurso privado, versão adulterada, questão/alternativa inválida, replay e vazamento em resposta/erro) não foram executados contra MongoDB nesta fase. Testes anteriores das atividades são evidência histórica, não prova da implementação Beta 6. Não considerar DTO isolado como prova de resposta HTTP segura.

Antes de disponibilizar: executar as rotas reais no harness isolado, verificar a projeção serializada, provar que a versão da atividade é preservada e confirmar que nenhuma metadata genérica carrega gabarito. A explicação pós-tentativa permanece limitada ao contrato existente; não foi criada política de liberação diferente.
