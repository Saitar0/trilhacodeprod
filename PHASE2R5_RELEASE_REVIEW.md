# Trilha Code — Fase 2R.5: revisão do release candidate

**Data:** 16/10/2026 (America/Sao_Paulo)
**Commit base:** `fbb33fbc452b83d80083fe17c93e8f3df0ee6500`
**Estado:** preparado para revisão; alterações não staged e não commitadas. Não houve push ou deploy.

## 1. Arquivos do candidato

### Backend

- `backend/indexes.py` — compatibilidade do preflight com cursores PyMongo Async e comparação de índices compostos/textuais.
- `backend/seed.py` — validação com `EmailStr` e normalização de e-mail.
- `backend/tests/test_integrity_concurrency.py` — mock assíncrono de `list_indexes`.
- `backend/tests/test_seed.py` — validação, rejeição de endereço reservado `.invalid` e normalização antes da consulta.

### Frontend

- `frontend/src/components/layout/TopBar.tsx` — navegação mobile e foco/rotulagem acessíveis.
- `frontend/src/pages/admin/TrackEditor.tsx` — grid responsivo do editor.
- `frontend/src/pages/admin/Grading.tsx` — fila e abas responsivas de correção.
- `frontend/src/pages/admin/AdminTracks.tsx` — lista e abas responsivas de trilhas.
- `frontend/src/lib/api.ts` e `frontend/src/lib/api.test.ts` — leitura do envelope `error.message`, mantendo suporte a `detail`.

### QA, documentação e contexto Docker

- `compose.qa.yaml` — configuração QA sem credenciais fixas de usuário e sem bootstrap automático.
- `.dockerignore`, `backend/.dockerignore` e `backend/Dockerfile.prod.dockerignore` — exclusão do script local temporário de recuperação.
- `PHASE2R4_HOMOLOGATION.md` — estado consolidado da homologação funcional/visual.
- `PHASE2R5_RELEASE_REVIEW.md` — este inventário e resultados.

## 2. Arquivos excluídos

- `backend/_qa_reset_admin_password.py` — script temporário local de recuperação; foi preservado e excluído do candidato, das regras de lint da revisão candidata e dos contextos Docker.
- `.env.qa` — arquivo local ignorado pelo Git, sem valores reproduzidos no relatório.
- Dados, caches, logs e dependências locais ignorados pelo Git; foram preservados. Nenhum cookie, dado de sessão, dump, backup ou screenshot sensível integra o candidato.

## 3. Resultados backend

| Gate | Resultado |
| --- | --- |
| Ruff completo nos fontes candidatos | Aprovado; nenhuma ocorrência |
| Compilação Python | 60 arquivos compilados, virtualenvs/dependências/caches excluídos |
| Coleta pytest | 70 testes coletados |
| Suíte completa | **70/70 aprovados em 13,77 s** |
| Mongo de teste | MongoDB 7.0.43 descartável, `127.0.0.1:27018`, sem volume persistente |
| Isolamento de fixtures | Apenas banco `test_<uuid>`, descartado ao terminar; QA não foi acessado |
| Testes de seed/preflight | Incluídos na suíte completa; cobrem endereço inválido antes da consulta, normalização, 23 especificações, chaves compostas/textuais, duplicatas e filtros parciais |
| `pip-audit` | Nenhuma vulnerabilidade conhecida em `backend/requirements.txt` |

## 4. Resultados frontend

- `npm ci` direto no host falhou com `ENOTFOUND registry.npmjs.org`. O `npm ci` limpo executado no build Docker completou: 677 pacotes e zero vulnerabilidades reportadas.
- `npm run typecheck`: aprovado.
- `npm run lint`: aprovado.
- `npm test`: **6/6 aprovados em 3 arquivos**. `frontend/src/lib/api.test.ts` está incluído e cobre `error.message` e `detail`.
- `npm run build`: aprovado.
- `npm audit --audit-level=high`: aprovado, zero vulnerabilidades.

## 5. Builds de produção

- `backend/Dockerfile.prod`: build limpo aprovado. O contexto ficou em aproximadamente 172 KB. A imagem importa `AsyncMongoClient` com PyMongo 4.18.2 e contém o `backend/indexes.py` corrigido sem depender de bind mount local. O script temporário de recuperação foi excluído do contexto.
- `frontend/Dockerfile.prod`: build limpo aprovado; `npm ci`, TypeScript e Vite passaram. O Vite emitiu aviso de chunk acima de 500 KB para `IconCatalog` (aproximadamente 800 KB antes de gzip; 148 KB gzip).
- As imagens foram construídas apenas localmente. Não houve publicação nem deploy.

## 6. Riscos e pendências

- CI remoto não foi executado para o SHA candidato porque ele ainda não existe como commit.
- A homologação funcional/visual continua parcial: as capturas reais da fase 2R.4 não puderam ser exportadas como arquivos; a ferramenta de navegador não expôs status HTTP por requisição.
- O build frontend mantém um chunk grande de ícones; o build passou, mas o tamanho merece acompanhamento de desempenho.
- Backup/restore operacional, CI verde no commit candidato, staging, smoke tests pós-deploy e revisão de promoção continuam pendentes conforme `DEPLOY.md` e `PHASE2_RELEASE_READINESS.md`.

## 7. Alterações de segurança

- Removidas do Compose as senhas e e-mails sintéticos fixos de admin/editor/estudante. `.env.qa` segue ignorado e os valores não foram lidos ou impressos.
- Compose QA validado sem iniciar serviços: banco exclusivamente `trilhacode_phase2r4_qa`; Mongo sem porta publicada; API/frontend publicados somente em loopback; rede interna QA dedicada; credenciais Mongo/JWT interpoladas de ambiente; API inicia somente Uvicorn.
- `_qa_reset_admin_password.py` foi mantido localmente, não versionado e excluído também dos contextos de build.
- Nenhum banco QA existente, container de outro projeto ou volume de QA foi alterado nesta fase.

## 8. Evidências QA

- A evidência da fase 2R.4 registra MongoDB 7.0.43, schema 2 e **23/23 índices aprovados**, sem ausentes, conflitos ou duplicatas. Não repetimos preflight, migrações, criação de índices, seed ou `resume-restores` nesta fase.
- Fluxos funcionais de estudante, administração, editor e submissões persistentes nos estados `submitted`, `in_review` e `graded` foram exercitados conforme o relatório de homologação.
- A responsividade administrativa foi medida em 1440, 1024, 390 e 360 px; três problemas de overflow foram corrigidos e revalidados. Console sem erros ou avisos capturados.
- Os testes desta fase usaram Mongo temporário separado; nenhum apontou para `trilhacode_phase2r4_qa`.

## 9. Proposta de mensagem de commit

`fix(release): consolidate phase 2r.5 qa corrections`

## 10. Condições para CI remoto

Após revisar este inventário e criar o commit candidato, executar o workflow do GitHub no SHA exato por PR ou `workflow_dispatch` com alvo `none`. Confirmar jobs backend e frontend verdes e anexar a URL/log ao registro de release. O workflow de validação não precisa de secrets de deploy. Não selecionar `staging` ou `production` no dispatch até que os gates operacionais correspondentes estejam aprovados; não habilitar auto-deploy para contornar o workflow.

## 11. Registro do commit controlado — 16/10/2026

- Inventário revisado na `main`, sobre `fbb33fbc452b83d80083fe17c93e8f3df0ee6500`; sem divergência com `origin/main`, conflitos ou alterações staged preexistentes.
- Auditoria do candidato: `.env.qa` permanece ignorado e fora do índice; `_qa_reset_admin_password.py` permanece local, fora do commit e excluído dos contextos Docker raiz, backend e produção. `compose.qa.yaml` usa somente interpolação obrigatória para credenciais, limita portas publicadas a loopback e mantém Mongo em rede interna QA. Não foram encontrados segredos, cookies, dumps, logs sensíveis ou dados reais de usuários nos caminhos selecionados.
- Arquivos incluídos, resultado e SHA do commit: serão registrados após a criação do commit controlado.
- Push: pendente de autorização explícita. CI remoto: pendente de push autorizado; nenhum resultado ou URL disponível ainda.
- Deploy: não executado. O workflow em `.github/workflows/ci-deploy.yml` aciona somente validações em `push`; os jobs de deploy exigem `workflow_dispatch`, alvo explícito e branch correspondente, com padrão `none`. A configuração externa de auto-deploy do Coolify não é verificável neste repositório e precisa permanecer desativada para push.
- Limitações visuais/de rede seguem as registradas acima: capturas sem exportação local e sem painel de status HTTP por requisição. Backup/restore verificado, gates operacionais, staging, smoke tests pós-deploy e revisão de promoção continuam pendentes conforme `DEPLOY.md` e `PHASE2_RELEASE_READINESS.md`.
