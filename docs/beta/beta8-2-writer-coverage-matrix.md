# Beta 8.2 — matriz reconciliada de writers

## Método e limite

O inventário C16 versionado em `backend/integration_tests/editorial_writer_inventory_c13.json` enumera 17 famílias W-01–W-17. Os 17 símbolos continuam presentes nos arquivos referenciados no commit-base. A inspeção de código confirmou as operações listadas abaixo e adicionou cobertura por operação para W-05 e W-07. Esta reconciliação não descobre jobs externos, scripts fora do checkout, processos implantados ou credenciais distribuídas; portanto, o inventário não é uma prova exaustiva do ambiente operacional.

Estados abaixo descrevem o código e as provas desta worktree. `INTEGRATED_AND_VERIFIED` aplica-se somente à operação indicada, não à família inteira.

| Writer | Caminho verificado no código | Coleções/efeitos | Estado Beta 8.2 | Evidência ou bloqueio |
|---|---|---|---|---|
| W-01 | `tracks.create_track`, `update_track`, `reorder_tracks` | `tracks`, `edit_history` | `REQUIRES_MIGRATION` | Caminhos antigos não foram migrados; reorder não carrega ator até o serviço. |
| W-02 | `tracks.delete_track` | Cascata em trilha, conteúdo, publicações, aprendizagem e histórico | `REQUIRES_OPERATIONAL_DECISION` | Exclusão destrutiva não executada; retenção e recuperação do histórico do aluno precisam de contrato. |
| W-03 | `tracks.duplicate_track` | Inserção de trilha e cópia composta | `REQUIRES_MIGRATION` | Sem autorização de origem/destino, recuperação e idempotência demonstradas. |
| W-04 | `tracks.publish_track` | Conteúdo, snapshots, publicações e versões | `REQUIRES_OPERATIONAL_DECISION` | Nenhuma publicação executada; depende de geração, IAM operacional e ADR-008. |
| W-05 | `nodes.create_node`, `reorder_nodes`; `PUT /api/nodes/{id}` / `nodes.update_node` | `nodes`, auditoria | `INTEGRATED_AND_VERIFIED` somente para `PUT` de atualização de rascunho; criação/reordenação `REQUIRES_MIGRATION` | HTTP autenticado, grant `node.update`, CAS/fencing, auditoria, replay e rejeição MongoDB de escrita direta. Sem capacidade experimental a rota PUT retorna 503. |
| W-06 | `nodes.delete_node`, `duplicate_node` | Nós, blocos, relações, progresso e reconciliação | `REQUIRES_OPERATIONAL_DECISION` | Sem operação destrutiva, cascata ou preservação de aprendizagem exercitadas. |
| W-07 | `POST /api/blocks` / `create_block`; `PUT /api/blocks/{id}` / `update_block`; `reorder_blocks`; `DELETE /api/blocks/{id}` | `content_blocks`, histórico | `INTEGRATED_AND_VERIFIED` para POST de criação e PUT de atualização; reorder/delete `REQUIRES_MIGRATION` | POST e PUT passam pela identidade FastAPI, grant por trilha, autoridade C8/C12, CAS/fence e auditoria. Criação repete com mesma operação sem duplicar. Conta Mongo comum não pode inserir, atualizar ou excluir blocos. |
| W-08 | `relations.create_relation`, `update_relation`, `delete_relation` | Relações e histórico | `REQUIRES_MIGRATION` | Escopo das duas pontas, ciclos, concorrência e efeitos curriculares não cobertos. |
| W-09 | `taxonomy` CRUD | Catálogos e conteúdo referenciado | `REQUIRES_OPERATIONAL_DECISION` | Autoridade global, versionamento e efeitos cruzados pendentes. |
| W-10 | `imports` e jobs de importação | Staging, trilha, nós, blocos, relações e versões | `REQUIRES_MIGRATION` para o importador operacional | Beta 8.2 exercitou o serviço de staging Beta 5 e seu bridge experimental, não migrou o import writer de produção. Preparador não escreve no namespace de promoção. |
| W-11 | `versions` restore/resume | Conteúdo e progresso/histórico associado | `REQUIRES_OPERATIONAL_DECISION` | Sem restore ou retomada executados; política de gerações e dados de aluno é pré-requisito. |
| W-12 | `integrity` snapshots/reconciliação | Versões, snapshots, conteúdo e progresso | `REQUIRES_MIGRATION` | Não vinculado ao protocolo de geração em runtime. |
| W-13 | `seed.py` | Usuários, trilhas, nós, blocos e catálogos | `REQUIRES_OPERATIONAL_DECISION` | Não executado. Alvo e identidade de seed precisam permanecer explicitamente descartáveis. |
| W-14 | `manage.py` comandos | Índices, migração e administração variável | `REQUIRES_OPERATIONAL_DECISION` | Não executado; precisa de classificação comando a comando. |
| W-15 | `immutable_publications` | Publicações e chunks imutáveis | `REQUIRES_MIGRATION` | Ainda não integrado à autoridade e à geração experimental. |
| W-16 | `audit.audit` | `edit_history` | `UNVERIFIED` | A nova autoridade escreve sua auditoria transacional própria; o helper legado não foi migrado. |
| W-17 | `EditorialGenerationsPoC` | Namespace PoC de gerações | `UNVERIFIED` | Não participa da composição Beta 8.2; ausência de uso no harness não prova contenção de outros processos. |

## Cobertura por operação

* Famílias históricas reconciliadas: **17/17**.
* Operações editoriais reais integradas e persistentes neste ramo: **3** — W-07 PUT (Beta 8.1, reexecutado), W-07 POST (Beta 8.2), W-05 PUT (Beta 8.2).
* Novas operações integradas nesta fase: **2**, cobrindo criação e atualização.
* Operações destrutivas integradas nesta fase: **0**. Exclusão de conteúdo, subárvore ou trilha segue bloqueada/pendente; não foi substituída por exclusão lógica.
* Escrita direta negada pelo MongoDB com usuário sintético comum: blocos `insert/update/delete`, nós `insert/update/delete` e `track_publications.insert`; preparador negado no namespace de heads experimentais.
* Contenção por role comum testada não equivale a migração ou contenção global dos 17 writers. A role privilegiada de autoridade continua capaz de escrever nas coleções necessárias.
* Writers somente leitura verificados: **0**. Outros writers desabilitados por completo: **0** demonstrados.

## Priorização

W-05 PUT e W-07 POST/PUT foram escolhidos por serem mutações de rascunho, com alvo identificável por trilha, e permitirem exercitar a cadeia HTTP → autenticação → grant → CAS/fence → persistência → auditoria sem tocar publicação ou dados de aprendizagem. W-02, W-04, W-06 e W-11 permanecem adiados por efeitos destrutivos, publicação ou política de retenção ainda não ratificada. W-01, W-03, W-08, W-09, W-10, W-12, W-13, W-14, W-15, W-16 e W-17 exigem adaptação ou decisão específica listada acima.

## Limite operacional

As rotas experimentais de POST de bloco e PUT de nó retornam 503 sem composição explícita da capacidade Beta 8.1. O PUT de bloco já possuía esse comportamento. O serviço editorial ainda é exercitado no mesmo processo Python da aplicação durante o harness; a prova não demonstra isolamento de processo ou distribuição de segredos em runtime operacional.
