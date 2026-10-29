# Beta 7 — isolamento de testes Docker e MongoDB

## Desenho do ambiente

O harness Beta 7 reutiliza o gate da Beta 6.1 sem publicar portas. Cada execução cria identidade aleatória, imagem de runner, contêiner Mongo, runner, credenciais, banco e rede bridge interna. Mongo e runner pertencem somente à rede privada; MongoDB 7 usa WiredTiger e tmpfs para `/data/db` e `/data/configdb`. Não há bind mounts, volumes persistentes nem portas publicadas.

Antes do cliente Mongo ser construído, o host confere IDs Docker completos, nomes, labels de fase/execução/proprietário, estado dos contêineres, rede interna, membership exato, identidade da imagem, ausência de mounts/bindings e credenciais configuradas. O processo interno valida URI, database, IDs, nome/host, credencial exclusiva, gate e marcador do servidor antes de permitir os testes. Uma falha de inspeção aborta sem fallback a `localhost:27017`.

O cleanup refaz as verificações de propriedade e isolamento. Somente recursos com IDs e labels correspondentes à execução Beta 7 são elegíveis. Após a execução final, consultas por label para contêineres, redes, volumes e imagem não encontraram recursos Beta 7.

## Diagnóstico da falha anterior

O relatório Beta 6.1 identificou a incompatibilidade: o harness tentava comprovar uma porta host publicada em rede Docker `internal`; no Docker Desktop, `HostConfig.PortBindings` podia existir sem binding efetivo correspondente em `NetworkSettings.Ports`. Considerar apenas a configuração solicitada como prova seria inseguro. A solução conservou o gate e passou a usar somente comunicação pela rede interna, sem publicação de porta. Na Beta 7, uma falha adicional de decodificação de saída Docker no Windows foi resolvida no subprocesso do harness com UTF-8 e substituição de bytes inválidos, sem imprimir saída que pudesse conter credenciais.

## Suíte Docker histórica G2

O contrato antigo criava redes/contêineres sem propriedade verificável. Agora exige opt-in `TRILHACODE_RUN_G2_DOCKER_CONTRACT=1`; o default é skip. A execução usa Mongo `7.0.43` já presente (sem pull), rede bridge interna, labels completas, tmpfs para dados e configuração, sem volumes/binds/portas. A representação real do Docker Desktop foi ajustada para validar `HostConfig.Tmpfs`, pois `Mounts=[]` não enumerava tmpfs. O teste confere ownership antes da limpeza e deixa recursos preservados se qualquer identidade divergir.

Provas: guard offline **5 passed**; execução opt-in controlada **6 passed**. O teste Compose histórico foi pulado na suíte containerizada porque o Docker CLI/daemon não é disponibilizado ao runner.

## Suíte completa e materialização do checkout

A suíte unitária completa revelou que o Dockerfile E2E copiava apenas backend/frontend, enquanto testes contratuais leem manifests Beta, contratos arquiteturais, arquivos `ops/g2` e workflows. Após a primeira coleta, o runner foi ampliado para copiar apenas `docs/beta`, `docs/architecture`, `ops/g2` e `.github/workflows`, com inclusão explícita desses caminhos no dockerignore. A repetição completa passou: **386 passed, 39 skipped**. Não foram copiadas pastas de curso ou migração para a imagem. Os 221 artefatos curriculares foram copiados por lista, após conferência individual de hash, para diretório temporário dentro do runner e removidos com o ciclo do contêiner.

## Evidência final

Gate final: contexto `desktop-linux`, IDs e run ID exclusivos, network internal `true`, ports `none`, mounts persistentes `none`; credenciais aleatórias não registradas na documentação. O HTTP, o browser e Mongo operaram dentro da rede exclusiva. A verificação após limpeza retornou zero recursos Beta 7. Nenhum banco preexistente, staging, produção ou `localhost:27017` foi consultado.
