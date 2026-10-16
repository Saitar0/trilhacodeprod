# Deploy Trilha Code com Coolify

Este projeto usa duas aplicações independentes no Coolify: **API** e **frontend**, em cada ambiente. Isso permite domínios, variáveis de build e implantações independentes; a API executa a migração como comando pre-deploy. O MongoDB é um recurso gerenciado pelo Coolify. Não use `compose.yaml` para produção: ele é voltado ao desenvolvimento local.

Substitua `example.com`, endereços e valores `REPLACE_...` antes de criar os recursos. Nunca versione credenciais.

## 1. DNS e domínios

Escolha nomes sem ambiguidade:

| Ambiente | Frontend | API |
| --- | --- | --- |
| Production | `app.example.com` | `api.example.com` |
| Staging | `app.staging.example.com` | `api.staging.example.com` |

No DNS do domínio, crie registros **A** para cada hostname apontando para o IPv4 público da VPS Hostinger. Crie registros AAAA somente se IPv6 estiver configurado e acessível na VPS. Aguarde a propagação e confira com `nslookup app.example.com`, `nslookup api.example.com`, `nslookup app.staging.example.com` e `nslookup api.staging.example.com` (ou `dig`). Todos devem resolver para a VPS antes de pedir certificados TLS.

## 2. GitHub privado e projeto Coolify

1. No Coolify, conecte o repositório privado por **GitHub App** ou deploy key somente de leitura. GitHub App é conveniente para manter a integração; deploy key é simples para um repositório único.
2. Crie um projeto `Trilha Code` e dois ambientes: `staging` e `production`.
3. Em cada ambiente, configure branch e recursos distintos: `staging` acompanha a branch `staging`; `production` acompanha `main`.

## 3. MongoDB nativo do Coolify

1. Crie o recurso MongoDB em cada ambiente (recomendado: bancos/credenciais separados; nunca compartilhe DB_NAME entre staging e production).
2. Defina usuário e senha fortes no painel. Use conexão pela rede interna do Coolify e **não publique a porta MongoDB** para a internet.
3. Copie a URI interna exibida pelo Coolify para `MONGO_URL`, incluindo usuário, senha, host/rede, porta, banco e `authSource` adequado. Guarde-a como variável secreta no ambiente da API.
4. Use `DB_NAME=trilhacode_staging` e `DB_NAME=trilhacode_production` respectivamente. Prefira usuários Mongo com permissões limitadas ao banco da aplicação.

## 4. Variáveis de ambiente

Use [`.env.staging.example`](.env.staging.example) e [`.env.production.example`](.env.production.example) como inventário; copie cada variável no painel, sem subir arquivos `.env` reais.

- `JWT_SECRET`: gere um valor aleatório forte, com pelo menos 32 caracteres; mantenha secreto.
- `MONGO_URL` e `ADMIN_PASSWORD`: marque como secrets no Coolify.
- `FRONTEND_URL`, `CORS_ORIGINS`, `COOKIE_DOMAIN`, `COOKIE_SAMESITE=Lax` e `COOKIE_SECURE=true`: configure conforme a tabela. `COOKIE_DOMAIN=.example.com` em production e `.staging.example.com` em staging evita colisão de cookies entre ambientes no mesmo navegador.
- `TRUSTED_PROXY_IPS`: configure o IP/CIDR interno real do proxy Coolify para a aplicação e para os cabeçalhos encaminhados pelo Uvicorn. Não copie `127.0.0.1` do exemplo sem confirmar a topologia da sua VPS. Use apenas endereços do proxy confiável.
- `ADMIN_EMAIL` e `ADMIN_PASSWORD`: credenciais iniciais; use senha única forte. O seed de produção cria o admin se ainda não existir.
- `WEB_CONCURRENCY=1` inicialmente. A API mantém estado externo; aumente só após medir memória/CPU.
- `SENTRY_DSN` é opcional no backend. Para o frontend, configure também `VITE_SENTRY_DSN` se desejar captura no navegador. DSNs são públicos, nunca coloque token de autenticação Sentry no frontend.
- Production desativa `/docs`, `/redoc` e `/openapi.json`; staging os mantém disponíveis.

## 5. Aplicação da API

Crie uma aplicação Dockerfile em cada ambiente, apontando ao repositório/branch corretos:

- Build pack: **Dockerfile**.
- Contexto de build: raiz do repositório (`.`).
- Caminho do Dockerfile: `backend/Dockerfile.prod`.
- Porta interna: `8000` (ou valor de `PORT`). Não publique porta no host; o proxy do Coolify faz o encaminhamento e TLS.
- Domínio: `https://api.example.com` em production; `https://api.staging.example.com` em staging.
- Healthcheck: `GET /health` (já incluído na imagem); depois do deploy confira também `GET /ready`.
- Adicione todas as variáveis API do arquivo de exemplo correspondente. A configuração production rejeita segredo JWT inseguro, domínio de cookie ausente/incorreto, URLs sem HTTPS e admin inicial incompleto.
- Em **Pre-deploy command**, configure `python -m backend.manage migrate`. Não configure `seed` como pre-deploy. A imagem não executa migração nem seed ao iniciar.
- `TRUSTED_PROXY_IPS` controla tanto o `--forwarded-allow-ips` do Uvicorn quanto a identificação do IP cliente usada pelo limitador de login.

## 6. Aplicação do frontend

Crie outra aplicação Dockerfile em cada ambiente:

- Build context: raiz do repositório (`.`).
- Dockerfile: `frontend/Dockerfile.prod`.
- Porta interna: `8080`; não publique porta no host.
- Domínio: `https://app.example.com` em production; `https://app.staging.example.com` em staging.
- O healthcheck `GET /` já está na imagem.
- Cadastre `VITE_BACKEND_URL` como **build variable** (não apenas runtime): `https://api.example.com` ou `https://api.staging.example.com`. O Vite incorpora variáveis `VITE_*` ao JavaScript durante o build; mudar apenas a variável runtime não altera a imagem criada.
- Se habilitar Sentry frontend, informe `VITE_SENTRY_DSN`, `VITE_SENTRY_ENVIRONMENT` e, opcionalmente, `VITE_SENTRY_RELEASE` também como build variables.
- A imagem `frontend/Dockerfile.prod` serve `dist/` pelo Nginx. A CSP mantém `script-src 'self'`; o HTML do Vite carrega o módulo externo empacotado e não depende de scripts inline.
- A CSP inicial libera estilos inline (compatibilidade com componentes React), imagens/conexões HTTPS (imagens externas, API e Sentry) e frames somente do YouTube para blocos de vídeo. Scripts continuam restritos à mesma origem. Se os hosts reais de imagens/Sentry forem conhecidos, restrinja `img-src` e `connect-src` a esses hosts.

## 7. CI e disparo de deploy

A opção implementada é o deploy webhook de recurso do Coolify disparado pelo GitHub Actions **após os jobs de backend e frontend passarem**. O workflow `.github/workflows/ci-deploy.yml` usa `main` para produção e `staging` para staging.

1. Em **Keys & Tokens > API Tokens**, crie um token Coolify com permissão mínima **deploy** e prazo de validade.
2. Atribua tags distintas `trilhacode-production` e `trilhacode-staging` às aplicações API e frontend de cada ambiente (não ao Mongo). Em **Webhooks**, copie o **Deploy Webhook (auth required)** de cada tag.
3. Crie os quatro GitHub repository secrets em **Settings > Secrets and variables > Actions**: `COOLIFY_PRODUCTION_WEBHOOK`, `COOLIFY_PRODUCTION_TOKEN`, `COOLIFY_STAGING_WEBHOOK`, `COOLIFY_STAGING_TOKEN`. O token exige apenas permissão `deploy`. O workflow aciona todos os recursos da tag depois dos checks; se preferir separar a ordem/observação da API e frontend, use dois webhooks e duas chamadas por job.
4. Proteja `main` com revisão e checks obrigatórios. Um pedido de deploy aceito apenas enfileira o deploy; confirme o estado saudável no Coolify.

Alternativa manual: se sua versão Coolify oferecer **Wait for CI**, habilite-o junto do auto-deploy da branch e confirme que aguarda os checks requeridos do GitHub antes de iniciar. Sem esse recurso, o auto-deploy em push pode correr em paralelo ao CI; prefira o workflow com webhook autenticado. Consulte [Coolify Deploy Webhooks](https://coolify.io/docs/core/automation/deploy-webhooks).

## 8. Primeiro acesso e checagens

1. Faça o primeiro deploy de staging, observe logs e confirme `https://api.staging.example.com/health` e `/ready`.
2. Em cada ambiente, depois da migração e do banco prontos, execute uma única vez no container/API pelo comando de execução do Coolify: `python -m backend.manage seed`. É idempotente: cria o admin de `ADMIN_EMAIL`/`ADMIN_PASSWORD` se não existir e prepara taxonomias; em production não semeia trilha demo. Não rode isso repetidamente se pretende rotacionar a senha de usuário.
3. Abra o frontend, entre como admin, e confirme login, navegação e leitura de conteúdo. O login retorna cookies `access_token` e `refresh_token` com `HttpOnly`, `Secure`, `SameSite=Lax`, `Path=/` e o domínio configurado. No navegador confirme esses atributos e que não há bloqueio CORS/cookies.
4. Repita para staging com suas credenciais próprias. Em production confirme `/ready` saudável e que `/docs`, `/redoc` e `/openapi.json` retornam 404.

## 9. Backup, segurança e rollback

Configure backup diário do Mongo para S3 e faça um restore de teste seguindo [`scripts/backup_restore.md`](scripts/backup_restore.md). Confirme sucesso do job, objeto no bucket e leitura da restauração pela aplicação.

Checklist Hostinger/VPS:

- Firewall de entrada: somente SSH (22, de preferência restrito ao seu IP), HTTP (80) e HTTPS (443). Verifique também o firewall da Hostinger.
- SSH somente com chave; desative login SSH por senha quando confirmar acesso por chave e mantenha uma sessão administrativa de reserva durante a mudança.
- Mantenha sistema operacional e Coolify atualizados, com janela de atualização e backup.
- MongoDB sem porta pública; somente redes internas necessárias.
- `/docs`, `/redoc` e `/openapi.json` fechados em production.
- Mongo/S3 com credenciais independentes; secrets somente no painel/secret stores.
- Backups da aplicação no S3 com criptografia, bucket privado, política IAM de menor privilégio e retenção definida.

Rollback: em Coolify abra a aplicação afetada > **Deployments**, escolha o deploy anterior que estava saudável e use a ação de rollback/redeploy disponível nessa versão. Se o rollback exigir novo build, selecione o commit anterior e redeploy. Confirme `/health`, `/ready`, login e logs após a reversão. Migrações devem ser compatíveis com versões anteriores; restaure backup apenas como recuperação de dados planejada, pois pode descartar gravações posteriores.

Recursos: para API + frontend + MongoDB na mesma VPS, comece com **2 vCPU e 4 GB RAM** e disco SSD com folga para dados e backups locais; monitore durante carga real. O tamanho necessário de Mongo depende do volume de conteúdo, snapshots e sessões. Para produção com tráfego/crescimento, prefira 4 vCPU/8 GB ou mova Mongo para recurso gerenciado separado. Mantenha espaço para imagens antigas e restaurações temporárias.
