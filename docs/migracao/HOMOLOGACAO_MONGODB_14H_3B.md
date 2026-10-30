# Homologação MongoDB — Etapa 14H.3B

## Ambiente isolado

- Sistema: Windows.
- Binário: MongoDB `mongod` instalado localmente, versão 9.0.2.
- Cliente: PyMongo assíncrono 4.17.0.
- Réplica da execução final: conjunto exclusivo `rs-14h3bfinale99f323b601a`, um membro em `127.0.0.1:54161`, autenticação/keyfile habilitados.
- URI usada em testes: `mongodb://<credencial-de-teste>@127.0.0.1:54161/admin?replicaSet=rs-14h3bfinale99f323b601a&authSource=admin`; senha não registrada.
- Standalone: processo separado autenticado em `127.0.0.1:54162`, usado apenas para comprovar falha segura sem suporte transacional.
- Ambos os processos usaram diretórios temporários exclusivos sob `%TEMP%`, sem volumes compartilhados, sem portas públicas e sem conexão a `127.0.0.1:27017`.
- Antes dos testes, foi verificado que cada porta pertencia ao PID/executável iniciado nesta execução e que `hello` identificava a topologia esperada.

O usuário administrativo foi criado exclusivamente para inicialização e limpeza do banco de teste. Os testes de RBAC criaram contas temporárias com privilégios distintos e não imprimiram credenciais. Cada teste criou e removeu seu próprio banco aleatório.

## Testes MongoDB executados

| Suíte | Resultado | Evidência |
| --- | --- | --- |
| `backend/unit_tests/test_editorial_persistence_mongodb.py` | 4 passed | transações, RBAC, índices, replay, CAS concorrente, rollback, confirmação perdida e recusa no standalone |
| `backend/unit_tests/test_typed_activity_persistence_mongodb.py` | 5 passed | regressão da persistência tipada da Etapa 14F no replica set descartável |

O teste do repositório editorial criou os índices e verificou `index_information()` no próprio MongoDB. Incluiu controles concorrentes de revisão e criação, replay idempotente simultâneo, chave divergente, duplicidade de bloco/assunto, falha injetada dentro da transação com releitura dos documentos após rollback, e perda simulada da confirmação após commit real.

No RBAC, principal de metadados sem privilégio da coleção privada conseguiu ler metadados, recebeu `Unauthorized` ao consultar payload privado diretamente e não pôde escrever nos heads. Um principal privado separado leu o payload sintético privado. A credencial de serviço editorial foi usada apenas para o repositório e testes de fixture; não representa usuário público ou permissão de aluno.

## Incidentes e correções durante homologação

As primeiras execuções revelaram defeitos no harness de teste, não no repositório: o wrapper de falhas perdia a injeção ao receber `with_options`, inspeção de índices tentava usar credencial sem `listIndexes`, e o teste de confirmação incerta não inicializava o estado local de índices. O harness foi corrigido para preservar o wrapper e consultar índices com a credencial administrativa exclusivamente no banco descartável. Após as correções, os quatro testes editoriais passaram.

O primeiro comando de inicialização usou um nome de replica set diferente do argumento `--replSet` e foi rejeitado pelo próprio `mongod`. Nenhum teste ou dado foi escrito nessa tentativa. A inicialização foi repetida com nome correspondente e passou. Credenciais ficaram em arquivo temporário com ACL restrita ao usuário da sessão; não foram registradas.

## Limitações

O conjunto de réplica tinha um único membro. A execução confirma suporte a transações e semântica de commit nesse ambiente, mas não comprova failover, eleição, recuperação de desastre, disponibilidade de cluster, topologia, rede, RBAC de produção ou compatibilidade com as configurações operacionais do Trilha Code. O standalone confirma que a implementação rejeita transações quando MongoDB não as suporta; não é evidência de operação de produção.

Os dados de teste foram sintéticos. Nenhum dos 406 blocos compartilhados, 1.001 colocações ou 15 projetos do bundle foi importado. Nenhuma rota ou serviço operacional foi conectado.

## Encerramento dos recursos

Após concluir a suíte, os dois processos MongoDB iniciados nesta etapa foram encerrados por PID, após confirmação do executável, argumentos e portas. As portas 54161 e 54162 foram verificadas fechadas. O arquivo temporário de credenciais foi sobrescrito com conteúdo vazio de credenciais e o keyfile foi zerado.

A política de execução bloqueou a remoção dos diretórios temporários, inclusive após confirmar que eram exclusivos desta etapa. Permanecem os quatro diretórios locais abaixo, contendo dados de teste sintéticos e logs; nenhum contém credenciais válidas. Os keyfiles dos dois ambientes finais foram zerados. A remoção manual desses diretórios ainda é necessária. Nenhum outro caminho foi alvo de limpeza.

- `C:\Users\Joao\AppData\Local\Temp\14h3b-22ff719257f9`
- `C:\Users\Joao\AppData\Local\Temp\14h3b-standalone-f7da37601b10`
- `C:\Users\Joao\AppData\Local\Temp\14h3b-e99f323b601a`
- `C:\Users\Joao\AppData\Local\Temp\14h3b-standalone-e647affd50a2`

O serviço MongoDB preexistente e a instância na porta 27017 não foram consultados nem alterados.
