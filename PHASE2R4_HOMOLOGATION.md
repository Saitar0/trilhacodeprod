# Trilha Code — Fase 2R.4: Homologação visual e funcional

**Data:** 16/10/2026 (America/Sao_Paulo)
**Estado consolidado (Fase 2R.5, 16/10/2026): PARCIALMENTE HOMOLOGADO.** Os fluxos funcionais exercitados em QA e a responsividade nos viewports medidos foram aprovados nos escopos documentados. As regressões locais e os builds de produção passaram nesta fase. Ainda não há screenshots exportadas para arquivos nem inspeção HTTP detalhada por requisição; CI remoto, backup/restore operacional e staging continuam pendentes.
**Commit base:** `fbb33fbc452b83d80083fe17c93e8f3df0ee6500` (`main`). Este relatório registra evidências posteriores ao commit base; o candidato ainda não foi commitado. Nenhuma alteração existente foi descartada.

> O veredito original da Fase 2R.4.5 e as restrições descritas nas seções abaixo são registros históricos daquela etapa; os resultados consolidados atuais estão no final deste documento.

## 8. Atualização — Fase 2R.4.1: inicialização controlada

**Data:** 16/10/2026 (America/Sao_Paulo)
**SHA confirmado antes da execução:** `fbb33fbc452b83d80083fe17c93e8f3df0ee6500`.

### Segurança e isolamento revalidados

- Diretório confirmado: `C:\Users\Joao\Documents\CURSO\trilhacodeprod`.
- `docker compose --env-file .env.qa --project-name trilhacode-phase2r4-qa -f compose.qa.yaml config --quiet` terminou com sucesso.
- A URI da API aponta ao serviço Compose `mongo` na rede QA, sem banco embutido no caminho; `DB_NAME` é `trilhacode_phase2r4_qa`. A URI e credenciais não são reproduzidas aqui.
- O inventário Docker não encontrou colisão para o projeto/container QA, volumes e rede nomeados QA ou portas de host `18000`/`13000`; não havia listener local nessas portas. Mongo não tem publicação no host (`27017/tcp: null`).
- A rede `trilhacode_phase2r4_qa_internal` é interna e o container Mongo está conectado somente a ela. O volume nomeado de dados `trilhacode_phase2r4_qa_mongo_data` era inexistente antes da criação; nenhum volume/rede de outro projeto é referenciado. O Mongo criou também um volume anônimo novo em `/data/configdb`.
- A configuração do serviço API define somente Uvicorn como comando. `backend/Dockerfile` instala dependências e copia o código; não contém migração, criação de índices, seed, `resume-restores` ou inicialização do banco.

### MongoDB QA

- Criado e iniciado exclusivamente o serviço `mongo` via `compose.qa.yaml`, projeto `trilhacode-phase2r4-qa`.
- Container: `trilhacode-phase2r4-qa-mongo-1`; estado `running`, healthcheck `healthy`.
- Versão consultada: **MongoDB 7.0.43**.
- Sem porta pública no host; rede QA interna exclusiva e armazenamento QA dedicado.
- A rede, o volume nomeado de dados e o volume anônimo de configuração são recursos QA criados nesta etapa.

### Imagem da API QA

- `docker compose ... build api` concluiu com sucesso e gerou `trilhacode-phase2r4-qa-api:latest` sem iniciar o serviço API.
- Dependências instaladas conforme `requirements-dev.txt`, que inclui `requirements.txt`; versão real instalada: **PyMongo 4.18.2**.
- Verificação feita em container descartável com `--network none`, sem conexão com Mongo: `from pymongo import AsyncMongoClient` **importou com sucesso** (`AsyncMongoClient`). O container de verificação foi removido (`--rm`).
- O contexto enviado ao build foi de aproximadamente **1,35 GB**, o que tornou a transferência e exportação demoradas; o build terminou com sucesso.

### Limites e pendências

- Nenhuma migração, criação de índices, seed, `resume-restores` ou comando de gerenciamento do backend foi executado.
- API e frontend não foram iniciados. Não houve chamadas HTTP, integração funcional, QA visual nem screenshots.
- O container preexistente `trilhacodeprod-api-1` não foi alterado; a divergência da instalação PyMongo nessa imagem antiga permanece sem correção.
- A próxima homologação ainda depende de autorização própria para escritas no banco QA antes de migrações, índices, seed ou retomada de restores. Permanecem pendentes inicialização posterior da API/frontend e testes funcionais/visuais.

**Resultado desta etapa:** MongoDB QA isolado saudável; imagem da API construída; import de `AsyncMongoClient` confirmado com PyMongo 4.18.2. Nenhum push ou deploy foi feito.
**Escopo desta etapa:** leitura autorizada do estado/logs do container existente, inspeção e ajuste apenas da configuração QA e deste relatório. Nenhum serviço QA foi iniciado; nenhum container existente ou banco foi alterado.

## 1. Diagnóstico do ambiente

- `compose.yaml` define MongoDB 7 com volume persistente `mongo_data`, API publicada na porta 8000 e frontend na 3000. A API tem `restart: unless-stopped`, monta `./backend` em `/app` e, antes do Uvicorn, executa `ensure-indexes`, `migrate`, `seed` (fora de production) e `resume-restores`.
- O acesso Docker dentro da sandbox falha com `permission denied`, conforme diagnóstico anterior. Foi solicitada e obtida aprovação para uma consulta somente leitura fora da sandbox. Contexto informado: Docker Desktop 4.95.0 e Engine 29.8.2.
- Estado observado de `trilhacodeprod-api-1`: `restarting`, `RestartCount=123`, `ExitCode=1`, `OOMKilled=false`; o último processo iniciou e encerrou em cerca de um segundo. A política de restart explica a repetição, e os logs identificam a falha que encerra o processo.
- **Causa concreta do reinício:** os últimos 150 logs repetem `ImportError: cannot import name 'AsyncMongoClient' from 'pymongo'` durante a importação de `database.py`, acionada por `manage.py`. A API falha antes de iniciar Uvicorn e antes de executar migração, índices, seed ou `resume-restores`. O `requirements.txt` no SHA do workspace fixa PyMongo 4.18.2; a imagem/container existente carrega uma instalação que não exporta esse símbolo. Isso demonstra divergência entre dependência da imagem em execução e o código/dependências presentes no workspace; a versão exata instalada no container não foi consultada.
- `mongo.log` local é de 12/10/2026 e termina com shutdown normal do `mongod`; não identifica o container da API e não explica o reinício. Não foi tratado como log daquele container.
- A aplicação lê `backend/.env` via Pydantic, mas o Compose injeta explicitamente `MONGO_URL`, `DB_NAME`, `JWT_SECRET` e demais configurações da API. O Compose QA novo injeta valores próprios e não carrega esse arquivo local.

## 2. Ambiente QA exclusivo preparado

Arquivos preparados:

- [compose.qa.yaml](C:/Users/Joao/Documents/CURSO/trilhacodeprod/compose.qa.yaml)
- `.env.qa` (gerado para credenciais descartáveis, ignorado pelo Git; nenhum valor é reproduzido neste relatório)

Isolamento configurado:

- Projeto Compose: `trilhacode-phase2r4-qa`.
- MongoDB: `mongo:7`, sem porta publicada no host e acessível apenas pela rede interna QA.
- Banco: `trilhacode_phase2r4_qa`.
- Volumes nomeados exclusivos: `trilhacode_phase2r4_qa_mongo_data` e `trilhacode_phase2r4_qa_frontend_node_modules`.
- Rede interna exclusiva: `trilhacode_phase2r4_qa_internal`.
- Portas publicadas somente em loopback: API `127.0.0.1:18000`; frontend `127.0.0.1:13000`.
- Usuários e senhas da aplicação são sintéticos e exclusivos para QA. Segredo JWT e credencial raiz do Mongo são gerados localmente em `.env.qa`.
- A URI aponta apenas ao serviço Compose `mongo`; banco, nome do projeto, volumes, portas e rede têm nomes fixos próprios. Não há referência a staging, production ou ao volume `mongo_data`.

A configuração foi validada com `docker compose --env-file .env.qa --project-name trilhacode-phase2r4-qa -f compose.qa.yaml config --quiet` (exit 0). `.env.qa` contém somente as três chaves esperadas; valores não foram reproduzidos. A consulta de colisões não encontrou container do projeto QA nem containers publicando `18000`/`13000`; os dois volumes QA e a rede QA ainda não existem. A consulta local de listeners TCP também não encontrou processos escutando nessas portas.

O isolamento revisado é: Mongo sem porta publicada; API/frontend publicados apenas em `127.0.0.1`; rede interna, banco (`trilhacode_phase2r4_qa`) e volumes QA com nomes exclusivos. O `compose.yaml` de desenvolvimento usa `mongo_data`; o Compose QA não referencia esse volume nem banco de staging/produção. A verificação estática e inventário confirmam ausência de colisões atuais, mas os recursos só serão criados numa etapa futura autorizada.

### Bootstrap controlado

Na revisão inicial, `compose.qa.yaml` encadeava `preflight-indexes` → `migrate` → `preflight-indexes` → `ensure-indexes` → `preflight-indexes` → `seed` → `resume-restores` antes do Uvicorn. Ajustei **somente esse arquivo QA**: a API inicia diretamente com Uvicorn e não executa operações de banco automaticamente. Nenhum arquivo de produção/desenvolvimento foi alterado. Plano, não executado:

1. Confirmar novamente projeto/portas e iniciar apenas o Mongo QA com `docker compose --env-file .env.qa --project-name trilhacode-phase2r4-qa -f compose.qa.yaml up -d mongo`.
2. Construir a imagem da API se necessário e executar o preflight de leitura isolado: `docker compose --env-file .env.qa --project-name trilhacode-phase2r4-qa -f compose.qa.yaml run --rm --no-deps api python -m manage preflight-indexes`.
3. **Após autorização explícita para escritas no banco descartável QA**, executar um comando por vez, sempre via `docker compose ... run --rm --no-deps api <comando>` e confirmando antes o destino `DB_NAME`/`MONGO_URL`: `python -m manage migrate`; preflight; `python -m manage ensure-indexes`; preflight; `python -m manage seed`; `python -m manage resume-restores`.
4. Iniciar API e frontend; o comando da API é apenas Uvicorn. Fazer QA funcional e visual após ambos ficarem saudáveis.

Migrações, `ensure-indexes`, seed e `resume-restores` alteram o Mongo e exigem autorização. `preflight-indexes` é somente leitura. A inicialização do Mongo, o build das imagens e a subida dos serviços também não foram autorizados nesta etapa e ficam pendentes de próximo ok. Nenhuma operação foi executada.

## 3. Inicialização e integração

| Verificação | Resultado |
|---|---|
| Build das imagens | API QA construída; frontend não construído |
| Inicialização Mongo/API/frontend | Mongo QA iniciado e saudável; API/frontend não iniciados |
| Logs dos serviços | Mongo healthcheck saudável; API/frontend sem execução ou logs |
| `GET /health` | Não executado |
| `GET /ready` (Mongo + schema 2) | Não executado |
| Comunicação frontend/API e CORS | Não executada |
| Login/autenticação e cookies | Não executados |
| Persistência de dados | Não executada |
| Estabilidade da API e erros HTTP | Não avaliadas em runtime |

A implementação declara `/health` como verificação de processo e `/ready` como verificação de conexão ao Mongo e versão de migração mínima 2. Isso foi confirmado por leitura do código, não por chamadas HTTP.

## 4. QA visual e funcional

**Navegador:** não acessível para esta homologação, pois o frontend QA não pôde ser iniciado. Não foram capturadas screenshots. A inspeção visual permanece pendente; não há aprovação visual.

| Fluxo | 1440 px | 1024 px | 390 px | 360 px |
|---|---|---|---|---|
| Login, cadastro, erros e logout | Não executado | Não executado | Não executado | Não executado |
| Dashboard do aluno | Não executado | Não executado | Não executado | Não executado |
| Perfil | Não executado | Não executado | Não executado | Não executado |
| Lista, busca e filtros de trilhas | Não executado | Não executado | Não executado | Não executado |
| Visualizador e navegação entre blocos | Não executado | Não executado | Não executado | Não executado |
| Editor de trilhas e blocos | Não executado | Não executado | Não executado | Não executado |
| Submissões e feedback | Não executado | Não executado | Não executado | Não executado |
| Painel administrativo, tabelas e filtros | Não executado | Não executado | Não executado | Não executado |
| Modais, menus e dropdowns; teclado | Não executado | Não executado | Não executado | Não executado |
| Scroll, layout, estados vazios/carregamento/erro | Não executado | Não executado | Não executado | Não executado |
| Console JavaScript e requests 4xx/5xx | Não executado | Não executado | Não executado | Não executado |

**Evidências reais de tela:** nenhuma. Nenhum fluxo foi declarado aprovado sem exercício observável.

## 5. Migrações e índices

Revisão estática de `DEPLOY.md`, `backend/migrations/`, `backend/manage.py` e `backend/indexes.py`:

- Duas migrações esperadas: `0001_legacy_snapshots` e `0002_block_submission_capabilities`; versão esperada do schema: 2.
- `backend/indexes.py` define 23 especificações de índice.
- `preflight-indexes` é somente leitura e verifica compatibilidade/duplicidades; `ensure-indexes` chama `create_index` e altera o banco.
- O procedimento documentado separa preflight, migração, preflight pós-migração, criação de índices e preflight final.
- O Compose de desenvolvimento atual não segue esse fluxo controlado: chama `ensure-indexes` antes de `migrate` e não executa preflight. A configuração QA foi ajustada para não executar bootstrap automático; a sequência documentada será chamada explicitamente somente depois de autorizado.
- Nenhum preflight, migração, criação de índice, seed ou retomada de restores foi executado nesta sessão, em qualquer banco.

## 6. Erros, correções e regressão

- **Erro observado no container existente:** `AsyncMongoClient` ausente no pacote `pymongo` instalado; os logs confirmam que isso causa a saída 1 e o ciclo de reinício.
- **Acesso Docker:** dentro da sandbox segue negado; fora dela, após aprovação, as consultas de leitura ao estado/logs e inventário de colisões foram concluídas.
- **Correção reproduzida no app:** nenhuma. Não foi possível reproduzir defeito de aplicação sem runtime.
- **Preparação realizada:** configuração QA separada, credenciais sintéticas locais, alvo Mongo/DB/volumes/rede/portas exclusivos e API sem bootstrap automático. Validação sintática Compose aprovada; nada foi iniciado.
- **Regressão local:** não executada. O contexto do solicitante informa 63 testes backend aprovados anteriormente; essa evidência não foi reexecutada nem verificada para este relatório. Nenhuma alegação de regressão aprovada é feita aqui.
- Builds, testes frontend, testes de API, acessibilidade, persistência e screenshots seguem pendentes.

## 7. Pendências para staging

1. Corrigir a divergência de dependência do container existente por fluxo próprio; ele não foi modificado nem reiniciado nesta etapa.
2. Antes de outra etapa, revalidar portas/nomes; Mongo QA e imagem da API já foram criados nesta etapa controlada.
3. Obter autorização explícita para cada operação de escrita no Mongo QA (migrações, criação de índices, seed e retomada de restores); confirmar o alvo QA antes de cada comando e nunca apontar para bancos preexistentes.
4. Executar o bootstrap controlado, iniciar API/frontend e registrar logs e resultados de `/health` e `/ready`.
5. Exercitar fluxos funcionais, CORS, auth, persistência e erros; corrigir somente defeitos reproduzidos no ambiente isolado.
6. Fazer inspeção visual real em 1440, 1024, 390 e 360 px, registrar navegador/versão, console/rede e anexar screenshots identificados pelo SHA.
7. Reexecutar regressões necessárias no SHA exato e registrar resultados verificáveis.
8. Para staging, seguir `DEPLOY.md`: ambiente/DB confirmados, backup e janela operacional, preflights antes e depois das escritas e aprovação do responsável. Nenhuma migração/índice em banco existente ocorreu nesta sessão.

## Veredito

**BLOQUEADO para homologação funcional/visual.** O SHA no workspace foi revisado estaticamente. Nesta atualização, o MongoDB QA foi iniciado e ficou saudável em armazenamento/rede exclusivos; a imagem da API QA foi construída e o import de `AsyncMongoClient` foi confirmado. API e frontend não foram iniciados; nenhuma migração, criação de índices, seed ou retomada de restores foi executada. A causa observada no container antigo (`AsyncMongoClient` ausente na instalação ali carregada) continua sem correção nesse container. A próxima etapa requer autorização explícita antes de qualquer escrita no banco QA; integração, regressão e inspeção visual permanecem pendentes.

## 9. Atualização — Fase 2R.4.2: preparação controlada do banco QA

**Data:** 16/10/2026 (America/Sao_Paulo)
**Resultado desta fase:** **APROVADO para a preparação do banco QA**. Este resultado não aprova a execução da API/frontend nem a homologação funcional/visual.

### SHA e working tree

- Repositório confirmado: `C:\Users\Joao\Documents\CURSO\trilhacodeprod`.
- `HEAD`: `fbb33fbc452b83d80083fe17c93e8f3df0ee6500`; o commit não mudou durante a preparação.
- Estado final: `backend/indexes.py` modificado para corrigir o preflight; `PHASE2R4_HOMOLOGATION.md` e `compose.qa.yaml` permanecem não rastreados. `.env.qa` não foi exibido nem reproduzido. Nenhuma alteração foi descartada.

### Isolamento reconfirmado

- Compose validado com `docker compose --env-file .env.qa --project-name trilhacode-phase2r4-qa -f compose.qa.yaml config --quiet`.
- O único container persistente do projeto QA observado foi `trilhacode-phase2r4-qa-mongo-1`, saudável, MongoDB **7.0.43**, projeto `trilhacode-phase2r4-qa`.
- Mongo sem publicação de porta no host; conectado somente a `trilhacode_phase2r4_qa_internal`. O volume `/data/db` é `trilhacode_phase2r4_qa_mongo_data`; `/data/configdb` usa volume anônimo próprio. Nenhum volume de outro projeto é montado.
- Configuração efetiva da API aponta para o host de serviço `mongo`, banco `trilhacode_phase2r4_qa`, e compartilha a rede `qa_internal`. URI/credenciais não foram impressas.
- Portas de host `18000` e `13000` estavam livres; Mongo não define portas publicadas. A API QA está configurada para iniciar somente Uvicorn, sem migrations, índices, seed ou `resume-restores` automáticos.
- Os comandos de gestão foram executados como containers descartáveis `api` com `run --rm --no-deps`; API e frontend não foram iniciados. O inventário final manteve apenas o Mongo persistente do projeto QA. Containers, volumes e bancos de outros projetos não foram modificados.

### Revisão das operações e migrações

- `manage.py` separa `preflight-indexes`, `migrate`, `ensure-indexes`, `seed` e `resume-restores`; nenhuma operação chama `resume_restore_jobs` implicitamente. `resume-restores` **não foi executado**.
- A migração `0001_legacy_snapshots` percorre `track_versions` e transforma snapshots embutidos em chunks. O banco estava inicialmente sem coleções/documentos, portanto não havia snapshots legados para transformar.
- A migração `0002_block_submission_capabilities` atualiza block types existentes e registra marcador auxiliar. Não havia block types preexistentes para modificar.
- `python -m manage migrate` terminou com exit code 0. Foram registrados `0001_legacy_snapshots` (versão 1) e `0002_block_submission_capabilities` (versão 2). A versão máxima do schema é **2**; snapshots legados remanescentes: 0.

### Preflights e índices

1. Preflight inicial: `python -m manage preflight-indexes`, exit code 0; **23 AUSENTE**, zero `CONFLITO`, zero `DUPLICATAS`. Nenhuma escrita ocorreu.
2. Primeiro preflight pós-migração: falhou antes de produzir findings por falta de `await` em `AsyncCollection.list_indexes`; não alterou o banco. Corrigida somente a chamada assíncrona em `backend/indexes.py`, conforme a API oficial do [PyMongo AsyncCollection 4.18](https://pymongo.readthedocs.io/en/4.18.0/api/pymongo/asynchronous/collection.html). Repetição: exit code 0, **23 AUSENTE**, sem conflitos ou duplicatas.
3. `python -m manage ensure-indexes`: exit code 0; percorreu as **23 especificações** de `backend/indexes.py`.
4. Primeiro preflight pós-criação: marcou falsamente nomes compostos como conflito e o índice textual como ausente. Inspeção read-only confirmou que os 23 índices armazenados eram compatíveis: MongoDB usa `_` nos nomes compostos e representa o índice textual por `_fts`/`weights`. Corrigida somente a comparação no preflight; nenhuma definição de índice foi alterada ou removida.
5. Preflight repetido após a correção e preflight final pós-seed: exit code 0 em ambos; **23/23 `OK`**, zero `AUSENTE`, `CONFLITO` ou `DUPLICATAS`. Foram confirmadas as opções de unicidade e os filtros parciais previstos, incluindo `one_pending_review` e `one_running_restore`.

### Seed sintético

- `python -m manage seed` foi executado uma única vez no banco QA e terminou com exit code 0.
- Dados criados: **3 usuários** (1 admin, 1 editor, 1 student), **15 taxonomias**, **15 block types**, **3 tags**, **1 trilha demo**, **17 nós**, **24 blocos de conteúdo** e **6 relações**.
- Os três usuários usam domínio sintético `example.invalid`, têm perfil inicial e `is_demo=true`. A trilha, os 17 nós e os 24 blocos também estão marcados como demo. Os papéis correspondem à política de permissões em `backend/constants.py`.
- Zero registros não-demo em usuários, trilhas, nós e blocos. Coleções operacionais como submissions, progresso, eventos, notas, reviews e restore jobs permaneceram vazias; havia zero jobs de restore.
- O seed não faz chamadas externas nem lê dados reais; nenhum segredo/hash foi impresso nos logs. A base estava vazia antes do seed.

### Validação final e pendências

- MongoDB: `running`/`healthy`, versão 7.0.43; schema 2; 23 índices compatíveis; preflight final sem duplicatas ou conflitos.
- Nenhum comando `resume-restores`, deploy, push ou publicação foi realizado. Nenhum container, volume ou banco externo foi alterado.
- Permanecem pendentes para a etapa seguinte: iniciar API e frontend QA, validar `/health` e `/ready`, integração e fluxos funcionais, inspeção visual e screenshots. Esta fase encerra antes de iniciar esses serviços.

**Comandos de gestão executados no Compose QA, sem segredos:** `python -m manage preflight-indexes` (inicial, pós-migração, pós-índices e final, além das repetições após correções), `python -m manage migrate`, `python -m manage ensure-indexes` e `python -m manage seed`.

## 10. Atualização — Fase 2R.4.3: homologação funcional e visual

**Data:** 16/10/2026 (America/Sao_Paulo)
**SHA em `HEAD`:** `fbb33fbc452b83d80083fe17c93e8f3df0ee6500`. Nenhum commit ou push foi realizado.
**Veredito desta etapa: BLOQUEADO.** API e frontend QA iniciaram e respondem dentro da rede; o Engine não publicou as portas no host, impedindo o navegador e a aprovação visual.

### Verificações prévias e isolamento

- Revalidado o projeto Compose `trilhacode-phase2r4-qa`, a rede `trilhacode_phase2r4_qa_internal` (`bridge`, `Internal=true`), o volume de dados exclusivo `trilhacode_phase2r4_qa_mongo_data`, banco `trilhacode_phase2r4_qa` e ausência de portas publicadas no Mongo.
- Mongo permaneceu `running`/`healthy`, versão 7.0.43. Consulta final read-only confirmou schema versão 2 e 42 índices totais (23 da aplicação e um `_id` por coleção).
- As portas 18000 e 13000 estavam livres antes do início. O Compose renderiza API `127.0.0.1:18000:8000`, frontend `127.0.0.1:13000:3000`, `CORS_ORIGINS=http://localhost:13000` e `VITE_BACKEND_URL=http://localhost:18000`.
- A API inicia por Uvicorn. O lifespan chama apenas `check_schema_version()` e fecha o cliente Mongo; nenhum bootstrap automático de migração, índices, seed ou `resume-restores` foi encontrado. Nesta etapa não foram executados `migrate`, `ensure-indexes`, `seed` nem `resume-restores` contra o banco QA. O único comando direto de gestão foi o preflight read-only.
- Não foram modificados containers, bancos, volumes ou redes de outros projetos. Builds e operações de serviço foram direcionados ao projeto QA; não houve deploy, publicação, push ou commit.

### Correção de índices e testes

- `ruff check` passou para `backend/indexes.py`, `backend/tests/test_integrity_concurrency.py` e `backend/tests/test_pymongo_async.py`.
- `py_compile` passou para esses arquivos. Uma tentativa inicial de compilar todo `backend/` foi interrompida porque varria também o ambiente virtual; os arquivos relevantes foram compilados diretamente depois.
- A primeira execução completa, no banco aleatório `test_*` criado pelo fixture, teve 62 aprovados e 1 falha. A inspeção confirmou que PyMongo 4.18.2 implementa `AsyncCollection.list_indexes` como coroutine; o mock do teste era síncrono. Corrigi somente o mock para corresponder ao driver. A suíte completa repetida passou: **63/63 em 12,53 s**. O fixture criou, migrou, indexou e descartou exclusivamente o banco temporário `test_*`; não apontou ao banco QA preparado.
- O preflight real read-only no banco QA confirmou **23/23 OK**, zero ausentes, conflitos ou duplicatas. Nenhuma especificação dos 23 índices foi alterada nesta etapa.
- O build da imagem API foi tentado, mas ficou sem progresso na etapa `COPY . .` após transferir cerca de 8,5 MB; foi interrompido. O serviço iniciou da imagem já existente, com `./backend:/app` montado e, portanto, usando o `indexes.py` local corrigido. A imagem API não foi atualizada.

### API QA e integração

- Serviço `api`: `running`/`healthy`, `RestartCount=0` após 17 minutos observados. Logs mostram Uvicorn iniciado sem `ImportError` e sem operação automática de manutenção.
- Healthcheck interno `GET /health`: **200**. `GET /ready` executado de dentro do container: **200**, `{"ok":true,"migration_version":2}`.
- Chamadas do host a `http://127.0.0.1:18000/health` e `/ready` foram recusadas. `HostConfig.PortBindings` contém o mapeamento solicitado, mas `NetworkSettings.Ports` permaneceu vazio (`8000/tcp: []`); `docker ps` não mostrou porta publicada. A API está conectada somente à rede QA interna sem gateway. Não alterei a topologia para contornar isso, pois enfraqueceria o isolamento.
- Preflight CORS interno com `Origin: http://localhost:13000` e método POST retornou 200, `Access-Control-Allow-Origin: http://localhost:13000` e `Access-Control-Allow-Credentials: true`. A interação real navegador→API permanece sem verificação.
- Um login direto com a conta seed `admin.qa@example.invalid` retornou 422 porque `EmailStr` rejeita domínios especiais `.invalid` antes da autenticação. Não alterei a validação nem a seed, e não rodei seed novamente.
- Pelo fluxo normal de cadastro foi criada uma conta de estudante sintética em domínio reservado `example.com`; nenhum serviço de email foi chamado. Com ela, a API retornou: cadastro 200 com cookies `access_token`/`refresh_token`; `/api/auth/me` 200; perfil 200; logout 200; `/api/auth/me` após logout 401.
- Leitura da conta sintética: lista de trilhas 200 (1 item), árvore de conteúdo 200 (17 nós), busca 200 (9 resultados), submissões do aluno 200 (lista vazia). Dashboard `/api/progress/overview` respondeu 200; a primeira chamada fria levou 5,14 s e ultrapassou o timeout de 5 s do cliente de teste, enquanto a repetição após aquecimento levou cerca de 0,06 s. Registrar como ressalva de latência fria.
- Painel, permissões administrativas, cadastro/login dos demais usuários seed, perfil com atualização, editor, blocos, submissão/feedback com gravação e filtros administrativos não foram homologados.

### Frontend e QA visual

- Build da imagem frontend concluiu com sucesso: Node 20 Alpine, `npm ci` instalou 677 pacotes e reportou zero vulnerabilidades. O processo teve avisos de dependências declaradas deprecated.
- O container frontend ficou transitoriamente em estado `Created`; a tentativa seguinte reportou conflito de nome. A inspeção final encontrou esse container QA, que foi iniciado diretamente pelo nome exato. Vite 6.4.4 informa `ready` e responde internamente em 3000. GET interno `/` e `/src/index.tsx` retornou 200; `http://api:8000/health` da rede QA retornou 200. O ambiente do frontend contém `VITE_BACKEND_URL=http://localhost:18000`. Os logs de Vite mostram um aviso de plugin PostCSS que não passou a opção `from`; não houve browser para avaliar o impacto visual.
- O browser Codex In-app tentou abrir `http://127.0.0.1:13000` após o frontend estar running e recebeu `net::ERR_CONNECTION_REFUSED`. API e frontend mostram bindings configurados em `HostConfig`, mas `NetworkSettings.Ports` permanece vazio (`8000/tcp: []` e `3000/tcp: []`); o host não consegue abrir 18000/13000. O frontend alcança a API pelo DNS interno, mas o JavaScript no browser usaria a URL localhost configurada; essa chamada não foi observada.
- Não foi possível confirmar visualmente o carregamento React, erros JavaScript, todos os recursos estáticos, navegação por teclado ou aparência responsiva. Nenhum fluxo visual foi declarado aprovado e nenhuma screenshot real foi capturada. Versão do browser não disponível; erro de rede observado foi `ERR_CONNECTION_REFUSED`.

| Largura | Resultado visual | Screenshot | Console/rede do navegador |
|---:|---|---|---|
| 1440 px | Não executado — frontend indisponível no host | Nenhuma | Não coletado |
| 1024 px | Não executado — frontend indisponível no host | Nenhuma | Não coletado |
| 390 px | Não executado — frontend indisponível no host | Nenhuma | Não coletado |
| 360 px | Não executado — frontend indisponível no host | Nenhuma | Não coletado |

### Estado final e pendências

- Containers deste projeto: Mongo QA `healthy`; API QA `healthy` sem reinícios; frontend `running` com Vite pronto internamente, sem healthcheck Compose e sem porta publicada no host. Nenhuma migração, criação de índices, seed ou retomada de restores foi executada nesta etapa.
- Working tree: `backend/indexes.py` continua modificado; `backend/tests/test_integrity_concurrency.py` recebeu apenas a correção do mock assíncrono; `compose.qa.yaml` e este relatório seguem não rastreados. O SHA permanece o acima.
- Para encerrar a Fase 2R.4, resolver a publicação da porta respeitando a rede interna; então repetir health/ready pelo host, autenticação/admin com dados sintéticos aceitos, submissões, editor e painel; executar QA real no navegador em 1440/1024/390/360 px e anexar screenshots, logs de console/rede. Reavaliar os endereços seed `.invalid` e o tempo da primeira chamada do dashboard sem contornar as validações durante esta homologação.

## 11. Atualização — Fase 2R.4.4: diagnóstico da publicação de portas

**Data:** 16/10/2026 (America/Sao_Paulo)
**SHA em `HEAD`:** `fbb33fbc452b83d80083fe17c93e8f3df0ee6500` (sem commit/push).

### Diagnóstico read-only

- Compose renderizado com `--env-file .env.qa --project-name trilhacode-phase2r4-qa -f compose.qa.yaml config --quiet`: sucesso. Mongo, API e frontend estavam ligados somente à `trilhacode_phase2r4_qa_internal`; ela usa driver `bridge`, `Internal=true`.
- Inspeção dos endpoints dos três containers: gateway vazio em cada endpoint. O IPAM da rede contém uma configuração de gateway, mas os endpoints Docker dos containers não receberam gateway.
- `HostConfig.PortBindings` solicitava API `127.0.0.1:18000→8000` e frontend `127.0.0.1:13000→3000`. `NetworkSettings.Ports` era `8000/tcp: []` e `3000/tcp: []`; `docker ps` mostrava somente as portas internas. `docker compose port` respondeu `:0` para ambos.
- O Mongo não tem binding (`HostConfig.PortBindings={}`; `27017/tcp: null`) e permanece exclusivamente em `qa_internal`, com `trilhacode_phase2r4_qa_mongo_data` montado em `/data/db` e volume anônimo próprio em `/data/configdb`.
- API e frontend estavam `running`; API e Mongo `healthy`. De dentro da API, `mongo` resolveu para `172.20.0.2`; `/health` e `/ready` responderam 200. As portas 13000 e 18000 recusaram conexão do Windows. Não foi observado listener conflitante no Compose; os bindings declarados no arquivo e no `HostConfig` coincidem. O impedimento confirmado é a ausência de conectividade da rede interna ao host junto com a ausência de bindings efetivos no Engine, não um erro no mapeamento de porta nem falha de processo.
- A API da aplicação estava configurada para usar `http://localhost:18000`; CORS permitia `http://localhost:13000`. Portanto, para esta configuração, o browser deve abrir `http://localhost:13000`. Usar `127.0.0.1` para a página resultaria em origem diferente da origem CORS configurada.
- Referência técnica consultada: documentação oficial Docker Compose sobre redes internas/híbridas e documentação oficial de publicação de portas.

### Topologia validada estaticamente e mudança preparada

- Rede `qa_internal`: bridge interna exclusiva, Mongo somente nela e API ligada nela para manter DNS `mongo`.
- Rede `qa_access`: nova bridge regular, nome exclusivo `trilhacode_phase2r4_qa_access`; API e frontend ligados nela, Mongo fora dela.
- Publicação permanece somente em loopback: API `127.0.0.1:18000:8000`, frontend `127.0.0.1:13000:3000`; a URL do browser continua `http://localhost:18000`.
- `docker compose ... config --quiet` e inspeção dos campos renderizados confirmaram as redes por serviço, `Internal=true` apenas em `qa_internal`, `driver=bridge` nas duas redes e bindings loopback sem alterações. Resolução de `mongo` e HTTP readiness foram comprovados na configuração anterior; a topologia nova ainda precisa de validação runtime.
- Nenhum container ou rede foi recriado durante o diagnóstico. Containers QA confirmados por nome: `trilhacode-phase2r4-qa-api-1`, `trilhacode-phase2r4-qa-frontend-1` e `trilhacode-phase2r4-qa-mongo-1`.
- Recriação aprovada na ferramenta e executada com `docker compose --env-file .env.qa --project-name trilhacode-phase2r4-qa -f compose.qa.yaml up -d --no-deps --force-recreate api frontend`. Na primeira tentativa, o Compose tentou substituir também a rede interna devido à declaração redundante `driver: bridge`; removeu-se apenas essa declaração (o driver bridge é o padrão), mantendo `internal: true`. A repetição terminou com API saudável e frontend iniciado.

### Runtime após a correção

- Rede `trilhacode_phase2r4_qa_internal`: `bridge`, `Internal=true`; o endpoint Mongo não tem gateway e `/proc/net/route` mostra somente a rota local `172.20.0.0/16`, sem rota default. O IPAM da rede informa `172.20.0.1`, mas esse valor não aparece como rota default no Mongo. Mongo está somente nela. API também está nela, com IP `172.20.0.3`; `mongo` resolve para `172.20.0.2`.
- Rede nova `trilhacode_phase2r4_qa_access`: `bridge`, `Internal=false`, gateway `172.25.0.1`. API (`172.25.0.2`) e frontend (`172.25.0.3`) estão ligados nela. A tabela de rotas da API mostra a rota default via `172.25.0.1` e a rota direta para `172.20.0.0/16`; Mongo não aparece como endpoint da rede de acesso.
- Mongo `trilhacode-phase2r4-qa-mongo-1` manteve ID `583af2d9011cf1b232829723c6723338f66c077ecdecb6892b78a1125441efab`, `StartedAt` original, estado `running`/`healthy`, e os mesmos volumes de `/data/db` e `/data/configdb`. Não foi parado, recriado ou removido.
- API e frontend foram recriados uma vez na tentativa final: `trilhacode-phase2r4-qa-api-1` (ID novo; `running`/`healthy`, `RestartCount=0`) e `trilhacode-phase2r4-qa-frontend-1` (ID novo; `running`, Vite 6.4.4 pronto).
- `docker ps` mostrou `127.0.0.1:18000->8000/tcp` e `127.0.0.1:13000->3000/tcp`. `HostConfig.PortBindings` e `NetworkSettings.Ports` coincidem nos dois serviços. `Test-NetConnection` retornou `True` para as duas portas.
- Pelo Windows: `http://localhost:18000/health` **200**; `http://localhost:18000/ready` **200**, `{"ok":true,"migration_version":2}`; `http://localhost:13000/` **200**. A API continuou saudável depois das chamadas.
- CORS: preflight `OPTIONS` de `http://localhost:13000` para POST retornou 200, `Access-Control-Allow-Origin: http://localhost:13000`, `Access-Control-Allow-Credentials: true` e métodos GET/POST/PUT/PATCH/DELETE/OPTIONS.

### Navegador e smoke test inicial

- Navegador real: Codex In-app Browser, origem `http://localhost:13000`. A raiz `/` redireciona ao login; escolhemos `localhost`, igual à URL de API no `VITE_BACKEND_URL` (`http://localhost:18000`). Não usamos `127.0.0.1` na barra, evitando divergência da origem CORS `http://localhost:13000` e de cookies host-only.
- Home/login: renderizado em 1440×900 e 390×844. Cadastro: renderizado em ambas as larguras. Login e cadastro sem dados acionaram a validação HTML nativa “Preencha este campo.”. `documentElement.scrollWidth` e `body.scrollWidth` foram iguais à viewport em 1440 e 390; sem overflow horizontal nestas telas.
- Requisições reais do app no browser chegaram à API em `localhost:18000`: GET `/api/auth/me` e POST `/api/auth/refresh` retornaram 401 por ausência de sessão/cookies; isso confirma conectividade browser→API. Depois, o usuário forneceu credenciais para testar a conta QA; um único POST `/api/auth/login` chegou ao backend e retornou 401 (a tela exibiu “Request failed with status code 401”). Não repetimos a tentativa nem reproduzimos a senha no relatório. Como o browser exibiu o status HTTP retornado pela API, não houve bloqueio CORS nessa chamada. O cadastro não foi submetido.
- Screenshots reais das telas login/cadastro em 1440×900 e 390×844 foram capturadas no navegador e exibidas nesta conversa. Não foram exportadas como arquivos locais. Nenhum erro JavaScript foi visível no estado de tela; a coleta dedicada do console do browser não ficou disponível. Os logs da API não mostram falha de CORS, e as chamadas de autenticação anônimas chegaram ao backend.
- Dashboard, lista de trilhas e visualizador de conteúdo não foram acessados porque requerem uma sessão autenticada. O relatório 2R.4.3 não contém o email/senha da conta sintética já criada; as credenciais fornecidas nesta continuação não foram aceitas pelo banco QA. Não usamos usuários seed `.invalid`, não alteramos validação de e-mail e não criamos outra conta. O browser está aberto na tela de login; para continuar os fluxos autenticados, é necessário usar as credenciais corretas de uma conta que exista nesse banco QA ou autorizar cadastro sintético novo.

### Resultado da correção

**Veredito de rede: CORRIGIDO e runtime verificado.** A topologia de duas redes preserva Mongo no segmento interno e publica API/frontend em loopback pela bridge QA de acesso. Portas e endpoints são alcançáveis pelo Windows, e o browser real carrega o app e envia chamadas à API; CORS foi confirmado. O smoke test visual inicial confirmou login/cadastro em 1440 e 390 px. O login autenticado retornou 401 para as credenciais tentadas; dashboard, trilhas e conteúdo permanecem pendentes de uma conta válida no banco QA. A latência fria de dashboard observada em 2R.4.3 também permanece como pendência de desempenho. Nenhum banco/volume externo, deploy, publicação, commit ou push foi alterado/executado.

## 12. Atualização — Fase 2R.4.5: homologação autenticada (checkpoint de sessão)

**Data:** 16/10/2026 (America/Sao_Paulo)
**Projeto QA:** `trilhacode-phase2r4-qa`
**Veredito desta etapa: BLOQUEADO para fluxos autenticados — aguardando autenticação manual do usuário.** O frontend respondeu em `http://localhost:13000` e abriu `/login`; o navegador não tinha abas abertas antes da navegação e a aplicação exibiu o formulário Entrar. Portanto, não havia sessão autenticada disponível para verificar.

### Evidências desta sessão

- A página real `/login` foi capturada em **1440×900, 1024×900, 390×844 e 360×844**. As imagens foram apresentadas nesta sessão de homologação. Não foram exportadas como arquivos locais.
- Em cada viewport, `documentElement.scrollWidth` e `body.scrollWidth` corresponderam à largura solicitada (1440, 1024, 390 e 360); nenhum elemento ultrapassou os limites horizontais. Na tela móvel, o painel de apresentação foi ocultado e o formulário ocupou o layout compacto.
- A coleta dedicada de console retornou **zero entradas `error`/`warn`** no momento da verificação. Isso cobre a tela de login observada, não a navegação autenticada.
- Não foi feita coleta de falhas de rede ou latência de dashboard nesta sessão porque o app permaneceu em `/login`. O histórico da fase 2R.4.3 já registra `/api/progress/overview` em **5,14 s no primeiro carregamento** (acima do timeout cliente de 5 s) e **aprox. 0,06 s após aquecimento**; essa medição é da chamada de API no teste funcional, não um tempo visual do browser.
- O registro 2R.4.4 contém a tentativa anterior de autenticação que recebeu **401**. Nenhuma nova tentativa foi feita. Não foram lidos ou registrados senha, cookies de sessão ou tokens.

### Classificação dos fluxos

| Fluxo | Classificação nesta etapa | Evidência/limite |
|---|---|---|
| Login e disponibilidade do app | **Parcial — login visível** | `/login` respondeu e renderizou; autenticação manual ainda necessária. |
| Dashboard do aluno, perfil autenticado, trilhas, busca, navegação/conteúdo e progresso | **Bloqueado** | Exigem sessão; não foram abertos nesta sessão. |
| Editor e submissões/feedback | **Bloqueado por sessão e permissão** | Retomar somente com conta sintética com as permissões necessárias. |
| Administração | **Bloqueado por sessão e permissão** | Retomar somente com conta sintética com permissões administrativas. |
| Responsividade da tela de login | **Verificada nas quatro larguras** | Sem overflow horizontal observado; capturas reais apresentadas nesta sessão. |
| Responsividade das telas autenticadas | **Não executada** | Aguardando autenticação manual. |

### Continuação

O navegador foi deixado visível em `http://localhost:13000/login` para autenticação manual. Após a conta sintética de QA abrir o dashboard, retomar a medição de latência no browser, coletar erros/falhas de rede e testar os fluxos permitidos conforme as permissões da conta. Nenhum código, banco, container, rede ou outro projeto foi alterado nesta etapa.


## 13. Atualização final — Fase 2R.4.5: homologação autenticada

**Data:** 16/10/2026 (America/Sao_Paulo)
**Ambiente:** `trilhacode-phase2r4-qa`, frontend `http://localhost:13000`, API `http://localhost:18000`, schema 2 e índices 23/23 conforme estado informado para esta fase.
**Conta observada:** papel **Estudante**. Nenhuma credencial, cookie de sessão ou token foi lido, copiado ou registrado.

### Fluxos funcionais

| Fluxo | Resultado | Evidência e ressalvas |
|---|---|---|
| Dashboard do aluno | **Aprovado funcionalmente** | Saudação, trilha, retomada e progresso carregaram. Link de retomada abriu o tópico salvo. |
| Perfil | **Aprovado para leitura/navegação** | Página e campos Nome, Bio e Objetivos carregaram; não salvamos alterações. |
| Trilhas e busca | **Aprovado** | Uma trilha foi listada; busca `Variáveis` filtrou para 1 tópico. |
| Navegação e conteúdo | **Aprovado parcialmente** | Visão da trilha, tópico `Variáveis e tipos` e próximo tópico liberado `Condicionais e laços` abriram; conteúdo, checklist, snippet e quiz renderizaram. |
| Feedback do quiz | **Aprovado na UI** | Resposta `Sim` exibiu “Correto” e explicação. Depois, a aba Exercícios continuou mostrando “Nenhum exercício respondido”; o quiz não gerou submissão persistida observável. |
| Progresso | **Aprovado** | Pelo botão da interface, o tópico foi marcado como concluído; a trilha passou de 0/9 (0%) a 1/9 (11%), com próximo passo atualizado. Escrita restrita a esse dado sintético na QA. |
| Editor/administração | **Não executado por permissão** | A conta exibiu papel Estudante e não apresentou controles administrativos. Não foi usada conta com papel editor/admin. |
| Submissões persistentes e feedback de submissão | **Pendente** | O material acessível expôs um quiz com feedback imediato, mas nenhum exercício com envio persistente. A aba Exercícios permaneceu vazia após o quiz. |

### Responsividade e evidência visual

Screenshots reais do browser foram capturados e apresentados nesta sessão para dashboard, perfil e conteúdo nas larguras **1440, 1024, 390 e 360 px**. Não foram exportados para arquivos locais; por isso as imagens aparecem na evidência desta sessão, mas não têm caminhos de arquivo neste repositório.

| Largura | Dashboard | Perfil | Trilha/conteúdo | Resultado de layout |
|---:|---|---|---|---|
| 1440 px | Capturado | Capturado | Capturado | Sem overflow horizontal observado. |
| 1024 px | Capturado | Capturado | Capturado | Sem overflow horizontal observado. |
| 390 px | Capturado | Capturado | Capturado | **Defeito:** largura do documento 430 px; navegação superior e botão de conta extrapolam a viewport em cerca de 40 px. Barra horizontal visível. |
| 360 px | Capturado | Capturado | Capturado | **Defeito:** largura do documento 430 px; navegação superior extrapola a viewport em cerca de 70 px. Barra horizontal visível. |

O overflow é provocado pela navegação superior: a área de conta começa em x=384 px e termina em x=430 px, e a linha de navegação também ultrapassa o limite em 360 px. O conteúdo principal se ajusta à tela, mas o documento mantém scroll horizontal. Classificação: **defeito visual responsivo reproduzível em dashboard, perfil e conteúdo a 390/360 px**.

### Latência, console, rede e autorização

- O carregamento inicial do dashboard após o login foi concluído antes de a sessão de automação receber a aba e **não tem medição confiável**. Nas duas recargas autenticadas medidas depois, até o card da trilha ficar visível: **1.011 ms** na primeira recarga observada e **637 ms** na seguinte. São tempos de navegador nessa sessão aquecida, não a primeira abertura após login.
- A medição anterior da chamada API fria `/api/progress/overview` permanece: **5,14 s** na primeira chamada e aprox. **0,06 s** após aquecimento (registrada na fase 2R.4.3). Não inferir desses tempos que o dashboard inicial no browser levou 5,14 s.
- Coleta do console nesta sessão: **0 erros e 0 avisos** nos níveis consultados.
- Não foi possível coletar lista/status de requests do browser com a ferramenta disponível. A tentativa read-only de consultar logs do container API QA foi negada pelo acesso ao Docker Engine (`permission denied`). Assim, não há falhas de rede ou códigos HTTP novos confirmados nesta sessão. O 401 da tentativa anterior de login continua documentado na fase 2R.4.4; após a sessão autenticada, nenhum erro de autorização apareceu na interface durante os fluxos exercidos.

### Resultado e escopo

**Veredito: PARCIALMENTE HOMOLOGADO.** Fluxos do estudante cobertos: dashboard, perfil (sem salvar), trilha, busca, navegação/conteúdo, feedback de quiz e progresso. Defeito visual confirmado em 390/360 px. Editor, submissões persistentes e administração permanecem pendentes de uma conta sintética com permissões e conteúdo de exercício adequados. Nenhum código foi modificado; nenhuma migração, criação de índices, seed, `resume-restores`, push ou deploy foi executado. A única escrita funcional foi concluir 1 tópico pela interface no banco QA.

## 14. Fase 2R.4.6 — Correção de overflow mobile

**Data:** 16/10/2026 (America/Sao_Paulo)
**Ambiente:** frontend QA http://localhost:13000, sessão autenticada de estudante, projeto Compose trilhacode-phase2r4-qa.

### Causa raiz e correção

- O container do topo usava uma única linha sem quebra (flex h-14 justify-between). O agrupamento da marca e da navegação tinha largura natural mínima: marca, espaçamento gap-8 e dois links ocupavam aproximadamente **368 px** antes mesmo do botão da conta. Este começava em **x=384 px** e terminava em **x=430 px**. Em 360 px, o link “Meu estudo” também passava da borda. O conteúdo principal não era a causa.
- Em telas pequenas, o topo agora permite duas linhas: marca e conta na primeira, links de navegação preservados na segunda. O grupo usa min-w-0 e os links podem quebrar quando necessário. A partir do breakpoint sm, a linha única, espaçamentos, altura e tamanhos tipográficos originais do desktop permanecem ativos.
- O botão de conta compacto recebeu nome acessível explícito. Links e botão têm contorno de foco visível com focus-visible; nenhum link foi removido e menus/itens continuam disponíveis pelo teclado.

### Arquivos alterados

- frontend/src/components/layout/TopBar.tsx — quebra responsiva e compactação da navegação, nome acessível do menu da conta e foco visível.
- PHASE2R4_HOMOLOGATION.md — este registro.

### Validação visual e funcional

O navegador real foi usado antes e depois. Antes da correção, dashboard e perfil foram capturados em 390/360 px; o conteúdo também foi medido nessas larguras. As capturas mostraram o botão/links cortados e barra horizontal. Depois, dashboard, perfil e conteúdo foram abertos nas quatro larguras e não houve elemento com borda direita além do viewport.

| Página | 1440 px | 1024 px | 390 px | 360 px |
|---|---:|---:|---:|---:|
| Dashboard | Sem overflow | Sem overflow | Sem overflow | Sem overflow |
| Perfil | Sem overflow | Sem overflow | Sem overflow | Sem overflow |
| Trilha/conteúdo | Sem overflow | Sem overflow | Sem overflow | Sem overflow |

As larguras medidas de document.documentElement.scrollWidth nunca excederam window.innerWidth após a correção; em alguns estados com barra vertical, a largura documentada ficou 15 px menor que a viewport. As capturas reais depois da correção mostram dashboard, perfil e conteúdo em layout móvel. As imagens foram exibidas nesta sessão, mas não exportadas para arquivos: a interface de navegador disponível retornou capturas visuais sem caminho de gravação local.

No celular, “Estudar” e “Meu estudo” permanecem visíveis, legíveis e navegam para / e /estudos. O menu da conta foi aberto com Enter, expôs “Perfil” e “Sair”, fechou com Escape e devolveu o foco ao botão. O botão compacto anuncia “Menu da conta de João Vitor Camarolli Gallina”; a navegação por teclado mostrou contorno de foco visível. O menu continua alinhado dentro da viewport. Dashboard, perfil e conteúdo renderizaram texto e controles sem corte horizontal. Os tamanhos e a navegação desktop permaneceram sem mudança visual estrutural.

O console do navegador ficou com **0 erros e 0 avisos** após a correção.

### Testes frontend

Os comandos foram executados no serviço frontend do Compose QA, que contém as dependências do projeto:

- npm run typecheck — passou.
- npm run lint — passou.
- npm test — passou; 2 arquivos e 4 testes.
- npm run build — passou. Vite ainda emite o aviso existente de chunk acima de 500 kB (chunk IconCatalog, aprox. 800 kB); a compilação termina com sucesso.

### Resultado e pendências

**Overflow mobile: corrigido e verificado** nas três páginas e quatro viewports. Não foi usado overflow-x: hidden global. O build não introduziu falha; o aviso de tamanho do chunk permanece fora do escopo. Permanecem as pendências de homologação anteriores para editor/admin e submissão persistente, sem relação com esta alteração. Nenhuma mudança foi feita no backend, MongoDB, índices ou migrações; não houve commit, push ou deploy.

## 15. Fase 2R.4.7 — Homologação administrativa e de submissões

**Data:** 16/10/2026 (America/Sao_Paulo)
**Veredito:** **PARCIALMENTE HOMOLOGADO** — administração, editor, permissões e fluxo de submissão manual exercitados em dados sintéticos no QA. Os quatro viewports solicitados não puderam ser configurados nesta interface de navegador; console JavaScript e painel de rede também não estavam expostos.

### Segurança e isolamento

- Projeto Compose confirmado: `trilhacode-phase2r4-qa`. Frontend `http://localhost:13000` e API `http://localhost:18000` responderam 200; `/ready` retornou schema versão 2.
- API QA apontou para o serviço `mongo` e banco `trilhacode_phase2r4_qa`. MongoDB 7.0.43 permaneceu `healthy`; `ping=1`. A API e Mongo QA compartilham `trilhacode_phase2r4_qa_internal`; Mongo não publica porta no host. API e frontend estão mapeados somente em loopback.
- O inventário do Docker também mostrou serviços de outros projetos ativos no host. Nenhum foi usado, conectado ao fluxo ou alterado; a rede e o banco de QA foram confirmados separadamente.
- Nenhuma senha, hash, cookie ou token foi registrado. Não foram executados `migrate`, `ensure-indexes`, `seed` completo ou `resume-restores`.

### Diagnóstico e correção dos e-mails seed

- `LoginIn` e `RegisterIn` usam Pydantic `EmailStr`. No ambiente QA, `admin.qa@example.invalid` e `qa-admin@example.test` foram rejeitados; endereços `@example.com` passaram. A validação ocorre antes da autenticação, por isso o login seed recebia 422.
- A rotina `run_seed()` chama `_seed_user(settings.admin_email, ...)`, `_seed_user(settings.editor_email, ...)` e `_seed_user(settings.student_email, ...)` em desenvolvimento/QA. Os endereços inválidos vinham das variáveis de ambiente declaradas em `compose.qa.yaml`; `_seed_user` gravava a string sem validar, criando contas que a rota de login não aceitava.
- Correção permanente sem afrouxar a regra: os três e-mails QA agora usam `example.com`; `_seed_user` normaliza e valida com o mesmo `EmailStr` antes de consultar ou gravar. Endereço inválido falha antes de qualquer escrita. `backend/tests/test_seed.py` protege a aceitação dos três endereços QA e a rejeição de `.invalid`.
- Para disponibilizar contas privilegiadas, foi verificada a política em `backend/constants.py`, `permissions.py` e `services/auth.py`: cadastro público sempre cria `student`; admin e editor recebem papéis via seed; a troca de papel exige `users.manage`, disponível somente a admin, e o ator não pode alterar o próprio papel. Não foi concedido privilégio a estudante.
- As contas admin/editor sintéticas foram criadas/verificadas invocando somente `_seed_user` dentro do container API QA, com o banco QA confirmado, em um único event loop. O seed completo não foi executado. Cadastro público normal criou os dois estudantes sintéticos auxiliares.

### Contas sintéticas usadas

| Conta | Papel | Uso |
|---|---|---|
| `admin.qa@example.com` | admin | Painel, editor e correção |
| `editor.qa@example.com` | editor | Acesso editorial e testes de permissões |
| `student.qa@example.com` | student | Submissão, lista do estudante e feedback |
| `student.qa2@example.com` | student | Submissão independente e teste de isolamento entre estudantes |

As quatro contas foram verificadas no banco QA. Ambas as contas de estudante têm submissões persistidas. Nenhuma conta real foi usada; a sessão real que já estava aberta no navegador foi encerrada antes dos testes.

### Autorização por papel

Login e logout de admin, editor e estudante funcionaram pela interface e pela API. Status observados nas rotas da API:

| Papel | `/api/admin/stats` | `/api/users` | `/api/submissions` |
|---|---:|---:|---:|
| Admin | 200 | 200 | 200 |
| Editor | 200 | 403 | 200 |
| Estudante | 403 | 403 | 403 |

- Na interface, o estudante não vê o link Admin e uma navegação direta a `/admin` retornou para `/`. Editor acessou o painel e não recebeu link Usuários; tentativa direta de `/admin/usuarios` também retornou para `/`.
- Editor e admin puderam abrir a fila de correções. O estudante só acessou sua própria submissão; uma tentativa de ler a submissão do segundo estudante retornou 404.
- Nenhuma falha de autorização foi observada nos fluxos testados.

### Painel administrativo e editor

- Painel carregou estatísticas e histórico sintético. Lista de trilhas exibiu abas de status, busca e ações. Fila de correções exibiu filtros por status/tipo, busca e detalhe da resposta; a busca pelo estudante sintético encontrou a submissão correta.
- Teste de formulário sem título mostrou “Informe o título da trilha”. Foi criada a trilha sintética `Homologação QA 2R.4.7`; foram criados fase, módulo, submódulo, tópico e bloco `exercise_open` com revisão manual e rubrica. A trilha e os itens foram publicados no QA para habilitar a submissão estudantil.
- Edição do resumo do tópico e dos metadados da trilha foi salva pela interface. Recarregar o editor preservou a hierarquia, o bloco, enunciado, critérios, modo manual e os metadados editados.
- A validação vazia do formulário de nó exibiu “Informe um título”; os formulários aceitos exibiram confirmações de salvamento/publicação. Não foi observado erro persistente no fluxo editorial após corrigir os dados do formulário.

### Submissões persistentes e feedback

- `exercise_objective`, `exercise_open` e `practical_challenge` são os tipos de bloco configurados com capability `submission`. O `quiz` seed usa `QuizBlock`: selecionar alternativa exibe “Correto/Ainda não” e explicação, chama o progresso do bloco e **não** cria submissão. Isso corresponde ao fluxo formativo verificado na fase 2R.4.5 e ao código atual.
- O exercício QA criou uma submissão em `submitted`; a lista “Meu estudo > Exercícios” exibiu a tentativa e continuou exibindo-a após recarregar. Contagem de leitura no Mongo QA confirmou uma submissão para cada estudante sintético.
- Admin assumiu a correção (`in_review`), marcou os dois critérios, registrou feedback e aprovou (`graded`). A tela do estudante, após nova sessão e recarga, exibiu status corrigido, resposta, rubrica e feedback. A tentativa cross-user foi 404.
- Envio vazio retornou 400 com mensagem API “A resposta está vazia”. A interface mostrou inicialmente o texto genérico do Axios porque `apiError` só lia `detail`, enquanto o backend usa `{error:{message}}`. `apiError` agora também lê esse envelope, com teste de regressão.
- Não foi exercitado fluxo de devolução/reenvio nesta rodada; o fluxo de aprovação e feedback está implementado e foi homologado.

### Inspeção visual, console e rede

- Capturas reais do painel administrativo, editor com árvore/bloco e feedback do estudante foram exibidas durante a sessão. A interface de navegador não forneceu caminho de exportação; portanto as imagens não foram anexadas como arquivos.
- A viewport disponível nesta sessão foi aproximadamente **842 px** de largura. Nela, o painel mostrou grade em duas colunas e o editor manteve árvore e formulário lado a lado; não foi observado corte horizontal óbvio nas capturas.
- Não foi possível configurar as larguras **1440, 1024, 390 e 360 px** para estas telas com o controle de navegador disponível. A fase 2R.4.6 documenta aquelas larguras para dashboard, perfil e conteúdo do estudante, mas isso não substitui a verificação administrativa solicitada. Scroll horizontal e layout mobile de admin/editor/submissões ficam pendentes.
- O controle disponível expôs árvore de acessibilidade e screenshots, mas não console JavaScript nem painel de requests. Não há contagem de console/rede desta rodada. As respostas HTTP de health/ready e dos testes de autorização foram verificadas diretamente na API.

### Arquivos e regressão

Arquivos alterados nesta fase:

- `backend/seed.py` — validação e normalização `EmailStr` no seed de usuários.
- `backend/tests/test_seed.py` — quatro casos de regressão para endereços aceitos/rejeitados.
- `compose.qa.yaml` — endereços QA válidos com `example.com`.
- `frontend/src/lib/api.ts` — leitura de `error.message` na resposta API.
- `frontend/src/lib/api.test.ts` — dois testes de mensagens dos formatos `error.message` e `detail`.
- `PHASE2R4_HOMOLOGATION.md` — este relatório.

Validações executadas após as alterações:

- `backend/tests/test_seed.py` isolado de fixtures globais de banco: **4 passaram**.
- `frontend/src/lib/api.test.ts`: **2 passaram**.
- Frontend `typecheck`: passou; frontend `lint`: passou; Ruff nos arquivos Python alterados: passou.
- Configuração Compose validada e endpoints QA health/ready/frontend responderam 200.

### Pendências

- Executar inspeção visual admin/editor/submissões em 1440, 1024, 390 e 360 px, quando houver controle de viewport adequado; registrar overflow, teclado/foco, mensagens, console e requests nessas larguras.
- O teste de console/rede do navegador não pôde ser realizado com as APIs de navegador disponíveis nesta sessão.
- Não foi feito commit, push ou deploy. As alterações e os dados sintéticos permanecem no workspace e no banco descartável QA para revisão.

## 16. Fase 2R.4.8 — QA visual administrativo final

**Data:** 16/10/2026 (America/Sao_Paulo)
**Veredito:** **NÃO HOMOLOGADO VISUALMENTE nesta rodada** — os viewports solicitados não puderam ser definidos ou medidos e a sessão autenticada aberta não correspondeu com segurança a uma das contas sintéticas listadas. Nenhum defeito funcional de admin/editor foi reproduzido nesta fase.

### Estado local identificado antes da inspeção

O relatório já estava não rastreado. O working tree também contém alterações locais preexistentes em `backend/indexes.py`, `backend/seed.py`, `backend/tests/test_integrity_concurrency.py`, `frontend/src/components/layout/TopBar.tsx` e `frontend/src/lib/api.ts`, além dos arquivos não rastreados `backend/tests/test_seed.py`, `frontend/src/lib/api.test.ts` e `compose.qa.yaml`. As mudanças abrangem preflight de índices/PyMongo, validação de e-mails QA, resposta de erros da API, TopBar responsiva e testes associados. Foram preservadas; nenhuma correção de produto foi feita nesta fase.

### Navegador e controle de viewport

- Navegador disponível: **Codex In-app Browser**. A versão do motor/navegador não foi exposta.
- A interface de controle forneceu navegação, árvore de acessibilidade e screenshots exibidos na sessão, mas não expôs API de viewport, avaliação DOM ou dimensões de `window.innerWidth` e `document.documentElement.scrollWidth`.
- Foi investigada a alternativa Playwright já disponível: o frontend não declara Playwright nas dependências. A tentativa de carregar os módulos Playwright no runtime existente falhou por incompatibilidade de módulo; não foi instalado software nem alterada a resolução/configuração global do Windows.
- A captura retornada pela interface não foi exportada para arquivo. Como as dimensões CSS reais não puderam ser lidas, nenhum tamanho de viewport foi atribuído às capturas atuais.

### Matriz visual desta fase

| Viewport solicitado | Admin | Editor | Estudante | Overflow/documento medido |
|---|---|---|---|---|
| 1440 × 900 | Não executado | Não executado | Não executado | Indisponível |
| 1024 × 768 | Não executado | Não executado | Não executado | Indisponível |
| 390 × 844 | Não executado | Não executado | Não executado | Indisponível |
| 360 × 800 | Não executado | Não executado | Não executado | Indisponível |

| Fluxo | Resultado da fase 2R.4.8 |
|---|---|
| Dashboard administrativo, listas/tabelas/filtros | Não executado: sem sessão admin sintética confirmada |
| Criação/edição de trilha, árvore de nós e editor de blocos | Não executado: sem sessão admin/editor sintética confirmada |
| Formulários, validações e confirmações | Não executado nesta fase |
| Fila de submissões, revisão, rubrica e feedback | Não executado nesta fase |
| Menus, dropdowns, modais e tabelas | Não homologados nesta fase; a abertura do menu observada ocorreu numa sessão que não foi aceita como QA e não conta como evidência |

A fase 2R.4.7 registra separadamente telas reais de painel/editor/feedback em viewport aproximado de 842 px, fluxos administrativos em contas sintéticas e limitações de captura. Isso não cobre nem substitui os quatro viewports desta matriz.

### Acessibilidade, console e rede

- O dashboard que estava visível permitiu avançar o foco por Tab até o link da marca; o indicador de foco era visível na captura. O menu de conta aberto foi fechado com Escape e o foco voltou ao acionador. Porém a identidade exposta no menu não correspondeu com segurança às contas QA documentadas, portanto esses sinais **não são contabilizados como aprovação de acessibilidade QA**.
- A sessão foi deixada sem novas interações após essa divergência. Nenhuma senha, cookie ou token foi registrado no relatório.
- Console JavaScript, requests/status de rede e falhas de recursos não foram acessíveis pela ferramenta de navegador utilizada. Não se afirma ausência de erros 4xx/5xx ou avisos.
- Não foi observada mensagem de validação, tentativa de autorização ou problema de carregamento de admin nesta fase, pois os fluxos não foram exercitados.

### Correções, verificações e lacunas

- Nenhum defeito administrativo foi reproduzido; nenhuma correção foi aplicada. Typecheck, lint, testes frontend e build não foram repetidos nesta fase, pois não houve alteração de código. Permanecem válidos apenas os resultados executados e atribuídos à fase 2R.4.7.
- A sessão sintética admin foi solicitada ao usuário. Até confirmação e troca de sessão, seguem pendentes a matriz administrativa por viewport, as verificações visuais de corte/rolagem e a coleta de console/rede. A ausência de controle de viewport permanece uma limitação mesmo após a troca de sessão.
- Nenhum banco, container ou permissão foi alterado; não foram executados migrations, ensure-indexes, seed, resume-restores, commit, push ou deploy.

**Veredito final da fase 2R.4.8:** inspeção visual administrativa **inconclusiva/não homologada** por limitação de viewport e falta de sessão sintética administrativa confirmada. As evidências anteriores de 2R.4.6 e 2R.4.7 permanecem restritas ao escopo e tamanhos declarados naquelas fases; não se declara aprovação dos testes não executados.

## 17. Fase 2R.4.9 — Homologação visual administrativa

**Data:** 16/10/2026 (America/Sao_Paulo)
**Veredito:** **Parcialmente homologado** — sessão QA sintética confirmada, fluxos administrativos inspecionados, três problemas reproduzidos de overflow horizontal corrigidos e revalidados no frontend QA. Console sem erros/avisos capturados. A inspeção de status HTTP das requisições não estava disponível na ferramenta.

### Identidade e escopo

- Sessão confirmada pelo menu de conta: `admin.qa@example.com`, nome **Admin QA Sintético**, papel **ADMIN**.
- Os dados abertos no painel incluem a trilha sintética **Homologação QA 2R.4.7**, conteúdo de exercício e submissões QA. O navegador permaneceu exclusivamente em `http://localhost:13000`.
- Nenhuma credencial, cookie ou token foi lido ou registrado. Nenhuma ação de correção foi enviada (iniciar, aprovar, reprovar ou devolver), pois isso gravaria um novo estado. A submissão pendente e uma revisão aprovada existente foram inspecionadas somente para validar a apresentação da resposta, rubrica, feedback e histórico.

### Viewports e matriz visual

Dimensões coletadas por `window.innerWidth × window.innerHeight`; `clientWidth` é menor quando a barra vertical clássica ocupa espaço. `scrollWidth` é a largura total do documento e foi comparada com `clientWidth` para identificar overflow horizontal.

| Viewport medido | Áreas inspecionadas | `clientWidth` / `scrollWidth` após correções | Resultado |
|---|---|---:|---|
| 1440 × 900 | dashboard, lista de trilhas, editor e revisão/feedback | 1440 / 1440 no dashboard | Sem overflow horizontal observado |
| 1024 × 768 | lista de trilhas, taxonomias/blocos, usuários e editor de nó | 1009 / 1009 na lista e no editor | Sem overflow horizontal; rolagem vertical normal |
| 390 × 844 | fila de correções, editor do nó e bloco | 375 / 375 | Sem overflow horizontal após correções |
| 360 × 800 | lista/filtros de trilhas, fila de correções, editor, modal de criação e lista de usuários | 345 / 345 | Sem overflow horizontal após correções |

As dimensões da viewport foram efetivamente controladas e medidas no navegador integrado. Foram capturadas telas reais do dashboard, lista, editor, fila/feedback e modal. A ferramenta mostrou as capturas durante a inspeção, mas não disponibilizou exportação para arquivo local; por isso não há caminho de screenshot salvo a anexar.

### Fluxos e acessibilidade

- **Dashboard:** métricas de estrutura, publicação, blocos, relações e atividade recente carregaram. A estrutura sintética QA foi encontrada.
- **Listas/filtros:** a lista de trilhas carregou; filtros de status e busca foram usados e refletiram a seleção. A lista de usuários carregou e manteve a largura do documento dentro da viewport. A fila de correções mostrou 1 resposta enviada e 1 corrigida; abas de status e filtro por trilha foram usados com resultado visível.
- **Editor:** trilha sintética, fase, módulo, submódulo, nó e bloco de exercício manual foram abertos. Campos de edição do nó e do bloco foram lidos sem alterá-los; o botão “Salvar” do nó estava desabilitado enquanto não havia mudanças.
- **Revisão/feedback:** painel de uma submissão pendente mostrou enunciado, resposta, rubrica e ações. Uma submissão já corrigida mostrou resposta do estudante, decisão, feedback e histórico.
- **Modal:** modal “Nova trilha” foi aberto em 1024 e 360 px; abas Geral/Nomenclatura/Regras foram navegadas, a rolagem vertical interna foi observada em mobile e o modal foi fechado por Escape sem criar conteúdo.
- **Teclado/foco:** Escape fechou o menu de conta e o modal; setas navegaram as abas do modal; o foco retornou ao acionador de conta e apresentou contorno visível de 2 px.
- Não foram observados cortes horizontais após as correções nem falhas de carregamento nas telas conferidas. Os modais e painéis mantiveram rolagem vertical própria em mobile.

### Defeitos reproduzidos e correções

1. **Editor de trilha/nó em 360 px:** antes da correção, `clientWidth=360` e `scrollWidth=371`; a coluna automática do grid mantinha largura mínima baseada no conteúdo. O grid passou a usar uma coluna `minmax(0, 1fr)` em mobile e colunas com `minmax(0, 1fr)` no desktop, com `min-w-0` nos itens. Revalidado em 360 e 390 px, sem overflow do documento.
2. **Fila de correções em 390/360 px:** as abas de status (441 px na captura inicial) e o cartão ampliavam o documento. As abas agora quebram em múltiplas linhas e o contêiner/lista podem encolher; revalidado com `clientWidth=scrollWidth` em ambos os tamanhos.
3. **Lista de trilhas em 360 px:** as quatro abas de status mediam 366 px contra 345 px disponíveis e causavam rolagem horizontal. As abas agora quebram em duas linhas; revalidado em 360 px, com `clientWidth=scrollWidth=345`.

Arquivos corrigidos:

- `frontend/src/pages/admin/TrackEditor.tsx`
- `frontend/src/pages/admin/Grading.tsx`
- `frontend/src/pages/admin/AdminTracks.tsx`

O serviço reiniciado para carregar as alterações foi somente `frontend` do Compose `trilhacode-phase2r4-qa`. API, Mongo e os demais containers não foram reiniciados nem alterados.

### Console, rede e testes

- Logs de console acessíveis: mensagens informativas/debug do Vite e React DevTools; **0 erros e 0 avisos** capturados.
- A interface de navegador expôs logs de console e métricas DOM, mas não expôs o painel de rede nem estados HTTP por requisição. Portanto falhas HTTP não podem ser descartadas com base nesta inspeção.
- Testes frontend executados no serviço frontend QA após as correções: **3 arquivos e 6 testes passaram** (`api.test.ts`, `AuthContext.test.tsx`, `App.test.tsx`).
- A instalação local de dependências tentou acessar o registry público, mas a rede estava indisponível. Isso não impediu o teste: a suíte foi executada com as dependências já presentes no container frontend QA. Typecheck e lint não foram repetidos nesta fase.

### Restrições respeitadas e pendências

- Não foram executados migrations, criação de índices, seed, `resume-restores`, comandos de escrita de dados, commit, push ou deploy.
- A revisão visual dos painéis foi coberta, mas não foi enviada nova avaliação (aprovar/reprovar/devolver), para preservar o estado persistente das submissões QA.
- Console e foco foram verificados; coleta HTTP detalhada não está disponível nesta ferramenta. Capturas reais foram feitas, mas não puderam ser gravadas em arquivos pela API do navegador.

**Veredito final da fase 2R.4.9:** **parcialmente homologado**. Os três defeitos visuais reproduzidos foram corrigidos e revalidados nos tamanhos afetados. A análise de status HTTP por requisição e a exportação local dos screenshots permanecem pendentes por limitação de ferramenta.

## 10. Consolidação — Fase 2R.5: regressão e release candidate

**Data:** 16/10/2026 (America/Sao_Paulo)
**Base revisada:** `fbb33fbc452b83d80083fe17c93e8f3df0ee6500`.
**Resultado:** regressão local aprovada; homologação funcional/visual permanece parcial; CI remoto e gates de staging não foram executados.

### Escopo aprovado e evidências

- QA reportado na fase 2R.4: MongoDB 7.0.43, schema 2 e **23/23 índices compatíveis**, sem ausentes, conflitos ou duplicatas; esta fase não repetiu preflight, migrações, criação de índices ou seed.
- Fluxos funcionais de estudante, administração, editor e submissões persistentes nos estados `submitted`, `in_review` e `graded` foram exercitados conforme as atualizações 2R.4.6–2R.4.9.
- A responsividade foi medida nos viewports administrativos de 1440, 1024, 390 e 360 px. Os três overflows encontrados foram corrigidos e revalidados; console administrativo sem erros ou avisos capturados.
- Backend: **70/70 testes passaram em 13,77 s** contra MongoDB 7.0.43 descartável em `127.0.0.1:27018`. O fixture usou somente banco `test_<uuid>` e o removeu ao terminar. O banco QA `trilhacode_phase2r4_qa` não foi usado pela suíte.
- A coleta encontrou 70 testes. Isso inclui comparações de chaves compostas/textuais, duplicatas e filtros parciais no preflight; validação e normalização no seed; e os dois testes de `apiError` em `frontend/src/lib/api.test.ts`.
- Nenhuma operação de escrita foi executada no MongoDB QA nesta fase.

### Regressões e builds da Fase 2R.5

- Ruff completo no backend candidato: **aprovado**. O script temporário `_qa_reset_admin_password.py` foi excluído da verificação por não fazer parte do candidato; os fontes candidatos passaram sem erros.
- Compilação Python: **60 fontes compiladas**, excluindo virtualenvs, dependências instaladas e caches.
- `pip-audit -r backend/requirements.txt`: **nenhuma vulnerabilidade conhecida**.
- Frontend: instalação limpa por `npm ci` no build Docker, typecheck, ESLint, Vitest **6/6**, build de produção e `npm audit --audit-level=high` aprovados; a auditoria encontrou zero vulnerabilidades. `api.test.ts` foi incluído (2 testes). A tentativa de `npm ci` diretamente no host falhou por DNS para `registry.npmjs.org`; a instalação limpa no container concluiu com sucesso.
- Imagens de produção da API e frontend construídas localmente sem iniciar ou substituir serviços existentes. A imagem da API importa `AsyncMongoClient` do PyMongo 4.18.2 e contém `backend/indexes.py` corrigido, sem bind mount. O contexto do backend ficou em aproximadamente 172 KB.
- O bundle frontend foi criado; Vite emitiu aviso de chunk maior que 500 KB (chunk `IconCatalog`, cerca de 800 KB antes de gzip). Não bloqueou o build.
- As imagens permaneceram locais; não foram publicadas.

### Revisão de segurança e estado dos dados

- `compose.qa.yaml` validado sem iniciar serviços: Mongo sem porta publicada, API/frontend em loopback, banco `trilhacode_phase2r4_qa`, rede Mongo interna dedicada, credenciais raiz/JWT interpoladas de `.env.qa` e comando da API apenas Uvicorn.
- Removidas do Compose as credenciais fixas das contas QA. O `.env.qa` permaneceu local e ignorado pelo Git; seus valores não foram lidos nem registrados.
- `_qa_reset_admin_password.py` permaneceu no workspace, sem ser removido ou versionado. Regras Docker agora também o excluem dos contextos de desenvolvimento e produção.
- Não há `.env.qa`, cookies, sessões, backups, dumps MongoDB ou screenshots sensíveis entre os arquivos candidatos. Caches e dados locais ignorados foram preservados.
- A ferramenta de navegador não exportou as screenshots capturadas para arquivos e não mostrou o painel de rede/status por requisição. A aprovação funcional e de layout está limitada às evidências documentadas; essas duas lacunas continuam explícitas.

### Pendências de release/staging

- Revisar o arquivo `PHASE2R5_RELEASE_REVIEW.md` e aprovar o inventário antes de criar o commit candidato.
- Criar o commit após revisão, então executar CI remoto no SHA exato com alvo `none` (sem deploy). Exigir jobs backend/frontend verdes e preservar a proteção de branch.
- Staging ainda requer backup recente e restore verificado, aplicação do procedimento operacional de `DEPLOY.md`, confirmação de schema/índices e smoke tests após deploy autorizado.
- Não declarar homologação completa nem promover a produção até fechar CI, backup/restore, staging, evidências visuais exportáveis e revisão operacional.
