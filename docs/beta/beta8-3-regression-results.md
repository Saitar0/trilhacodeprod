# Beta 8.3 — Resultados e limites de regressão

## Harness persistente

Execução final de `ops/beta8-3-security/run-local.ps1`: **36 passed, 1 skipped** no conjunto offline; saída do harness com código 0. A prova persistente passou em MongoDB 7/replica set, API, autoridade e verifier em rede interna exclusiva. API e autoridade tinham contêineres/PIDs distintos e usuários MongoDB diferentes. O gate identificou contêiner, rede e imagem por run ID e revalidou a propriedade antes do cleanup; contêineres, rede, imagem local e armazenamento temporário foram removidos. Nenhuma URI, senha ou segredo foi incluído nesta documentação.

## Cobertura prevista no escopo

* Contrato RPC, HMAC de requisição/resposta, nonce persistido anti-replay e forma tipada fechada.
* Inicialização experimental fail-closed sem marcadores explícitos.
* W-07 PUT/POST e W-05 PUT por HTTP, com autenticação real do FastAPI e grants C12 revalidados na autoridade.
* Negativas MongoDB para tentativas diretas da API e tentativas fora do escopo concedido à autoridade.
* Sessão expirada/revogada, grant ausente/revogado antes da chamada, usuário admin sem grant, identidade no corpo HTTP e CAS concorrente.
* Preparação pelo serviço Beta 5, transição sintética pelo RPC, retry idempotente, transição concorrente, adulteração do staging e sentinelas de aprendizagem.

Marcadores persistentes: `BETA8_3_PROCESS_BOUNDARY`, `MONGODB_DENIAL`, `HTTP_W07_PUT`, `HTTP_W07_POST`, `HTTP_W05_PUT`, `INTERNAL_AUTH_REPLAY`, `CAS_CONCURRENCY`, `STAGING_RPC`, `STAGING_CONCURRENCY`, `STAGING_INTEGRITY` e `AUTH_NEGATIVES` passaram. O harness verificou sete negativas diretas MongoDB da API, três negativas fora dos privilégios da autoridade e três negativas para o usuário de leitura do staging.

## Não executado / não comprovado

* Playwright não faz parte desta composição: ela não inicia frontend nem a prévia curricular Beta 7.1. A regressão de navegador é `NOT_RUN`.
* A suíte histórica completa C8–C16/Beta 5–8.2 não foi executada. O pytest offline direcionado dentro da imagem executou somente os cinco arquivos definidos no Dockerfile. Não são contagens de toda a suíte do repositório.
* Ruff, MyPy, TypeScript, ESLint, build frontend, HTTP/TLS operacional e distribuição operacional de credenciais não foram executados.
* Não há prova de contenção de todos os writers históricos nem da identidade operacional que os executará.
* Não foram simulados encerramento real do processo autoridade após commit nem perda natural de rede; a indeterminação de resposta foi exercitada como retry da operação persistida.
* A corrida controlada entre revogação de grant e commit pela nova fronteira HTTP entre processos não foi executada. O contrato C8 e os guards são reutilizados, mas essa ordem de commit precisa de uma prova persistente nessa topologia antes de aprovar a entrega B integralmente.
* O bridge de staging foi exercitado com retry, concorrência de transição, integridade e preservação; uma revogação concorrente durante o commit do bridge não foi injetada nesta execução.

## Compatibilidade do startup comum

Sem capacidade Beta 8.3, as três rotas selecionadas mantêm `503` fail-closed. O harness testa que os módulos experimentais recusam startup sem composição explícita. Esse bloqueio evita escrita direta, mas deixa essas mutações indisponíveis no startup comum; não se testou a configuração operacional nem se comprovou que uma autoridade aprovada já esteja provisionada. Nenhuma aplicação foi executada contra configuração real ou serviço externo.
