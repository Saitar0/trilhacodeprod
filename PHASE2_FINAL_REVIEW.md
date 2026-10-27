# Trilha Code — Revisão final da Fase 2

**Data:** 16/10/2026  
**Escopo:** homologação técnica e preparação de release. Nenhuma migração foi executada e nenhum banco real foi acessado. Nenhum push ou deploy foi feito.

## Veredito

**Não recomendado para release ainda (aprovação técnica condicional).** A inspeção estática confirma a migração para PyMongo Async, as agregações no padrão assíncrono e o bloqueio de deploy no CI até backend e frontend passarem. Ainda faltam resultados atuais e verificáveis de CI com instalação limpa, confirmação operacional dos novos índices em staging e inspeção visual das telas após a migração para Tailwind 4.

## Inspeção técnica

| Área | Resultado |
|---|---|
| Dependências backend | `pymongo==4.18.2` consta em `backend/requirements.txt` e `backend/requirements.prod.txt`. Não há referência a Motor nos manifests nem no código backend pesquisado. |
| Imagem API | `backend/Dockerfile.prod` usa Python 3.11 slim e instala `requirements.prod.txt`; executa a API pelo entrypoint. |
| Dependências e imagem frontend | `frontend/package.json` e lockfile definem os scripts de typecheck, lint, testes e build. `frontend/Dockerfile.prod` usa Node 20 para build e Nginx Alpine para servir `dist`. |
| PyMongo Async | `backend/database.py` cria um singleton `AsyncMongoClient`; `core.py` mantém a fachada compartilhada conforme os testes coletados e o relatório de migração. |
| `aggregate()` | Foram localizadas oito ocorrências em código/testes. Todas fazem `await ...aggregate(...)` e consomem os cursores de forma assíncrona. Nenhuma chamada sem await foi encontrada. |
| Inicialização/encerramento | O lifespan do FastAPI verifica a versão do schema antes de servir requisições e fecha o cliente com `await client.close()` no `finally`. O CLI fecha o cliente em `finally`; o teardown de testes fecha o cliente assíncrono. |
| CI/deploy | `.github/workflows/ci-deploy.yml` tem jobs independentes `backend` e `frontend`; ambos os deploys declaram `needs: [backend, frontend]`. Backend usa Python 3.11 e MongoDB 7 de serviço; frontend usa Node 20 e `npm ci`. |
| Tailwind 4 | CSS importa `tailwindcss`, carrega explicitamente a configuração JS legada com `@config` e PostCSS usa `@tailwindcss/postcss`. A configuração parece preparada para Tailwind 4, mas isso não confirma a aparência visual. |

### Índices e plano de deploy

`backend/indexes.py` contém índices novos/necessários, inclusive índices únicos para estado de trilha, tags, tentativas, notas e revisões. Há verificações de duplicidade antes de alguns índices únicos; se dados legados tiverem conflitos, a criação falha com exemplos para correção.

O comando de pre-deploy atualmente documentado em `DEPLOY.md` é `python -m backend.manage migrate`. A imagem de produção não chama `ensure_indexes` no startup, e `migrate` também não chama essa rotina. Assim, o plano documentado não garante a criação dos índices definidos em `indexes.py`. Antes de promover código, é preciso planejar a execução controlada de `python -m backend.manage ensure-indexes` em staging e, se aprovado, incluir essa etapa no processo de release. Isso não foi executado nesta revisão. Confirme previamente duplicidades e impacto/tempo de construção dos índices no dataset de staging; não rode a etapa em production sem janela e plano operacional.

## Validações desta sessão

| Verificação | Resultado atual |
|---|---|
| Ruff | **Aprovado:** `ruff check backend` via ambiente Python 3.11 local, `All checks passed`. |
| Python e dependências instaladas | **Parcialmente aprovado:** Python 3.11.9; `pip check` sem dependências quebradas. Isso não substitui instalação limpa do manifest de produção. |
| Coleta pytest | **Aprovada:** 63 testes coletados em 0,09 s. Coleta não executa os testes nem acessa o banco. |
| Suíte pytest | **Não executada nesta sessão:** Docker não conectou ao daemon; não usei `localhost:27017` nem qualquer banco existente. |
| Build da imagem API | **Bloqueado:** o daemon Docker retornou acesso negado no pipe do Docker Desktop. |
| `npm ci` limpo | **Inconclusivo/bloqueado:** tentativa sem progresso foi interrompida. Após ela, os executáveis locais `tsc`, `eslint`, `vitest` e `vite` não estavam disponíveis. |
| Typecheck, ESLint, Vitest e build frontend | **Não executados:** binários ausentes depois da tentativa de instalação. |
| Auditorias `pip-audit`/`npm audit` | **Não executadas nesta sessão:** não havia execução limpa de dependências e a instalação npm não se concluiu. |
| Visualização Tailwind 4 | **Não executada:** sem build frontend utilizável e sem inspeção das páginas no navegador. |

## Evidências anteriores e divergências

- O contexto desta homologação informa que **63 testes backend passaram** com Python 3.11 e MongoDB 7 descartável. Registro essa informação como evidência fornecida para esta revisão, não como execução repetida por mim.
- `PHASE2C1_ASYNC_FIX.md` documenta 63 testes coletados, mas diz que a suíte não foi executada por indisponibilidade do Docker/MongoDB. `PHASE2C_PYMONGO_ASYNC.md` também registra que a execução integral estava pendente. A divergência deve ser resolvida anexando o log/execução CI ou identificando a execução descartável que passou.
- `FRONTEND_SECURITY_COMPLETION.md` registra resultados anteriores aprovados para typecheck, lint, 4 testes Vitest, build e `npm audit` sem vulnerabilidades. O mesmo documento diz que `npm ci` limpo não foi confirmado localmente e requer confirmação no CI.
- `BACKEND_SECURITY_UPGRADE.md` registra aprovação anterior de 47 testes, Ruff, pip-audit e build da imagem de produção. É evidência de uma fase anterior e não cobre, por si só, os 16 testes adicionais da fase PyMongo Async.
- A configuração estática do workflow foi revisada nesta sessão, mas o status remoto atual do GitHub Actions não foi consultado.

## Bloqueios e riscos de release

1. **CI atual:** obter execução verde do workflow no commit candidato, com job backend completo e job frontend completo incluindo auditorias. Isso fecha a lacuna entre evidência histórica e o código atual.
2. **Índices:** o runbook precisa incluir o comando de índices e um preflight de dados legados em staging. Índices únicos podem falhar diante de duplicatas ou demorar conforme o volume.
3. **Visual:** revisar em navegador telas-chave de estudante, editor e administração, incluindo formulários, navegação, responsividade, estados de foco/hover e páginas com blocos de conteúdo. Tailwind 4 altera defaults e exige browsers modernos; conferir suporte dos navegadores do público.
4. **Acompanhamento do schema:** o lifespan bloqueia startup em produção quando a versão de migração esperada não foi aplicada. A ordem de migration e criação de índices precisa estar explícita no procedimento operacional.
5. **Auditoria de dependências:** os resultados documentados anteriormente são positivos, mas a auditoria atual depende de ambiente limpo e deve ser confirmada pelo CI.

Não identifiquei falha estática que exija refatoração ou correção de código nesta etapa. Não implementei novas funcionalidades nem fiz alterações funcionais.

## Próxima fase — proposta priorizada de funcionalidades educacionais

1. **Prática de recuperação e revisão espaçada:** agendar questões já estudadas com intervalos adaptativos, feedback breve e opção de pausar/reagendar. Métrica: retenção e revisões concluídas.
2. **Avaliação formativa por objetivo:** quizzes curtos por competência, explicação por alternativa e recomendação do próximo conteúdo. Métrica: evolução de acerto por objetivo, não apenas nota geral.
3. **Trilhas adaptativas:** recomendar reforço, avanço ou conteúdo alternativo conforme domínio demonstrado e pré-requisitos. Começar com regras transparentes e controladas por educadores.
4. **Projetos guiados com entregas incrementais:** dividir projetos em marcos, permitir rascunho, feedback e reenvio; reutilizar o fluxo existente de submissões quando adequado.
5. **Visão pedagógica para educadores:** mostrar dificuldades comuns, objetivos com baixo domínio e estudantes que precisam de apoio, com filtros por turma/trilha e proteção de dados.

Sugestão de sequência: validar revisão espaçada em piloto pequeno, medir o efeito da avaliação formativa, então avançar para adaptação e ferramentas de educador. As propostas não foram implementadas.
