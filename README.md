# Trilha Code

Plataforma full stack para organizar e estudar trilhas de aprendizagem. Administradores e editores mantêm trilhas, conteúdos e avaliações; estudantes acompanham o material, registram progresso e enviam exercícios. A aplicação usa React/TypeScript, FastAPI e MongoDB.

## Arquitetura

- `frontend`: React 19 com TypeScript e Vite; servidor de desenvolvimento na porta 3000.
- `backend/routes_*.py`: validação HTTP, permissões e serialização; `backend/services/` contém serviços por domínio, e `backend/schemas/` os contratos Pydantic.
- `api`: FastAPI/Uvicorn na porta 8000; no startup verifica a versão do banco. Índices, migrações, seed e retomada de restores são comandos explícitos.
- `mongo`: MongoDB 7, acessível à API na rede Compose como `mongo:27017`; dados persistidos no volume nomeado `mongo_data`.

O Compose é uma configuração de desenvolvimento: monta o código local e permite recarga durante a edição. O Vite serve a aplicação localmente; para produção, gere o bundle com `npm run build` ou use `frontend/Dockerfile.prod`, que serve o resultado pelo Nginx. Publique a API ASGI e o MongoDB em uma infraestrutura com autenticação, TLS, gestão de segredos, backups e controles de rede.

## Pré-requisitos

- Docker Desktop (Windows/macOS) ou Docker Engine (Linux), com Docker Compose v2 (`docker compose`).
- Git para clonar o repositório.

## Iniciar com Docker Compose

Na raiz do projeto, copie o exemplo de ambiente e inicie os serviços:

```sh
cp .env.example .env
docker compose up --build
```

No Windows PowerShell, use `Copy-Item .env.example .env` no primeiro comando. Os valores do exemplo são de desenvolvimento; gere um segredo JWT próprio antes de compartilhar o ambiente. Por exemplo, com OpenSSL: `openssl rand -hex 32`. As senhas das contas de demonstração também podem ser trocadas no `.env`. O arquivo `.env` é local e ignorado pelo Git.

A API e o frontend não copiam arquivos `.env` para suas imagens. O Compose fornece as variáveis de ambiente aos serviços. Como o backend monta `./backend` dentro do container, um `backend/.env` local também fica visível e `load_dotenv` pode carregá-lo. `load_dotenv` não sobrescreve variáveis já definidas por padrão; assim, os valores injetados pelo Compose, incluindo `MONGO_URL`, prevalecem. Para execução diretamente no host, o backend carrega esse arquivo da mesma forma.

O MongoDB não tem autenticação nesta configuração local, mas sua porta não é publicada no host: somente os serviços na rede privada do Compose o acessam. A API conecta a `mongo:27017`. Já o navegador acessa a API pela URL em `VITE_BACKEND_URL`, por padrão `http://localhost:8000`; o navegador não resolve o nome interno `api` do Compose.

### Comandos do dia a dia

```sh
# Iniciar em primeiro plano e acompanhar os logs
docker compose up --build

# Iniciar em segundo plano
docker compose up -d --build

# Acompanhar logs de todos os serviços ou somente da API
docker compose logs -f
docker compose logs -f api

# Parar/remover containers e rede; preserva o volume do MongoDB
docker compose down

# Recriar a imagem e o volume anônimo do node_modules do frontend
docker compose up -d --build --renew-anon-volumes
```

Use o último comando depois de alterar `frontend/package.json` ou `frontend/package-lock.json`, para que o volume `node_modules` seja recriado a partir das dependências instaladas pela imagem. O Dockerfile instala com `npm ci`.

### Acesso

- Aplicação: [http://localhost:3000](http://localhost:3000)
- API: [http://localhost:8000/api/](http://localhost:8000/api/)
- Liveness: [http://localhost:8000/health](http://localhost:8000/health) (não acessa o MongoDB)
- Readiness: [http://localhost:8000/ready](http://localhost:8000/ready) (ping no MongoDB e versão de migração)
- Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)

## Variáveis de ambiente

O Compose lê o `.env` da raiz. A tabela mostra os valores do `.env.example`; contas e segredo listados são apenas para desenvolvimento.

| Variável | Serviço | Exemplo | Descrição |
|---|---|---|---|
| `ENV` | API | `development` | Ambiente: `development`, `staging` ou `production`. |
| `DB_NAME` | API | `trilhacode_dev` | Banco usado pela aplicação. |
| `JWT_SECRET` | API | valor fictício de desenvolvimento | Chave JWT. Fora de `development`, precisa ter pelo menos 32 caracteres e não pode ser um valor de exemplo. |
| `FRONTEND_URL` | API | `http://localhost:3000` | Origem principal; também é incluída na lista de CORS. |
| `CORS_ORIGINS` | API | `http://localhost:3000` | Origens permitidas separadas por vírgula. |
| `MONGO_URL` | API | definido pelo Compose | URL do MongoDB. No Coolify, informe a URL do serviço de banco. |
| `COOKIE_DOMAIN` | API | vazio | Domínio do cookie, se necessário para compartilhar entre subdomínios. |
| `COOKIE_SAMESITE` | API | `lax` em produção | `lax`, `strict` ou `none`; `none` exige HTTPS e `COOKIE_SECURE=true`. |
| `COOKIE_SECURE` | API | derivado de `ENV` | Cookies seguros por padrão em produção; defina explicitamente se necessário. |
| `TRUSTED_PROXY_IPS` | API | vazio | IPs ou CIDRs de proxies separados por vírgula. Só esses peers habilitam confiança em `X-Forwarded-For`. |
| `ADMIN_EMAIL`, `ADMIN_PASSWORD` | API | vazios | Desenvolvimento: conta demo opcional. Produção: cria o primeiro admin somente se ainda não houver admin. |
| `EDITOR_EMAIL`, `EDITOR_PASSWORD` | API | vazios | Desenvolvimento/staging: contas demo opcionais; ignoradas em produção. |
| `STUDENT_EMAIL`, `STUDENT_PASSWORD` | API | vazios | Desenvolvimento/staging: contas demo opcionais; ignoradas em produção. |
| `VITE_BACKEND_URL` | Frontend | `http://localhost:8000` | URL da API que o navegador pode alcançar; ajuste se mudar `API_PORT`. No deploy, é uma variável de build. |
| `FRONTEND_PORT` | Compose/frontend | `3000` | Porta publicada do frontend; ajuste também `FRONTEND_URL`. |
| `API_PORT` | Compose/API | `8000` | Porta publicada da API; ajuste também `VITE_BACKEND_URL`. |
| `VITE_SENTRY_DSN`, `VITE_SENTRY_ENVIRONMENT`, `VITE_SENTRY_RELEASE` | Frontend | vazios / production | Configuração opcional do Sentry no navegador; valores `VITE_*` são incorporados ao bundle no build. |

Os exemplos contêm somente valores fictícios. Em staging e produção, configure os segredos no gerenciador de ambiente do Coolify; não use os valores do exemplo. O `JWT_SECRET` deve ter pelo menos 32 caracteres fora de development. O seed nunca redefine senha de usuário existente.

## Dados, seed e migrações

O volume nomeado `mongo_data` preserva os dados quando os containers são parados, reiniciados ou recriados. `docker compose down` mantém esse volume; ao iniciar novamente, os dados existentes continuam disponíveis. O diretório local `mongo-data/` pertence à execução manual e já está excluído pelo `.gitignore`; o Compose não o usa.

Para apagar os dados do banco Compose e começar do zero:

```sh
docker compose down --volumes
```

Esse comando remove o volume `mongo_data` e apaga permanentemente os dados nele. Não o use se quiser preservar o banco. Ele não remove a pasta local `mongo-data/`.

Na raiz do repositório, os comandos explícitos são:

```sh
python -m backend.manage ensure-indexes
python -m backend.manage migrate
python -m backend.manage seed
python -m backend.manage resume-restores
```

`migrate` aplica migrações numeradas de `backend/migrations/` e registra a versão na coleção `migrations`, sob uma trava distribuída. `ensure-indexes` é idempotente. `seed` é idempotente e não redefine senhas. `resume-restores` recupera jobs pendentes usando lease e heartbeat. O Compose de desenvolvimento executa esses comandos antes da API; `run_local.ps1` faz o mesmo no Windows. A API apenas verifica a versão esperada e falha em produção quando faltam migrações.

Em development e staging, o seed cria a trilha demonstrativa e as contas configuradas; documentos da trilha, nós, blocos e usuários de demonstração recebem `is_demo: true`. Em production, esse conteúdo e as contas demo não são criados. O primeiro administrador só é criado com `ADMIN_EMAIL` e `ADMIN_PASSWORD`, e apenas quando ainda não há nenhum admin. Se a conta informada já existir, o seed não altera seus dados nem senha.

Para execução local, `backend/.env.example` e `frontend/.env.example` documentam as configurações. O backend carrega `backend/.env` com `pydantic-settings`; o Vite lê `VITE_BACKEND_URL` no servidor local e o incorpora ao bundle de produção. O Compose injeta as variáveis no serviço da API. Em produção, `/docs`, `/redoc` e `/openapi.json` ficam desabilitados.

## Execução local sem Docker

Pré-requisitos: Python 3.11+, Node.js/npm e MongoDB Community Server 7 (a mesma versão principal do Compose). O script `run_local.ps1` é uma alternativa no Windows: cria o ambiente virtual Python se necessário, instala requisitos e abre terminais para API e frontend; se encontrar `mongod`, tenta iniciá-lo usando a pasta `mongo-data/`.

Configure os exemplos e inicie o script:

```powershell
Copy-Item .\backend\.env.example .\backend\.env
Copy-Item .\frontend\.env.example .\frontend\.env
.\run_local.ps1
```

Se `mongod` não estiver no PATH, crie a pasta `mongo-data/` se ela ainda não existir e inicie o MongoDB:

```powershell
New-Item -ItemType Directory -Force .\mongo-data
mongod --dbpath .\mongo-data
```

No Linux/macOS, instale o MongoDB Community Server 7, crie a pasta `mongo-data/` e use `mongod --dbpath ./mongo-data`. Configure `backend/.env` com `MONGO_URL="mongodb://localhost:27017"` e `frontend/.env` com `VITE_BACKEND_URL=http://localhost:8000`.

Para iniciar manualmente, primeiro prepare o ambiente Python e depois rode os serviços em terminais separados:

```powershell
# Na raiz, criar e ativar o ambiente Python
py -3.11 -m venv backend\.venv
backend\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt

# Em outro terminal, frontend
cd frontend
npm ci
npm start
```

No Linux/macOS, a ativação equivale a `source backend/.venv/bin/activate`; depois de ativar, rode `python -m pip install -r backend/requirements.txt`. Em um terminal para a API, a partir da pasta `backend/`, execute `uvicorn server:app --reload --host 0.0.0.0 --port 8000`. Em outro, na pasta `frontend/`, execute `npm ci` e `npm start`. O script PowerShell define `FRONTEND_URL=http://localhost:3000` para o processo da API.

## Solução de problemas

- **Compose não inicia:** confirme que Docker Desktop/Engine está rodando e que `docker compose version` funciona.
- **Porta 3000 ou 8000 ocupada:** ajuste `FRONTEND_PORT` ou `API_PORT` no `.env` e as URLs relacionadas na tabela de variáveis.
- **API não fica saudável:** confira `docker compose logs -f mongo api`; a API aguarda o health check do banco.
- **Frontend não alcança a API:** use em `VITE_BACKEND_URL` uma URL alcançável pelo navegador, como `http://localhost:8000`; `api` é um nome interno dos containers.
- **Script falha com erro de fim de linha no WSL/Linux:** arquivos com finais de linha CRLF podem causar erros. Converta o script afetado para LF antes de executá-lo em Linux/containers; `run_local.ps1` é destinado ao PowerShell do Windows.
- **Execução manual sem MongoDB:** confirme que MongoDB 7 está instalado e que `mongod --dbpath ./mongo-data` (ou `mongod --dbpath .\\mongo-data` no PowerShell) está em execução.

## Testes e lint

- Frontend: `npm test` executa Vitest; `npm run typecheck`, `npm run lint` e `npm run build` verificam tipos, lint e bundle.
- Backend: execute `python -m pytest` na pasta `backend/` com MongoDB disponível em `mongodb://localhost:27017`. Os testes usam o app FastAPI em processo e um banco descartável `test_<uuid>`, removido ao final; configure outro endereço com `MONGO_URL_TEST`. O nome do banco é validado como proteção contra exclusão de dados fora de teste. `VITE_BACKEND_URL` não é usado pela suíte.

## Conteúdo do curso

`docs/courses/trilhacode/Conteudos/` guarda os materiais editoriais detalhados das unidades. Eles não são carregados automaticamente pelo Compose. O arquivo `docs/courses/trilhacode/trilha-code-bulk-import.json` é um pacote de importação compatível com a API; para incluí-lo na plataforma, use a tela de importação do painel administrativo, confira a simulação e confirme a importação.

## Contribuição e licença

Não há um arquivo de licença nem um guia de contribuição formal neste repositório. Antes de redistribuir ou publicar o projeto, defina e inclua uma licença adequada. Para propor mudanças, abra uma branch, descreva o objetivo e os passos de validação e envie um Pull Request.

## Estrutura

- `backend/routes_*.py`: endpoints e validação HTTP.
- `backend/services/`: regras de negócio e acesso ao MongoDB por domínio.
- `backend/schemas/`: modelos de entrada e saída da API.
- `backend/migrations/`: migrações de dados numeradas e versionadas.
- `backend/manage.py`: CLI para migrações, seed, índices e retomada de restores.
- `frontend/src/components/`: componentes de tela; `frontend/src/types/` contém tipos TypeScript compartilhados da aplicação.
- `frontend/`: aplicação React, estilos e dependências Node.
- `compose.yaml`: ambiente local de desenvolvimento com MongoDB, API e frontend.
- `run_local.ps1`: inicialização local no Windows sem Compose.
- `docs/courses/`: materiais e pacote de importação do curso Trilha Code.
