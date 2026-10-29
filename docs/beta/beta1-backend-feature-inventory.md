# Beta 1 — inventário backend

Base de referência: C16 `6c227fa6`. A inspeção estática prova presença de implementação, não operação. Nenhum banco ou serviço foi iniciado.

| ID | Domínio | Estado | Evidência no código | Lacuna/necessidade beta |
|---|---|---|---|---|
| B-01 | Cadastro, login, JWT, refresh | `IMPLEMENTED_IN_INSPECTED_CODE` | `backend/routes_auth.py`, `security.py` | Rodar jornada E2E e validar envio email em QA |
| B-02 | Sessões e logout/revogação | `IMPLEMENTED_IN_INSPECTED_CODE` | `backend/services/sessions.py` | Persistência real/topologia não verificada |
| B-03 | Verificação email/reset | `IMPLEMENTED_IN_INSPECTED_CODE` | Rotas `/auth/register`, `/verify-email`, reset | Entrega SMTP real e abuso pendentes |
| B-04 | Permissões | `PARTIALLY_IMPLEMENTED` | `constants.py` static `PERMISSIONS`; `permissions.py` | `admin`/`editor` têm `content.write` global; grant por trilha não existe no código inspecionado |
| B-05 | Trilhas/unidades/blocos | `IMPLEMENTED_IN_INSPECTED_CODE` | `routes_content.py`, `services/tracks.py`, `nodes.py`, `blocks.py` | Bundle curricular C16 todo draft/não importado |
| B-06 | CRUD/editor/ordenação | `PARTIALLY_IMPLEMENTED` | CRUD em `routes_content.py` e services | C7–C16 documentam writers concorrentes e bypass; não existe contenção global provada |
| B-07 | Importação | `IMPLEMENTED_IN_INSPECTED_CODE` | `routes_import.py` chama `services/imports.py` | Contrato C16 legacy; bundle tipado da worktree migratória não foi integrado; não executar nesta fase |
| B-08 | Publicação e snapshot | `PARTIALLY_IMPLEMENTED` | `services/tracks.py::publish_track`, `versions.py::snapshot_track`, `integrity.py` | Atomicidade composta e concorrência não comprovadas |
| B-09 | Restauração | `PARTIALLY_IMPLEMENTED` | `routes_versions.py`, `services/versions.py::apply_snapshot` | Falha no meio/conflito com escrita concorrente não comprovados |
| B-10 | Quiz objetivo | `IMPLEMENTED_IN_INSPECTED_CODE` | `activity_publications.py`, `services/activities.py`, `activity_evaluator.py` | Funcionalidade do código não está no bundle curricular C16 |
| B-11 | Tentativas versionadas | `IMPLEMENTED_IN_INSPECTED_CODE` | `/activities/{id}/attempts`; collection `activity_attempts` | E2E não executado nesta auditoria |
| B-12 | Progresso e reconciliação | `IMPLEMENTED_IN_INSPECTED_CODE` | `services/progress.py`, `routes_progress.py` | Preservação com restore/delete requer teste de integração |
| B-13 | Exercícios escritos | `IMPLEMENTED_IN_INSPECTED_CODE` | `services/submissions.py`, `routes_submissions.py` | Correção manual; E2E fonte existe, sem execução |
| B-14 | Correção manual | `IMPLEMENTED_IN_INSPECTED_CODE` | `grade_submission`, `Grading` | Validar papéis, escopo e fluxo completo |
| B-15 | Notas, revisão, pré-requisitos | `IMPLEMENTED_IN_INSPECTED_CODE` | `learning.py` | Não equivale a domínio por competência |
| B-16 | Tutor IA | `NOT_FOUND` | Sem rota/serviço correspondente encontrado | Dependências `google-genai`/`openai` não provam recurso |
| B-17 | Executor de código seguro | `NOT_FOUND` | Sem sandbox/subprocess de produto encontrado | `CodeBlock` é apresentação; não executar código de aluno |
| B-18 | Gamificação RPG | `NOT_FOUND` | Sem serviços/modelos de XP/conquista encontrados | Adiar |
| B-19 | Pagamentos/entitlement Premium | `NOT_FOUND` | Sem rotas/modelos de plano encontrados; Stripe está em requirements | Gratuidade beta; comercial depois |
| B-20 | Convite/Pioneiros | `NOT_FOUND` | Sem serviço/tela/API do domínio encontrados | Convite manual requer processo de operação aprovado |
| B-21 | Certificado/portfólio/comunidade | `NOT_FOUND` | Não encontrados nas áreas inspecionadas | Depois da beta |
| B-22 | Suporte/feedback beta | `PARTIALLY_IMPLEMENTED` | Feedback instrucional em submission; sem caixa de feedback de produto | Definir canal/triagem |
| B-23 | Administração | `IMPLEMENTED_IN_INSPECTED_CODE` | Rotas de trilha, import, taxonomia, versões, usuário e correção | Sem escopo de escrita por trilha |
| B-24 | Auditoria editorial | `PARTIALLY_IMPLEMENTED` | `backend/audit.py`; C7–C16 | Não é atômica nem comum a todos escritores |

## Execução e fluxo

`backend/database.py` usa `AsyncMongoClient`; os handlers/services são assíncronos. `server.py` registra routers e ciclo de vida; `compose.yaml` declara MongoDB 7 local com volume, não iniciado. Quiz é publicação imutável com tentativa ligada a `published_version_id`; exercícios de texto usam `submissions` e correção humana. O importador C16 executa operações em fases e usa locks/job; esses locks não demonstram coordenação contra todos os outros writers.

## Testes nesta execução

Python 3.11.9 em venv temporário já existente: `unit_tests/test_snapshot_safety.py`, `test_editorial_readiness_contract.py`, `test_editorial_writer_containment_contract.py`: **14 passed**. Os seis testes de snapshot usam doubles/monkeypatch. Não foram repetidas regressões persistentes C8–C16 nem todas as suítes backend. O relatório C14 de 183 testes é histórico, não resultado Beta atual.

## Recomendação

Para beta, priorizar leitura, quiz objetivo publicado e versão-pinado, progresso e exercício com correção humana somente após reconciliação e QA. Não habilitar tutor, código executável ou pagamentos por existir dependência. Manter conteúdo estável enquanto o risco de escritor legado não tiver contenção ou restrição aprovada e verificável.
