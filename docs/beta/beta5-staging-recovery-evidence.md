# Beta 5 — evidência de preparação e recuperação

## Ambiente

MongoDB `mongo:7.0.43`, WiredTiger, standalone, contêiner dedicado com labels Beta 5, UUID, credenciais aleatórias, banco por execução, rede bridge dedicada, porta aleatória publicada somente em 127.0.0.1 e diretórios de dados em tmpfs. Nenhum volume foi montado. O harness validou inspeção Docker e identidade/servidor antes de abrir a persistência; o teste voltou a conferir a identidade antes da conexão assíncrona. A limpeza verificou o marcador e labels antes de remover contêiner e rede.

## Cenários executados

1. Converteu e validou o lote real de 10 unidades antes das gravações.
2. Injetou falha sintética depois do primeiro documento e antes do checkpoint. Resultado observado: um registro sem checkpoint; estado `RECOVERABLE` e evento técnico correspondente.
3. Retomou com o mesmo pacote. Resultado: todos os registros e checkpoints presentes, hashes conferidos, `PREPARED`.
4. Repetiu o pacote completo. Contagens de registros, checkpoints e eventos permaneceram iguais.
5. Corrompeu deliberadamente o hash de identidade do documento de job no banco sintético; o serviço lançou `StagingIdentityConflict` antes de gravar registros. O valor de job foi restaurado no teste.
6. Executou duas preparações simultâneas com serviços e clientes `AsyncMongoClient` independentes usando a mesma unidade real reduzida para prova concorrente. Resultado: um documento por ID, um checkpoint e um evento `prepared`.
7. Verificou que apenas coleções `_beta5_staging_*` e o marcador de ownership existiam; nenhuma coleção de trilha, bloco, publicação, progresso, tentativa ou submissão foi criada.

Falha simulada: exceção determinística no hook após documento, antes de checkpoint. Não foram simuladas perda de rede real, crash de processo, failover, transação MongoDB nem concorrência em múltiplos hosts. A repetição concorrente observada cobre dois clientes locais em uma única execução, não carga operacional.

## Limites

Staging parcial existe fisicamente no banco descartável até a retomada, mas não há leitor operacional acoplado. A validação não comprova ACL de produção nem proteção contra usuário que contorne o harness e acesse a coleção diretamente. A limpeza da prova eliminou o contêiner/armazenamento temporário sob propriedade verificada; não houve ação em bancos preexistentes.
