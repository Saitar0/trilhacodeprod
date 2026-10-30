# Matriz de integração — projetos curriculares (14H.2)

**Estado:** leitura arquitetural e projeção offline. Alternativas futuras são propostas; nenhuma política operacional foi aprovada nesta etapa.

## Compatibilidade atual

| Conceito | Comportamento/modelo existente | Situação para `ProjectSpec` | Lacuna / limite |
| --- | --- | --- | --- |
| Projeto e escopo | `ProjectSpec` no contrato intermediário; sem coleção/serviço operacional correspondente | **Representável offline** | Importador, API e frontend operacionais não possuem entidade de projeto curricular tipado |
| Entrega/marco | `ProjectDelivery` e `ProjectMilestone` preservam refs, corpo, ordem e relações no contrato | **Representável offline** | Não são entidades persistidas/submetíveis de primeira classe; não converter entre os dois tipos |
| Submissão de aluno | `backend/services/submissions.py`, `/api/submissions`, `backend/schemas/submissions.py`; chave operacional por usuário/bloco, com nó e curso | **Não compatível diretamente** | Não há `project_ref`, versão de projeto, `delivery_ref`/`milestone_ref`, tipos de evidência ou versão imutável de critérios |
| Correção manual | Rotas de submissão e permissão `submissions.grade` corrigem blocos genéricos; armazenamento de resultado/feedback por submissão | **Parcial, não reutilizado** | Não define revisão de entrega, rubrica de projeto, múltiplos alvos ou histórico por versão de projeto |
| Progresso | `backend/services/progress.py` e schema usam `user_id`, `node_id` e `block_id`; cliente pode registrar status genérico | **Não compatível como conclusão de projeto** | Não há chave por projeto/entrega nem política para checklist; a projeção não escreve progresso |
| Quiz | `backend/services/quizzes.py` mantém versão, tentativa, nota e revisão próprias | **Separado** | Limite/nota/revelação de quiz não se transferem a entrega, marco ou rubrica de projeto |
| Rubrica/checklist/aceite | Tipos e referências existem no contrato intermediário; validação de alvos e tipos em `validation.py` | **Referenciáveis no snapshot interno** | Exposição pública, preenchimento e avaliação operacional carecem de audiência e fluxo aprovados |
| Persistência editorial 14F | `activity_persistence.py` armazena revisões editoriais tipadas isoladas para seis tipos de atividade | **Não é modelo de projeto** | Sem `ProjectSpec`, entrega, marco, submissão ou progresso de projeto; não conectado a rotas |
| Importador legado | `backend/import_payload.py`, `backend/routes_import.py` validam/aceitam o formato legado; a matriz 14A classifica projetos/componentes como incompatíveis | **Bloqueado para importação** | Adaptar ao bloco genérico perderia hierarquia, identidade, alvos, opções e distinção formal; bundle versionado permanece fail-closed |
| Frontend curricular | `NodeReader` e `BlockRenderer` trabalham com nó/bloco; `TypedActivityRenderer` 14G representa seis tipos de atividade | **Não integrado** | Não há leitor de projeto ou navegação versão→entrega/marco; nenhuma API para esta projeção |
| Conteúdo compartilhado | `backend/curriculum_contract/shared_content.py` oferece identidade canônica/colocação offline | **Compatível apenas como contrato de leitura** | Não há política operacional de progresso por colocação nem ligação automática de projeto a colocações |

## Matriz de decisões que exigem aprovação

| Decisão pendente | Fato observado | Opções a considerar | Recomendação técnica existente/proposta | Situação humana |
| --- | --- | --- | --- | --- |
| Versão de projeto/entregas | O contrato tem IDs e hashes/proveniência, mas não tem campo de versão de projeto; há 20 entregas e 36 marcos | Snapshot imutável do projeto inteiro; versões separadas por componente; snapshot de projeto que pinne refs/hash de componentes | [PROPOSTA] Snapshot de projeto imutável com componentes pinados; alteração cria nova versão e preserva anteriores. Decidir também compatibilidade de versões de rubrica/aceite | **Pendente** |
| Histórico de submissões | Sistema genérico é por bloco; não por projeto/entrega/versionamento | Reutilizar submissão genérica; coleção/fluxo próprio de projeto; evidências externas com metadados | [PROPOSTA] Identidade futura por usuário + projeto + versão + componente e histórico append-only; sem compartilhar automaticamente com submissões de quiz/exercício | **Pendente** |
| Tipos de evidência aceitos | Bundle não define upload/repositório/anexo como política operacional | Texto; arquivo; URL/commit; combinação; evidência apenas em sistema externo | [PROPOSTA] Allowlist explícita por projeto/componente, limites, MIME, retenção, antivírus e privacidade antes de qualquer upload | **Pendente** |
| Correção manual | Existe correção manual genérica, sem entidade projeto/versão/entrega | Adaptar painel de exercícios; fila de revisão de projeto; revisão sem pontuação | [PROPOSTA] Fluxo próprio que referencia versão e componente, preserva histórico e exige permissão explícita; não reutilizar automaticamente estados `approved/rejected` | **Pendente** |
| Visibilidade de rubricas, checklists e aceites | O contrato não contém classificação de audiência nesses blocos | Staff-only; aluno vê rubrica antes da submissão; aluno vê critérios sem descritores/nota; audiência por bloco | [IMPLEMENTADO apenas offline] Projeção pública omite payload desses blocos. [PROPOSTA] Definir allowlist por papel e momento de revelação | **Pendente** |
| Checklist informativo ou persistente | `ChecklistBlock` preserva itens; não há identidade/progresso operacional de item de projeto | Lista instrucional estática; estado por aluno/projeto/versão/componente/item; híbrido | [PROPOSTA] Começar como conteúdo estático se a decisão de produto concordar; estado persistente exigiria IDs estáveis, histórico e regra de reabertura | **Pendente** |
| Seleção de stack | Bundle tem oito opções em dois projetos; 15 projetos têm `stack_selected: null`, `variants: []` | Escolha editorial antes da publicação; escolha individual por aluno/versão; manter apenas lista sem seleção | [IMPLEMENTADO] Preservar oito opções internamente e manter `null`/variantes vazias. [PROPOSTA] Se houver seleção individual, guardar no contexto de projeto/versionamento de aluno; não criar `ProjectVariant` para cada opção sem decisão | **Pendente** |
| Publicação e permissões | A plataforma tem `content.write`, `content.publish` e endpoint de importação legado protegido; projetos tipados não têm rota | Reutilizar permissões de conteúdo; permissão `projects.publish` própria; publicação em duas etapas | [PROPOSTA] Separar validação estrutural, revisão editorial e publicação; decidir se `content.publish` basta ou se projeto requer permissionamento específico e auditoria | **Pendente** |
| Compatibilidade com progresso atual | Progresso de conteúdo é por usuário/nó/bloco; 1.001 scopes compartilhados seguem `undecided` | Não registrar progresso de projeto; conclusão por entrega; conclusão por projeto; vincular a submódulo; híbrido | [PROPOSTA] Não mapear estado de leitura nem `quiz_passed` a projeto. Definir chave/versionamento e migração só após política específica; não tocar nos 55 relacionamentos curriculares | **Pendente** |

As recomendações acima não alteram o contrato, progresso ou comportamento da aplicação. A decisão sobre progresso compartilhado da 14H.1 permanece independente e não foi resolvida por esta etapa.

## Critérios de gate para 14H.3

Antes de persistir projetos, obter decisão humana sobre:

1. Identidade/versionamento de snapshots de projeto e pinagem de componentes.
2. Modelo de submissão, evidências permitidas, retenção e recuperação de falhas.
3. Política de correção manual e permissões.
4. Audiência de rubrica, checklist, aceite e conteúdo associado.
5. Checklist informativo versus estado individual persistente.
6. Stack editorial versus seleção individual.
7. Relação de projeto com progresso curricular e com histórico legado.
8. Requisitos de publicação, rollback, idempotência e isolamento entre versões.

Depois das decisões, 14H.3 deve começar como persistência isolada em MongoDB descartável, sem conectar importador ou rotas estudantis até homologação separada. Esta etapa não realizou esses passos.
