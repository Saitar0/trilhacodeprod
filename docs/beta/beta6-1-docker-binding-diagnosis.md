# Beta 6.1 — diagnóstico do binding e isolamento

## Conclusão

A falha Beta 6 não foi evidência de uma falha do MongoDB ou dos endpoints. O harness anterior exigia simultaneamente uma rede Docker `--internal` e um binding de porta publicado no host. No Docker Desktop para Windows, o binding solicitado podia constar em `HostConfig.PortBindings` sem aparecer em `NetworkSettings.Ports`. Como o gate exigia a confirmação efetiva dos dois lados, ele corretamente parou antes de criar um cliente Mongo.

O ponto de incompatibilidade era o desenho de rede do harness: uma rede `internal` é isolada do acesso externo e não fornece o caminho host↔contêiner que o teste antigo esperava. Não removemos a verificação nem aceitamos o binding solicitado como prova.

## Solução aplicada

O harness Beta 6.1 usa uma bridge `internal` exclusiva, sem portas publicadas. O MongoDB, o runner, a API, o Vite e o Chromium ficam na mesma rede; Mongo é acessado apenas pelo nome DNS do contêiner. API, Vite e navegador rodam dentro do runner e se comunicam por loopback no namespace dele. Assim, não existe binding host a validar e não há endpoint Mongo acessível pelo host.

O Dockerfile experimental usa MongoDB `7.0.43`, rede sem saída externa, `/data/db` e `/data/configdb` em `tmpfs`, runner com `/tmp` em `tmpfs`, credenciais e JWT aleatórios por execução. A rota do navegador aborta navegações HTTPS externas. Nenhum volume, porta, URI operacional ou instância preexistente participa da prova. A construção inicial da imagem baixa dependências declaradas nos arquivos oficiais do projeto e pacotes-base; durante os testes, os serviços de aplicação permanecem sem saída externa.

## Gate antes de conexão ou escrita

O host verifica o contexto Docker, IDs completos, nomes, labels com token de propriedade da execução, rede interna, membros exatos, imagem, ausência de mounts e portas, tmpfs e variáveis previstas. Só depois gera o comprovante de gate entregue ao runner.

Dentro do runner, `validate_internal_target` rejeita configuração ausente, URI malformada, host que não seja o Mongo exclusivo, porta diferente de 27017 interna, banco que não derive do run ID, nomes/IDs divergentes, credenciais incompatíveis e opções de conexão não aprovadas. `connect_internal_verified_target` verifica versão, WiredTiger e marcador de propriedade antes de devolver o cliente. Não há fallback para `localhost:27017`.

## Evidência desta execução

O gate passou no contexto `desktop-linux`. A evidência reportou rede interna, ausência de portas publicadas e de mounts persistentes, IDs exclusivos para contêineres/rede/imagem e banco exclusivo derivado do run ID. A URI e os segredos não foram registrados.

Após HTTP, navegador e QA, a inspeção por label Beta 6.1 retornou zero contêineres, redes e imagens. A limpeza verificou IDs e ownership antes da remoção. A instância mencionada no incidente Beta 4 não foi consultada nem limpa.

## Limites

Esta prova estabelece isolamento do MongoDB usado pela execução no Docker Desktop local observado. Ela não comprova segurança de CI futuro, de outro contexto Docker, de hosts compartilhados nem de ambientes operacionais. Uma nova plataforma precisa repetir o mesmo gate e não pode substituir IDs/ownership por prefixos ou nomes.
