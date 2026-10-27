# Trilha Code — Conclusão da Fase 1

Data: 16/10/2026

## Resumo

Foram configurados Ruff, auditorias de dependências e verificações explícitas para backend e frontend no GitHub Actions. O frontend passou por code splitting de rotas e componentes compartilhados: o chunk inicial foi reduzido de aproximadamente 1,64 MB para 490,6 KB (158,5 KB gzip). Typecheck, ESLint, testes frontend, build e Ruff passaram localmente.

A conclusão ainda tem dois bloqueios concretos: o ambiente local não tem MongoDB nem acesso ao Docker para executar a suíte backend; e as auditorias online encontraram vulnerabilidades nas dependências Python e JavaScript. As auditorias foram configuradas como etapas finais dos jobs, então o CI exibirá os demais resultados e continuará bloqueando o deploy enquanto esses findings existirem. Nenhuma execução remota do GitHub Actions foi consultada.

## Alterações realizadas

- Adicionada configuração Ruff em `backend/ruff.toml`, direcionada a Python 3.11 e às regras iniciais `E4`, `E7`, `E9`, `F` e `I`. Imports fora do topo são tolerados nos testes porque o fixture configura o banco isolado antes de importar a aplicação; o script de escala conserva instruções compactas com ponto e vírgula.
- Corrigida a organização de imports e removidos imports e atribuições sem uso identificados pelo Ruff, sem alterar a lógica da API.
- Separadas dependências de lint, teste e segurança em `backend/requirements-dev.txt`. `requirements.txt` mantém as dependências de runtime e recursos opcionais; ferramentas e dependências usadas apenas por testes foram movidas para o manifesto de desenvolvimento. O conjunto anterior continua instalado no Docker de desenvolvimento, agora por `requirements-dev.txt`. `requirements.prod.txt` e as versões de produção não foram alterados.
- Configurado o CI para executar Ruff, testes backend, compilação Python, typecheck, ESLint, testes Vitest, build e auditorias pip/npm. As auditorias são os últimos passos dos jobs para que seus findings não ocultem os resultados das outras verificações. Os jobs e condições de deploy Coolify permanecem no workflow.
- Confirmado `npm` como gerenciador oficial por `frontend/package-lock.json`, `npm ci` nos Dockerfiles e ausência de comandos Yarn no CI ou nos scripts. Removidos `yarn.lock` da raiz e `frontend/yarn.lock`; nenhum fluxo encontrado dependia deles.
- Aplicado lazy loading a páginas estudantis e administrativas. Extraído o agrupamento de revisões para um utilitário independente, para que a tela inicial não carregue a página “Meu estudo”.
- Separados o catálogo completo de ícones Lucide e o componente Markdown do módulo comum. Ambos são carregados quando usados; o catálogo completo continua preservado para nomes de ícones fornecidos pelos tipos de bloco.
- Adicionado teste de navegação que confirma o carregamento de uma rota protegida sob lazy loading.

## Arquivos alterados nesta tarefa

- `.github/workflows/ci-deploy.yml`
- `backend/Dockerfile`, `backend/requirements.txt`, `backend/requirements-dev.txt`, `backend/ruff.toml`
- `backend/core.py`, `backend/routes_auth.py`, `backend/routes_content.py`, `backend/routes_progress.py`, `backend/routes_submissions.py`, `backend/routes_taxonomy.py`, `backend/routes_versions.py`, `backend/server.py`
- `backend/tests/backend_test.py`, `backend/tests/conftest.py`, `backend/tests/scale_import.py`, `backend/tests/smoke_hardening.py`, `backend/tests/test_phase2.py`
- `frontend/src/App.tsx`, `frontend/src/App.test.tsx`
- `frontend/src/components/common/index.tsx`, `frontend/src/components/common/IconCatalog.tsx`, `frontend/src/components/common/Markdown.tsx`
- `frontend/src/components/admin/GradingPanel.tsx`, `frontend/src/components/blocks/BlockRendererParts.tsx`, `frontend/src/components/blocks/ExerciseSubmission.tsx`, `frontend/src/components/student/NodeReader.tsx`, `frontend/src/components/student/TrackOverview.tsx`
- `frontend/src/pages/student/Catalog.tsx`, `frontend/src/pages/student/MyStudy.tsx`, `frontend/src/lib/groupReviews.ts`
- Removidos `yarn.lock` e `frontend/yarn.lock`.

O workspace já continha alterações locais e arquivos novos antes desta tarefa. Eles foram preservados. `PHASE1_STATUS.md` não foi sobrescrito.

## Dependências

- Adicionadas em `requirements-dev.txt`: `ruff>=0.14,<1` e `pip-audit>=2.9,<3`.
- Movidas de `requirements.txt` para `requirements-dev.txt`: Black, Flake8, HTTPX, iniconfig, isort, mypy, mypy_extensions, pytest e requests. O Docker de desenvolvimento e o CI instalam esse manifesto, mantendo essas capacidades.
- Nenhuma biblioteca foi removida do conjunto de desenvolvimento. Dependências sem import estático aparente, incluindo clientes de IA e bibliotecas opcionais, foram mantidas por falta de evidência para remoção segura.
- Nenhuma dependência frontend ou lockfile npm foi atualizada.

## Resultados das verificações

| Verificação | Resultado |
|---|---|
| `ruff check backend` | Passou: `All checks passed!` com Ruff 0.17.1. |
| `python -m compileall -q backend` | Passou. |
| `python -m pytest --collect-only -q` em `backend/` | Passou; 47 testes coletados. |
| `python -m pytest -q --tb=short` em `backend/` | Não concluído: o fixture precisa de MongoDB em `localhost:27017`, que não está disponível. A execução ficou aguardando a conexão e foi interrompida; `docker` também não conseguiu acessar o daemon. Não houve conexão a banco preexistente. |
| `npm run typecheck` | Passou. |
| `npm run lint` | Passou. |
| `npm test` | Passou: 2 arquivos e 4 testes. Inclui o teste da rota protegida lazy. |
| `npm run build` | Passou. Chunk inicial: 490,60 KB (158,53 KB gzip); `IconCatalog`: 799,58 KB, carregado sob demanda; `Markdown`: 158,64 KB, carregado pelas páginas que renderizam Markdown. Vite ainda avisa sobre o chunk lazy de ícones acima de 500 KB. |
| `npm audit --audit-level=high` com acesso ao registry | Executou e falhou por vulnerabilidades: 13 no total (2 baixas, 4 moderadas, 5 altas e 2 críticas). Não foi falha de conexão. |
| `pip-audit -r backend/requirements.prod.txt` com acesso ao serviço de advisories | Executou e falhou por 18 entradas de advisories em `pymongo==4.6.3` e `starlette==0.37.2`. Não foi falha de conexão. |
| Parse do workflow YAML | Passou; os jobs backend, frontend e os dois jobs de deploy estão presentes. |
| `git diff --check` | Passou; o Git apenas informou conversão de finais de linha LF/CRLF conforme a configuração local. |

### Principais findings de segurança

- **Python:** a auditoria sinalizou PyMongo e Starlette. A versão atual do Motor e do FastAPI limita a combinação de versões compatíveis desses pacotes; não atualizei o framework/banco automaticamente sem uma mudança de compatibilidade e testes de integração.
- **JavaScript:** os findings incluem advisories transitivos de ESLint, Vitest/Tinypool, AJV e Tailwind/PostCSS. As correções sugeridas pelo audit incluem upgrades que saem das versões/faixas atuais e mudanças de major. Nenhum `npm audit fix` foi executado e o lockfile foi preservado.

## Pendências e bloqueios

1. Executar a suíte backend completa em ambiente com MongoDB descartável. A fixture gera um nome `test_<uuid>` e possui proteção antes do teardown; a execução local foi bloqueada pela ausência do serviço.
2. Planejar atualizações compatíveis para resolver os advisories Python e npm. Até isso ocorrer, os jobs de auditoria falharão e os jobs de deploy, que dependem deles, permanecerão bloqueados.
3. Consultar uma execução real do GitHub Actions após a publicação das mudanças. A validação local do YAML não confirma uma execução remota.
4. O chunk lazy `IconCatalog` ainda tem cerca de 800 KB; o primeiro componente que solicitar um ícone dinâmico pode exibir o ícone Square de fallback durante o carregamento.

## Possíveis regressões

- Rotas lazy exibem brevemente “Carregando…” ao buscar seu módulo.
- Ícones dinâmicos podem exibir o fallback Square enquanto o catálogo é baixado. Nomes válidos continuam aceitos pelo catálogo completo; nomes inválidos continuam usando Square.
- A ordem e a classificação de revisões foram extraídas para um módulo sem alterar o algoritmo. Typecheck, lint, testes frontend e build passaram após a mudança.
- Não houve alteração de rotas, métodos, formatos de payload ou contratos da API.

## Recomendações para a Fase 2

- Atualizar FastAPI, Starlette, Motor e PyMongo em conjunto, validar a matriz de compatibilidade e executar a suíte backend completa antes de atualizar as versões de produção.
- Tratar os advisories npm em uma branch de atualização dedicada, validando Vitest/Tinypool, ESLint, Tailwind e PostCSS antes de atualizar lockfile e versões.
- Reduzir o chunk lazy de ícones preservando os nomes editáveis existentes; avaliar catálogo de ícones permitido ou divisão por conjunto carregado sob demanda.
- Planejar a migração dos handlers `FastAPI.on_event` para lifespan, atualmente com avisos de depreciação na coleta de testes.
- Analisar os candidatos de dependência sem import estático e a origem privada de `litellm`; manter pacotes até confirmar que imports dinâmicos, scripts e funcionalidades futuras não dependem deles.
- Acompanhar o tamanho do chunk inicial e dos chunks lazy no CI para detectar regressões de bundle.
