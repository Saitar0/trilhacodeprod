# Deploy Trilha Code com Coolify

Este projeto usa duas aplicações independentes no Coolify: **API** e **frontend**, em cada ambiente. Isso permite domínios, variáveis de build e implantações independentes. A API não executa migrações ao iniciar; preflight, migração e criação de índices seguem os gates operacionais da seção 7. O MongoDB é um recurso gerenciado pelo Coolify. Não use `compose.yaml` para produção: ele é voltado ao desenvolvimento local.

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
- `FRONTEND_URL`, `CORS_ORIGINS`, `COOKIE_DOMAIN`, `COOKIE_SAMESITE=Lax` e `COOKIE_SECURE=true`: substitua os exemplos por origens HTTPS reais sem caminho/query/fragmento. Staging e production usam cookies seguros por padrão e rejeitam configuração explícita `COOKIE_SECURE=false`. `COOKIE_DOMAIN` deve corresponder ao host do frontend (por exemplo, `.dominio-real.tld`) e ser isolado entre ambientes quando ambos compartilham o mesmo navegador. A API rejeita hosts reservados/de exemplo.
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
- Adicione todas as variáveis API do arquivo de exemplo correspondente. A configuração production rejeita segredo JWT inseguro, hosts reservados/de exemplo, domínio de cookie ausente ou incompatível com o frontend, URLs sem HTTPS ou com caminhos, e admin inicial incompleto.
- Não trate `python -m backend.manage migrate` isoladamente como procedimento completo. Siga a sequência de release da seção 7 antes de promover a aplicação. Não configure `seed` como pre-deploy. A imagem não executa migração, criação de índices nem seed ao iniciar.
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
- A CSP inicial libera estilos inline (compatibilidade com componentes React), imagens/conexões HTTPS (imagens externas, API e Sentry) e frames do YouTube e Vimeo, que são os provedores aceitos pelos blocos de vídeo. Scripts continuam restritos à mesma origem. Se os hosts reais de imagens/Sentry forem conhecidos, restrinja `img-src` e `connect-src` a esses hosts.

## 7. Sequência de release e banco de dados

Execute cada etapa em uma tarefa operacional registrada, com confirmação explícita do ambiente e do `DB_NAME`. Use a imagem do commit candidato e a URI/credencial do ambiente alvo. Não copie URI ou credenciais de production para staging. O `preflight-indexes` não modifica o banco; `migrate` e `ensure-indexes` escrevem.

### Pré-condições

1. Commit candidato identificado e jobs backend/frontend verdes no CI; staging visualmente homologado antes de qualquer promoção.
2. Janela aprovada, responsável operacional presente, acesso de rollback confirmado e backup recente concluído. Para production, confirme também um restore recente de teste, retenção e espaço livre no Mongo e volume da VPS.
3. Confirme destino, `DB_NAME`, host/cluster, credencial de menor privilégio e versão do MongoDB com o operador. Verifique que o alvo é o banco exclusivo do ambiente planejado. Pare se qualquer identificador divergir.
4. Capture estado atual: versão do app, `/ready`, versão de schema, inventário dos índices e métricas do banco. Suspenda mudanças concorrentes de schema e cargas administrativas durante a operação.

### Ordem obrigatória

1. **Backup:** crie snapshot/backup consistente imediatamente antes da mudança; registre confirmação, horário, local e retenção. Em production, não prossiga se o backup falhar ou não puder ser localizado.
2. **Preflight (somente leitura):** rode `python -m backend.manage preflight-indexes`. Ele compara os índices esperados com os existentes e agrupa chaves para todos os índices únicos, incluindo filtros de índices parciais. `OK` significa compatível; `AUSENTE` significa que será necessária criação; `CONFLITO` significa mesmas chaves com opções/nome incompatíveis; `DUPLICATAS` lista exemplos. Coleções grandes podem tornar o scan demorado e consumir CPU/memória. Interrompa se houver conflito, duplicatas ou erro/limite de recursos; não tente corrigir automaticamente.
3. **Migrate (escrita de dados):** só após revisar e aprovar a saída do preflight, rode `python -m backend.manage migrate`. Migrações obrigatórias: `0001_legacy_snapshots` compacta snapshots embutidos em chunks e altera documentos de versões; `0002_block_submission_capabilities` atualiza campos/capacidades em tipos de bloco existentes. O CLI usa uma trava de migração com lease de 15 minutos e grava registros em `migrations`. O startup da API exige schema versão 2; portanto, aplique migração antes de iniciar o novo backend. Confirme versão 2 e logs antes de continuar.
4. **Preflight pós-migração:** rode novamente `python -m backend.manage preflight-indexes`. Migrações podem alterar dados. Pare caso apareçam conflitos ou duplicatas; escale a correção como mudança de dados separada, com plano e aprovação próprios.
5. **Ensure-indexes (escrita de índices):** com o segundo preflight limpo, rode `python -m backend.manage ensure-indexes`. Este é o único comando de gerenciamento que cria os índices declarados em `backend/indexes.py`. Não é chamado por `migrate`, pelo startup da API ou pelo Docker entrypoint. O comando cria os índices em sequência e não remove índices extras.
6. **Verificação:** rode novamente `python -m backend.manage preflight-indexes`. Exija `OK` em todos e nenhuma saída `AUSENTE`, `CONFLITO` ou `DUPLICATAS`. Depois valide `/health`, `/ready` (schema 2), logs, métricas e smoke test autenticado em staging. Só então autorize a publicação manual pelo workflow, na branch e ambiente corretos.

### Índices cobertos pelo preflight e ensure-indexes

| Coleção | Índices esperados (ordem e opções) |
| --- | --- |
| `users` | `email` unique |
| `login_attempts` | `identifier`; `last` TTL 3600 s |
| `nodes` | `(track_id, parent_id, order)`; texto `(title, summary)`, nome `node_search_text` |
| `content_blocks` | `(node_id, order)` |
| `relations` | `track_id` |
| `progress` | `(user_id, track_id)`; `(user_id, node_id, block_id)` unique |
| `user_track_state` | `(user_id, track_id)` unique, `one_user_track_state` |
| `learning_events` | `(user_id, at desc)` |
| `edit_history` | `(track_id, at desc)` |
| `taxonomies` | `(group, key)` unique |
| `block_types` | `key` unique |
| `tags` | `slug` unique, `one_tag_slug` |
| `submissions` | `(user_id, block_id, attempt desc)` unique; `(status, submitted_at)` |
| `notes` | `(user_id, node_id, block_id)` unique |
| `reviews` | `(user_id, status, due_at)`; `(user_id, node_id, block_id)` unique parcial `status=pending`, `one_pending_review` |
| `version_chunks` | `(version_id, seq)` unique |
| `restore_jobs` | `track_id` unique parcial `status=running`, `one_running_restore` |
| `migrations` | `key` unique |

As definições do código são a fonte de verdade para chaves e opções. `preflight-indexes` é somente leitura: lista especificações e faz agregações de duplicatas. Ele não reserva o estado do banco e não elimina a possibilidade de uma escrita concorrente criar conflito depois da checagem. Congelar operações de escrita relevantes durante o intervalo entre preflight e criação é obrigatório.

### Impacto, falhas e critérios de aborto

- Agregações de duplicidade percorrem as coleções para chaves únicas. Embora não escrevam, podem demorar e pressionar CPU/memória; monitore e faça primeiro em staging com volume representativo. Se excederem recursos, não habilite `allowDiskUse` às cegas nem prossiga: dimensione e planeje uma checagem controlada.
- MongoDB 7 constrói índices com bloqueios exclusivos breves no início/fim; durante a maior parte da construção permite operações intercaladas. Ainda há consumo relevante de CPU, memória, I/O e disco temporário, e as escritas passam a manter cada índice. Duração depende de volume, cardinalidade, hardware e carga; meça em staging com dataset representativo e reserve janela. Índices podem afetar latência de escrita.
- Referências oficiais: [processo de build de índices no MongoDB 7](https://www.mongodb.com/docs/v7.0/core/index-creation/) e [parâmetros de memória para index build](https://www.mongodb.com/docs/v7.0/reference/parameters/).
- Se `ensure-indexes` falhar, o comando para no primeiro erro e índices anteriores podem já ter sido criados. Não há rollback automático. Registre o erro; corrija a causa por procedimento aprovado, rode preflight, repita `ensure-indexes` (idempotente para índices compatíveis) e preflight final. Não derrube índices existentes como tentativa de reparo.
- Aborte antes de prosseguir diante de backup ausente, ambiente/credencial incerta, preflight com duplicatas/conflitos, falha parcial de migração, versão de schema diferente de 2, falta de disco, saturação/latência fora do limite acordado, healthcheck falho, erro de aplicação ou CI não verde. Não inicie o novo backend se a migração não concluiu: o lifespan rejeitará schema anterior.
- A restauração de backup pode descartar gravações posteriores; use-a apenas como recuperação planejada, com decisão do responsável pelo banco. Preferir rollback da aplicação se o schema continuar compatível.

## 8. CI e disparo de deploy

A opção implementada é o deploy webhook de recurso do Coolify disparado pelo GitHub Actions **após os jobs `backend`, `frontend` e `e2e` passarem**. O workflow `.github/workflows/ci-deploy.yml` valida em push para `main`/`staging`, PRs destinados a essas branches e `workflow_dispatch`. Pushes e PRs executam somente os checks. A publicação exige execução manual com input explícito `staging` ou `production`, branch correspondente e todos os três jobs verdes. O input manual padrão é `none`. Cada job de deploy também está associado ao GitHub Environment correspondente.

Para rodar o CI completo sem deploy, use um PR para `main` ou `staging`, faça push às branches validadas ou execute `workflow_dispatch` na branch/commit candidato com input `none`. Só depois da sequência de banco da seção 7, e com aprovação operacional registrada, execute `workflow_dispatch` na branch adequada com input de publicação correspondente. Em qualquer dispatch de verificação, mantenha o input `none`; os jobs de deploy serão pulados.

Os jobs de validação e publicação permanecem no mesmo arquivo, mas têm gatilhos/condições separados. A validação não depende de secrets; a publicação exige os secrets Coolify, branch e input explícitos. Configure ambientes `staging` e `production` com revisores/proteção adequada no GitHub Settings; a associação `environment:` por si só não configura aprovação. Proteja `main` exigindo ambos os checks e bloqueando push direto/bypass. Desative auto-deploy por push no Coolify para que ele não contorne o gate manual do workflow. Preserve os secrets atuais e não replique credenciais de deploy nos jobs de teste.

O job envia uma chamada autenticada ao webhook sem retry automático. Se a chamada falhar ou expirar, o resultado pode ser ambíguo: primeiro confira o estado da implantação no Coolify antes de repetir o dispatch, pois o webhook pode ter enfileirado o deploy mesmo sem uma resposta utilizável. Um job concluído confirma apenas a resposta HTTP do webhook; não confirma conclusão, saúde ou readiness da aplicação. Verifique esses estados no Coolify e pelos endpoints de health/readiness antes de declarar o ambiente homologado.

1. Em **Keys & Tokens > API Tokens**, crie um token Coolify com permissão mínima **deploy** e prazo de validade.
2. Atribua tags distintas `trilhacode-production` e `trilhacode-staging` às aplicações API e frontend de cada ambiente (não ao Mongo). Em **Webhooks**, copie o **Deploy Webhook (auth required)** de cada tag.
3. Crie os quatro GitHub repository secrets em **Settings > Secrets and variables > Actions**: `COOLIFY_PRODUCTION_WEBHOOK`, `COOLIFY_PRODUCTION_TOKEN`, `COOLIFY_STAGING_WEBHOOK`, `COOLIFY_STAGING_TOKEN`. O token exige apenas permissão `deploy`. O workflow aciona todos os recursos da tag depois dos checks; se preferir separar a ordem/observação da API e frontend, use dois webhooks e duas chamadas por job.
4. Proteja `main` com revisão e checks obrigatórios. Um pedido de deploy aceito apenas enfileira o deploy; confirme o estado saudável no Coolify.

Alternativa manual: se sua versão Coolify oferecer **Wait for CI**, habilite-o junto do auto-deploy da branch e confirme que aguarda os checks requeridos do GitHub antes de iniciar. Sem esse recurso, o auto-deploy em push pode correr em paralelo ao CI; prefira o workflow com webhook autenticado. Consulte [Coolify Deploy Webhooks](https://coolify.io/docs/core/automation/deploy-webhooks).

## 9. Primeiro acesso e checagens

1. Faça o primeiro deploy de staging, observe logs e confirme `https://api.staging.example.com/health` e `/ready`.
2. Em cada ambiente, depois da migração e do banco prontos, execute uma única vez no container/API pelo comando de execução do Coolify: `python -m backend.manage seed`. É idempotente: cria o admin de `ADMIN_EMAIL`/`ADMIN_PASSWORD` se não existir e prepara taxonomias; em production não semeia trilha demo. Não rode isso repetidamente se pretende rotacionar a senha de usuário.
3. Abra o frontend, entre como admin, e confirme login, navegação e leitura de conteúdo. O login retorna cookies `access_token` e `refresh_token` com `HttpOnly`, `Secure`, `SameSite=Lax`, `Path=/` e o domínio configurado. No navegador confirme esses atributos e que não há bloqueio CORS/cookies.
4. Repita para staging com suas credenciais próprias. Em production confirme `/ready` saudável e que `/docs`, `/redoc` e `/openapi.json` retornam 404.

## 10. Backup, segurança e rollback

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
