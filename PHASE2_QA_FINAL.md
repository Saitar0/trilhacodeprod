# Trilha Code — Homologação final de CI e interface

**Data:** 16/10/2026  
**Commit base:** `91ff14247211e675c9156a2caf113f961f78702e`  
**Estado do checkout:** modificado e com arquivos não rastreados. Os resultados locais abaixo foram obtidos sobre o working tree, que não corresponde apenas ao commit base. Nenhum push, workflow remoto, acesso a banco existente ou deploy foi feito.

## Veredito

**Homologação incompleta; não iniciar staging até resolver os bloqueios locais e confirmar os gates listados ao final.** Ruff passou. A coleta do pytest encontrou um erro de importação reproduzível. As suítes completas, verificações frontend, builds Docker e inspeção visual não puderam ser concluídos nesta sessão.

## 1. CI e caminhos de publicação

Inspecionei `.github/workflows/ci-deploy.yml` e os demais arquivos de workflow presentes no repositório.

- `push` e `pull_request` são limitados às branches `main` e `staging`. Os jobs iniciados por esses eventos são `backend` e `frontend`; os jobs de publicação exigem explicitamente `workflow_dispatch`, então push e PR não publicam por este workflow.
- `workflow_dispatch` oferece `none`, `staging` e `production`, com `none` como padrão. Com `none`, as condições dos dois jobs de publicação são falsas.
- `deploy-staging` exige CI verde (`needs: [backend, frontend]`), alvo `staging` e ref `refs/heads/staging`; `deploy-production` exige os mesmos jobs verdes, alvo `production` e ref `refs/heads/main`.
- Os jobs de publicação apontam para os GitHub Environments `staging` e `production` e usam secrets Coolify. A configuração do workflow, por si só, não confirma que esses environments, aprovações, secrets ou proteções estejam configurados e ativos.
- O workflow de validação não precisa dos secrets Coolify. Não disparei workflow manual nem consultei status remoto, proteções de branch ou configuração externa.
- Não encontrei outro workflow de publicação no diretório `.github/workflows`. `compose.yaml` é configuração de execução local e contém comandos de inicialização com migração/seed; `backend/Dockerfile.prod` e `frontend/Dockerfile.prod` definem imagens, mas não publicam por si. Os arquivos `.env.*.example` documentam integração com Coolify; não provam o estado da configuração externa. Auto-deploy por push no Coolify segue pendente de confirmação operacional.

## 2. Validações locais executadas

| Verificação | Resultado desta sessão |
|---|---|
| Ruff | **Aprovado.** `ruff check backend` usando o ambiente Python 3.11 do projeto: `All checks passed!`. |
| Coleta pytest | **Falhou antes de executar testes.** 56 testes foram coletados; a coleta foi interrompida por `ImportError` em `backend/tests/test_integrity_concurrency.py:8`, que importa `_assert_unique_values` de `indexes`, nome ausente em `backend/indexes.py`. |
| 63 testes backend com MongoDB descartável | **Não executados.** Docker Desktop está presente, mas o acesso ao daemon/arquivo de lock Buildx foi negado; `mongod`/`mongosh` não estão instalados e não havia listener local na porta 27017. Não acessei nenhum banco. |
| `npm ci` | **Falhou por rede/DNS.** O registry `registry.npmjs.org` retornou `ENOTFOUND` ao buscar `zwitch-2.0.4.tgz`. |
| Typecheck, lint, Vitest, build e `npm audit` | **Não executados.** A instalação limpa de dependências não terminou; resultados de instalações anteriores não foram reutilizados como evidência desta sessão. |
| Imagem Docker API | **Bloqueada.** `docker build -f backend/Dockerfile.prod ...` falhou ao abrir `.docker/buildx/.lock` com “Acesso negado”. |
| Imagem Docker frontend | **Bloqueada pela mesma condição.** A tentativa de build falhou ao abrir `.docker/buildx/.lock` com “Acesso negado”. |
| Homologação visual em navegador | **Não executada.** A consulta inicial de estado do navegador excedeu o tempo limite; nenhuma tela foi validada e nenhuma captura foi produzida. |

### Defeito reproduzido

`backend/tests/test_integrity_concurrency.py` ainda referencia `_assert_unique_values`, enquanto `backend/indexes.py` implementa a verificação de duplicatas por outra rotina (`_duplicates`) e não exporta esse helper. Isso impede a coleta integral da suíte no checkout testado. Não alterei código ou regras de negócio nesta homologação.

## 3. Evidências históricas — não são resultados desta sessão

- `PHASE2_RELEASE_READINESS.md` informa que 63 testes passaram anteriormente em MongoDB descartável e que validações frontend anteriores passaram; também registra que é necessário vincular evidência ao commit candidato. Não repeti esses resultados.
- `PHASE2_FINAL_REVIEW.md` relata Ruff aprovado, 63 testes apenas coletados naquela revisão, build Docker bloqueado, instalação npm inconclusiva e lacunas de inspeção visual. O relato histórico de 63 testes aprovados e os registros antigos de suíte não executada precisam ser reconciliados por log/execução identificável.
- `FRONTEND_SECURITY_COMPLETION.md` e `BACKEND_SECURITY_UPGRADE.md` são evidências de fases/estados anteriores e não substituem CI verde no commit candidato.

## 4. Instruções para inspeção visual manual

1. Disponibilize Docker com daemon acessível e use um projeto Compose exclusivo para QA, com volume e banco descartáveis separados. Não reutilize volume, URI, credenciais ou `DB_NAME` de ambientes existentes. Use somente usuários/dados sintéticos.
2. Suba API e frontend com a configuração local de desenvolvimento documentada em `DEPLOY.md`/`compose.yaml`. Registre o hash do commit e as alterações locais presentes; o hash base atual é `91ff14247211e675c9156a2caf113f961f78702e`.
3. Abra no navegador com viewport de 1440 px, 1024 px, 390 px e 360 px. Para cada fluxo, capture tela real e anote navegador/versão, viewport, resultado e erros do console/rede.
4. Percorra: login, mensagens de erro, cadastro, sessão e logout; perfil e formulários; dashboard do aluno; lista/busca/filtros de trilhas; visualizador e navegação de conteúdo; editor de trilhas e blocos; painel administrativo, tabelas e filtros; envio de submissão e correção/feedback.
5. Em cada área, verifique estados carregando, vazio, erro de rede/validação e sucesso. Exercite menus, dropdowns, modais, confirmação de saída, scroll interno, fechamento, hover/focus e navegação por teclado. Confira contraste, tipografia, alinhamento e ausência de scroll horizontal involuntário no mobile.
6. Registre erros JavaScript, requests 4xx/5xx inesperados, recursos 404, problemas de fonte/imagem e falhas de layout. Não marque aprovação visual apenas por build ou screenshots sem exercício dos fluxos.

## 5. Pendências remotas e visuais

- Obter execução verde do workflow no commit candidato, incluindo Ruff, suíte backend completa com MongoDB descartável, `pip-audit`, `npm ci`, typecheck, lint, Vitest, build e `npm audit`.
- Confirmar com responsáveis que branch protection/regras de merge exigem os checks pretendidos, que environments/secrets estão configurados conforme política e que o Coolify não publica por push automático. Esta sessão não confirmou controles externos.
- Executar inspeção visual completa no navegador conforme o roteiro acima e anexar capturas reais identificadas pelo commit testado.
- Resolver a divergência histórica das evidências de testes com URL/log da execução correspondente ao commit candidato.

## 6. Critérios para iniciar staging

- [ ] Corrigir o erro de coleta do pytest e obter execução verde da suíte backend completa contra MongoDB descartável.
- [ ] Concluir instalação limpa e todas as verificações frontend, incluindo auditoria de dependências.
- [ ] Construir as duas imagens de produção localmente ou obter evidência equivalente no CI.
- [ ] Identificar claramente o commit candidato e garantir que as evidências de CI correspondem exatamente a ele.
- [ ] Confirmar configuração de branch protection, GitHub Environments e comportamento de auto-deploy Coolify com os responsáveis; o workflow sozinho não comprova esses controles.
- [ ] Disponibilizar staging isolado, credenciais próprias, dados sintéticos/anonimizados e backup recuperável; confirmar URI e `DB_NAME` com dupla checagem antes de qualquer conexão.
- [ ] Planejar preflight, migrações e índices conforme `DEPLOY.md`, com janela, responsável, monitoramento, rollback e autorização operacional.
- [ ] Aprovar inspeção visual em desktop e mobile com capturas, commit, navegador e console registrados.

Esta homologação não aplicou migrações, criou índices em banco, publicou imagens, disparou workflows ou fez deploy.
