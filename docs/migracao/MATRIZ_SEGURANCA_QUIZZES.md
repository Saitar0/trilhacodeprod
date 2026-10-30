# Matriz de segurança — quizzes (Etapa 13C.1A)

Escopo: revisão do backend de quizzes e endurecimento autorizado antes da integração do renderer. Não houve acesso a banco de produção, alteração do frontend, importação curricular ou mudança nas árvores e no contrato intermediário.

## Matriz de controles e riscos

| Área | Evidência no código | Verificação | Risco residual / decisão |
|---|---|---|---|
| Autenticação | `backend/routes_quizzes.py` usa `current_user` nos endpoints do aluno; `backend/security.py` valida JWT, versão do token e usuário persistido. | Testes de rota não autenticada e de sessões independentes. | Nenhum bloqueio novo identificado nesta revisão. |
| Publicação | `POST /api/admin/quizzes/{quiz_id}/versions` depende de `require("content.publish")`. | Usuário estudante recebe 403; migração 0003 é exercitada no banco descartável. | Não foram criadas rotas administrativas de leitura do gabarito. |
| Visibilidade e curso | `backend/services/quizzes.py` consulta o nó e reutiliza `assert_visible`/`assert_unlocked`; os snapshots incluem `track_id`. | Teste de quiz em trilha privada e testes de acesso existentes. | A regra de pré-requisito continua herdada da plataforma e não distingue conclusão de leitura de aprovação avaliativa. |
| Isolamento por usuário | Leituras de `quiz_progress` filtram `user_id`; índice único por `(user_id, quiz_id, version_id)`. | Testes de histórico/revisão de outro usuário e progresso isolado. | Sem acesso cruzado observado. |
| Validação de submissão | `QuizAttemptIn` recusa campos extras; correção valida questões, alternativas, duplicatas e respostas omitidas no serviço. | Testes de payload adulterado, IDs desconhecidos e tentativas inválidas. | Só múltipla escolha de resposta única é corrigível; outros formatos são rejeitados. |
| Correção e aprovação | `grade_quiz_questions` calcula no backend; nota de aprovação é comparada em precisão inteira antes do arredondamento. | Regressões de correção e política 70% preservadas. | A pontuação agregada imediata ainda permite inferência em quiz de uma questão; isso decorre da política de produto aprovada. |
| Gabarito e explicações | Snapshots privados em `quiz_versions`; respostas públicas, histórico e resultado usam schemas allowlist. Revisão confere usuário, quiz, versão e três tentativas no servidor. | Testes públicos, histórico, logs, OpenAPI e revisão antes/depois da terceira tentativa. | O renderer atual permanece incompatível e não foi alterado nesta etapa. |
| Tentativas e histórico | Um documento agregado guarda tentativas imutáveis, melhor nota e contadores; a atualização de tentativa é um `find_one_and_update` condicional. | Concorrência de duas, três e quatro submissões; históricos completos. | A semântica foi testada em MongoDB standalone; failover de replica set não foi testado. |
| Idempotência | O servidor persiste hash da chave e do payload; chave repetida com mesmo corpo retorna o resultado, corpo diferente resulta em 409. | Retry após falha simulada depois da gravação e após iniciar outro processo da API. | Uma indisponibilidade real de rede/driver não foi injetada. O cliente deve repetir a mesma chave. |
| Limitação de requisições | `backend/services/auth.py::rate_limit` fornece bucket Mongo-backed compartilhado; os endpoints de quiz usam identidade HMAC do usuário, não IP. | Limite, HTTP 429, `Retry-After`, troca de IP e retry já persistido. | Contas diferentes continuam sendo identidades diferentes; não há controle de Sybil por dispositivo. |
| Erros e logs | `backend/server.py` padroniza 429 como `rate_limited`; middleware registra rota, status, duração e usuário, não o corpo. | Testes de respostas públicas e ausência de material de correção nos logs. | Exceções inesperadas continuam registradas com traceback operacional; não foi observado conteúdo de quiz no log. |
| Progresso legado | `POST /api/progress` grava status autodeclarado e `data`; não escreve `quiz_progress`. Data de conclusão é criada no servidor, não aceita no schema. | Teste envia `passed`, nota e acertos em `data`; o quiz continua com `passed=false`, zero tentativas e revisão bloqueada. | `track_locks` ainda considera `progress.status="completed"`. Como relações não declaram se exigem leitura ou aprovação, o comportamento atual foi mantido; decisão curricular pendente abaixo. |
| Versionamento | `quiz_versions` contém snapshot imutável e hash; limite/histórico são por versão. | Teste de nova versão e preservação do histórico anterior. | A publicação/reimportação continua restrita a usuários com `content.publish`. |
| Índices e migração | `backend/migrations/0003_quiz_attempts.py` chama `ensure_quiz_indexes`; índices únicos protegem versão e agregado. | Migração repetida e dados duplicados foram testados em bancos locais descartáveis. | Duplicatas preexistentes fazem a criação do índice falhar; exige intervenção/preflight, sem exclusão automática. |

## Rate limits implementados

Os valores são tokens por usuário e categoria, com janela de 60 segundos e refill contínuo. O bucket é compartilhado entre instâncias pelo armazenamento MongoDB existente (`login_attempts` e índice TTL em `last`). Os valores são configuráveis por ambiente:

| Categoria | Padrão |
|---|---:|
| Leitura do quiz | 120/min |
| Submissões | 10/min |
| Histórico | 60/min |
| Revisão | 30/min |
| Publicação | 10/min |

Ao esgotar o bucket, a API responde `429`, `error.code="rate_limited"` e `Retry-After`. Uma repetição sequencial de uma tentativa já persistida é resolvida antes do bucket de submissão e não consome outro token. A limitação é por identidade autenticada; trocar endereço IP não a reinicia.

Variáveis: `QUIZ_READ_LIMIT_PER_MINUTE`, `QUIZ_ATTEMPT_LIMIT_PER_MINUTE`, `QUIZ_HISTORY_LIMIT_PER_MINUTE`, `QUIZ_REVIEW_LIMIT_PER_MINUTE` e `QUIZ_PUBLISH_LIMIT_PER_MINUTE`.

## Progresso e pré-requisitos

Há quatro conceitos que o sistema ainda não modela da mesma forma:

1. **Leitura autodeclarada:** `POST /api/progress` aceita status como `completed`; o endpoint não é prova de avaliação.
2. **Resultado avaliativo:** somente `quiz_progress`, escrito pelo serviço de quiz após correção no servidor, determina `passed`, tentativas e elegibilidade de revisão.
3. **Autorização curricular:** visibilidade usa as regras de acesso do curso; bloqueios usam `assert_unlocked` e o grafo de relações.
4. **Pré-requisito avaliativo:** a relação atual contém tipo, sinalizador `enforced` e nota, mas não declara “exige quiz aprovado”.

Assim, o endpoint genérico não consegue fabricar o estado autoritativo `quiz_progress.passed`; porém, pode gravar conclusão de leitura que `track_locks` usa para uma relação genérica de pré-requisito. Não foi aplicada uma regra global nova. É necessária uma decisão de produto/modelo para distinguir “conteúdo visitado/concluído” de “avaliação aprovada” nos pré-requisitos antes de prometer bloqueio avaliativo.

## Falhas parciais e limites da evidência

- A tentativa não tem reserva separada: contador e registro são alterados no mesmo documento por operação atômica. Falha antes da atualização deixa o contador inalterado; pode restar apenas o agregado inicial com zero tentativas.
- Uma falha injetada antes da escrita foi seguida por retry da mesma chave, que registrou a tentativa 1.
- Uma falha injetada depois da confirmação da escrita simulou resposta perdida. Um processo Uvicorn novo, com a mesma base descartável, recebeu o retry da mesma chave e retornou o resultado persistido sem uma segunda tentativa.
- Testes de concorrência em MongoDB standalone protegeram a cardinalidade 3. Não provam comportamento de eleição, failover ou write concern em replica set.
- O servidor local reportou MongoDB 9.0.2 standalone. O `compose.yaml` declara `mongo:7`; não foi possível executar Docker/replica set neste ambiente.
- O limite de requisições é um recurso separado da contagem de tentativas; uma falha de infraestrutura depois de consumir um token pode exigir esperar pelo refill, ainda que nenhuma tentativa avaliativa tenha sido gravada.

## Testes ignorados

Foram 37 skips na suíte unitária: um teste de contrato com Docker, ignorado porque Docker Engine não está disponível; os outros 36 pertencem ao harness G2 que exige Bash POSIX, `jq` e `flock`, fornecidos pelo CI Linux. São limitações de ambiente, não funcionalidades de quiz omitidas. Nenhum skip foi removido.
