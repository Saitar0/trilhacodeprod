# Trilha Code — Fase 2A.3: Padronização dos routers e serviços

## 1. Mapeamento completo dos routers

| Router | Endpoints e responsabilidade HTTP | Serviço que executa o fluxo |
| --- | --- | --- |
| `backend/routes_auth.py` | `POST /auth/register`, `POST /auth/login`, `POST /auth/logout`, `GET /auth/me`, `POST /auth/refresh`, `GET/PUT /profile`, `GET /users`, `PUT /users/{user_id}/role` | `services.auth` para registro, login e limite de tentativas, leitura do usuário no refresh, perfil, listagem e troca de papel. Cookie, extração do endereço do cliente, token e dependências HTTP ficam na rota. `auth/me` e `profile` GET retornam o usuário resolvido por `current_user`. |
| `backend/routes_import.py` | `POST /import/track` | `services.imports.run_import` (já existia). A rota apenas recebe payload, `dry_run` e a dependência `content.write`. |
| `backend/routes_progress.py` | `POST /progress`, `POST /progress/visit`, `GET /progress/tracks/{track_id}`, `GET /progress/overview`, `GET /progress/history` | `services.progress` para persistência, validação de estado, desbloqueio, eventos, agregação e montagem dos retornos. |
| `backend/routes_submissions.py` | `GET /submissions/mine`, `PUT /submissions/draft`, `POST /submissions/submit`, `GET /submissions`, `GET /submissions/{sub_id}`, `POST /submissions/{sub_id}/claim`, `POST /submissions/{sub_id}/grade` | `services.submissions` (já existia) para consultas, avaliação, tentativas, histórico, progresso e eventos. A rota mantém autorização, schemas e serialização HTTP. |
| `backend/routes_taxonomy.py` | `GET /meta`; CRUD de `/taxonomies`, `/tags` e `/block-types` | `services.taxonomy` para consultas, validações de domínio, gravações e remoção de referências de tags. |
| `backend/routes_versions.py` | `GET /tracks/{track_id}/compare`, `POST /tracks/{track_id}/versions/{version_id}/restore` | `services.versions` (já existia). Snapshots, comparação, leases, backups, restauração, reconciliação e auditoria permanecem no serviço. |

As rotas de listagem e leitura individual de versões (`GET /tracks/{track_id}/versions` e `GET /versions/{version_id}`) ficam em `backend/routes_content.py`. A Fase 2A.2 já delegou essas consultas para `services.versions.list_track_versions` e `get_version`; não foram refeitas nesta fase.

## 2. Problemas encontrados na auditoria

Os números abaixo indicam as linhas que continham as operações antes da extração desta fase. Essas consultas e mutações foram removidas dos routers.

| Arquivo e linhas antes da extração | Achado | Impacto | Risco de regressão |
| --- | --- | --- | --- |
| `backend/routes_auth.py:42-49, 59-69, 92-98, 109-110, 116-117, 122-128` | O router consultava e alterava usuários e tentativas de login, fazia hash/verificação da senha e aplicava regras de registro, lockout e alteração de papel. | **Alto** — autenticação, controle de força bruta e permissões administrativas. | **Médio** — manter email normalizado, limite de cinco tentativas em 15 minutos, cookie de sessão, retorno público com permissões e auditoria de troca de papel. |
| `backend/routes_progress.py:24-35, 39-58, 63-74, 78-100, 103-114` | O router fazia consultas e escritas em `nodes`, `progress`, `user_track_state` e `learning_events`, além da agregação de conclusão e enriquecimento do histórico com títulos. Também coordenava bloqueios pedagógicos. | **Alto** — estado de aprendizagem, conclusão, tentativas e trilhas bloqueadas. | **Médio** — preservar o momento de início/conclusão, incremento de tentativas, idempotência da visita, eventos e cálculo de locks. |
| `backend/routes_taxonomy.py:33-48, 53-59, 64-71, 76-88, 93-103` | O router listava metadados e gravava taxonomias, tags e tipos de bloco. A remoção de tag também atualizava referências em nós e trilhas. | **Médio**; **alto para a integridade referencial** da remoção de tags. | **Baixo a médio** — manter ordenação, normalização de slug, contagem de ordem, validações de duplicidade e limpeza das referências. |
| `backend/routes_import.py:10-12` | Não havia acesso Mongo no router; importação já delegada. | **Baixo**. | **Baixo** — nenhum fluxo foi alterado. Persistência e validação de importação permanecem no serviço existente. |
| `backend/routes_submissions.py:28-66` | Não havia consultas nem agregações Mongo no router; todos os endpoints chamavam `services.submissions`. Regras de avaliação e mutações de progresso já estavam fora da camada HTTP. | **Alto no domínio**, mas a separação já era adequada. | **Baixo nesta fase** — nenhum comportamento de submissão foi modificado. |
| `backend/routes_versions.py:12-19` | Não havia consultas Mongo no router; comparação e restauração já estavam em `services.versions`. | **Alto para histórico e integridade**, mas a separação já era adequada. | **Baixo nesta fase** — nenhum código de snapshot ou restauração foi alterado. |

### Consultas, atualizações e agregações identificadas

- **Auth:** `find_one`, `insert_one`, `update_one`, `delete_many`, `find().sort().skip().limit()` nas coleções de usuários e tentativas de login; sem agregação.
- **Progress:** leituras e atualizações em progresso e estado da trilha, inserções de eventos e nós; `aggregate` agrupava nós concluídos por trilha. A listagem de histórico fazia busca adicional por títulos.
- **Taxonomy:** consultas ordenadas para `/meta`; buscas de duplicidade; inserções; atualizações e remoções de taxonomia/tipo; `count_documents` para ordem; remoção de tag seguida de `$pull` em `nodes` e `tracks`.
- **Import, submissions e versions:** routers sem acesso direto ao banco. As consultas e agregações do ciclo de submissões já ficam em `services.submissions`; planos e gravações da importação em `services.imports`; versionamento e restauração em `services.versions`.

### Código duplicado e serviços reutilizáveis

- Não foi encontrada a mesma consulta ou agregação implementada em mais de um dos seis routers. Os routers de importação, submissões e versões já reutilizavam serviços.
- `_public` em `routes_auth.py` era uma projeção local usada em mais de uma operação daquele router; foi concentrada em `services.auth._public`, evitando que os handlers conheçam a representação pública do usuário.
- `_node` e `_event` em `routes_progress.py` eram auxiliares compartilhados pelos handlers de progresso; foram movidos junto com seus consumidores para `services.progress`.
- Foram reutilizados `services.imports.run_import`, `services.submissions`, `services.versions`, `learning.assert_unlocked`, `learning.track_locks`, `audit.audit`, `security`, `serialization` e `services.common.get_document`. Nenhum serviço genérico adicional era necessário.

## 3. Alterações implementadas

- Extraído `backend/services/auth.py`: registro, autenticação e lockout, busca do usuário durante refresh, atualização de perfil, paginação de usuários, troca de papel e projeção pública com permissões. A rota continua responsável por cookies, token e decisão de IP confiável baseada na requisição.
- Extraído `backend/services/progress.py`: validação de status, resolução de nó, bloqueios, escrita de progresso e estado, eventos, visita, agrupamento de respostas por nó/bloco, resumo agregado e histórico com títulos.
- Extraído `backend/services/taxonomy.py`: carregamento de metadados, CRUD de taxonomias, tags e tipos de bloco, incluindo a limpeza `$pull` de tags em nós e trilhas.
- Convertidos os routers correspondentes em adaptadores HTTP. Paths, verbos, schemas de entrada e resposta, dependências e mensagens de erro foram mantidos.
- Não foram alterados `services.imports`, `services.submissions` nem `services.versions`. Motor continua sendo usado; não houve migração para PyMongo Async.
- As alterações locais preexistentes das fases anteriores e de outras áreas do worktree foram preservadas. Não houve push ou deploy.

## 4. Serviços criados ou reutilizados

**Novos:**

- `services.auth` — regras e persistência de autenticação e administração de usuários.
- `services.progress` — domínio e persistência do progresso do aluno.
- `services.taxonomy` — leitura e manutenção das classificações e tipos de bloco.

**Reutilizados sem reescrita:**

- `services.imports.run_import` para importações.
- `services.submissions` para ciclo de submissão e correção.
- `services.versions` para listagem/leitura de versões, comparação e restauração.
- `learning.assert_unlocked` e `learning.track_locks` para as regras pedagógicas já compartilhadas.
- `audit.audit`, `security`, `serialization` e `services.common.get_document` nos fluxos em que já eram usados.

Não foi criada camada genérica de repositório nem abstração adicional de banco.

## 5. Testes adicionados

Em `backend/tests/backend_test.py`:

- `TestAuth.test_update_profile_and_admin_role_change`: verifica atualização de perfil e alteração administrativa de papel.
- `TestMeta.test_tag_and_block_type_endpoints`: verifica criação/remoção de tag, limpeza das referências persistidas em trilha e nó, e criação/atualização de tipo de bloco.
- `TestProgress.test_visit_and_complete` agora também verifica o histórico de progresso e o título resolvido do nó.

## 6. Resultados das verificações

Executado com Python **3.11** (`backend/.venv311`) e MongoDB **7 temporário**, publicado somente na porta `27023`. A fixture criou um banco aleatório `test_*` e o descartou ao final.

- Ruff (`python -m ruff check .`): **passou**.
- Compilação de arquivos Python (`py_compile`): **55 arquivos compilados**.
- Suíte completa (`python -m pytest -q`): **54 passaram**, **5 avisos de depreciação**.
- `git diff --check`: **passou**. O Git exibiu apenas avisos de conversão de fim de linha LF/CRLF em arquivos já modificados no worktree.

Os avisos de teste são de `python_multipart`/Starlette e do uso de `on_event` pelo FastAPI em `backend/server.py`; não falharam testes e não foram introduzidos pelos novos serviços.

## 7. Riscos e regressões possíveis

- A suíte cobre os comportamentos existentes e os novos caminhos HTTP, mas não exercita concorrência entre requisições simultâneas de cadastro, criação de taxonomia/tag/tipo de bloco ou visita. As verificações de duplicidade existentes continuam sendo consulta seguida de inserção; sua atomicidade deve ser avaliada separadamente sem alterar índices ou contratos nesta fase.
- A remoção de tag continua executando a exclusão e os dois `$pull` sem transação, como antes. Uma falha parcial do banco entre essas operações pode deixar referências antigas; alterar essa garantia exigiria avaliar suporte transacional e topologia de produção.
- Cinco avisos de depreciação seguem pendentes no servidor/dependências; a migração do ciclo de vida FastAPI não foi parte deste escopo.
- A fachada `core.py` e eventuais imports externos ainda devem ser tratados conforme a decisão de compatibilidade registrada na Fase 2A.1.

## 8. Pendências recomendadas para a Fase 2A.4

- Auditar os routers que ficaram fora do escopo desta fase e confirmar que operações Mongo e regras de domínio estejam nos serviços apropriados.
- Avaliar garantias concorrentes para criação de usuários, taxonomias, tags e tipos de bloco, incluindo índices e respostas de conflito, sem presumir mudança de contrato.
- Avaliar uma estratégia consistente de falha/atomicidade para remoção de tags e outras mutações em múltiplas coleções.
- Decidir sobre a retirada futura da fachada `core.py` após confirmar consumidores externos.
- Manter Motor nesta etapa; qualquer migração de driver deve ser uma fase independente com compatibilidade, ciclo de vida e testes dedicados.
