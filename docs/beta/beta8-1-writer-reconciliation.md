# Beta 8.1 — Reconciliação individual dos writers

## Método e significado

Os 17 itens do inventário versionado `backend/integration_tests/editorial_writer_inventory_c13.json` foram reconciliados com os arquivos e símbolos do commit-base Beta 8. Os itens permanecem presentes. O inventário é estático: não comprova call graph exaustivo, processos externos, jobs implantados ou credenciais efetivamente distribuídas. A coluna Beta 8.1 classifica somente o que foi exercitado nesta worktree; não altera o estado histórico `runtime=NOT_VERIFIED`.

| ID | Writer e efeito principal | Coleções/operações (inventário C16) | Estado Beta 8.1 e evidência | Bloqueio/ação seguinte |
|---|---|---|---|---|
| W-01 | `services/tracks.py`: criar, editar e reordenar trilhas | `tracks`, `edit_history`; insert/update | `REQUIRES_MIGRATION`; caminho direto não exercitado | Integrar grant da trilha, CAS/fence, auditoria na transação e identidade do ator em reorder |
| W-02 | `services/tracks.py`: exclusão em cascata | trilhas, nós, blocos, relações, progresso, tentativas, publicações e versões; delete | `REQUIRES_OPERATIONAL_DECISION`; não executado | Política de retenção/recuperação de dados de aluno e contrato composto antes de qualquer uso |
| W-03 | `services/tracks.py`: duplicação | trilhas, nós, blocos, relações e histórico; insert | `REQUIRES_MIGRATION`; não executado | Grants de origem/destino, retry idempotente e recuperação de cópia parcial |
| W-04 | `services/tracks.py`: publicação | trilhas, blocos, snapshots, publicações e versões; insert/update | `REQUIRES_OPERATIONAL_DECISION`; nenhuma publicação foi executada | Geração imutável, head atômico, leitores compatíveis, autorização editorial e ADR-008 |
| W-05 | `services/nodes.py`: criar, editar e reordenar nós | `nodes`, `edit_history`; insert/update | `REQUIRES_MIGRATION`; não executado | Resolver trilha por relações, grant e CAS de ordenação |
| W-06 | `services/nodes.py`: excluir/duplicar nós e subárvores | nós, blocos, relações, progresso e histórico; delete/insert/update | `REQUIRES_OPERATIONAL_DECISION`; não executado | Preservação do histórico do aluno e operação composta recuperável |
| W-07 | `services/blocks.py`: CRUD e ordenação | `content_blocks`, `edit_history`; insert/update/delete | `INTEGRATED_AND_VERIFIED — PUT update somente no harness`. HTTP real usa serviço existente + C12/C8/C10; identidade runtime negada pelo Mongo; chamada direta legada também negada | POST, DELETE e reorder não migrados; serviço autoridade ainda pode escrever direto por privilégio de coleção |
| W-08 | `services/relations.py`: CRUD de relações | `relations`, `nodes`, histórico; insert/update/delete | `REQUIRES_MIGRATION`; não executado | Escopo das duas pontas, validação de ciclo, revisão e transação |
| W-09 | `services/taxonomy.py`: taxonomias, tags e tipos | catálogos, nós e trilhas; CRUD/update_many | `REQUIRES_OPERATIONAL_DECISION`; não executado | Definir autoridade global/versionamento e impedir efeitos cruzados |
| W-10 | `services/imports.py`: importação e jobs | locks/jobs, trilhas, nós, blocos, relações, versões e histórico | `REQUIRES_MIGRATION`; importador operacional não chamado | A preparação real Beta 5 foi testada separadamente em identidade limitada; import writer permanece fora da autoridade |
| W-11 | `services/versions.py`: restaurar/aplicar e retomar jobs | jobs, trilhas, nós, blocos, relações, versões, progresso e histórico | `REQUIRES_OPERATIONAL_DECISION`; não executado | Fencing por lote, recovery e política de preservação do aluno |
| W-12 | `backend/integrity.py`: snapshots, versões e reconciliação | versões, snapshots, conteúdo, submissões e progresso | `REQUIRES_MIGRATION`; não executado | Vincular snapshot a uma revisão única e proibir mutação de estado do aluno |
| W-13 | `backend/seed.py`: seeds de conteúdo/demo | usuários, trilhas, nós, blocos e catálogos; insert/upsert | `REQUIRES_OPERATIONAL_DECISION`; não executado | Alvo explícito descartável e identidade de seed isolada |
| W-14 | `backend/manage.py`: migrações/índices/comandos | varia por comando; escrita e administração de índice | `REQUIRES_OPERATIONAL_DECISION`; comandos não executados | Classificar comando a comando e limitar alvo/identidade |
| W-15 | `services/immutable_publications.py`: preparação de publicação | publicações e chunks; insert/update/delete | `REQUIRES_MIGRATION`; não executado | Integrar ao contrato de geração/head e auditoria |
| W-16 | `backend/audit.py::audit`: histórico funcional | `edit_history`; insert | `UNVERIFIED`; a nova fatia grava seu histórico C8 separado, não migra helper legado | Unificar contexto/transação do ator e garantir falha segura em cada writer |
| W-17 | `services/editorial_generations_poc.py::EditorialGenerationsPoC` | namespace PoC de geração; insert/update | `UNVERIFIED`; não montado no harness Beta 8.1 | Manter isolamento explícito e verificar ausência de credenciais/rotas compartilhadas |

## Contagens honestas

* Inventariados: 17/17.
* Integrados e verificados: 1 item parcialmente, somente a operação PUT de W-07.
* Contidos pelo role comum do MongoDB: operação de update de bloco no harness; não equivale a contenção de todos os escritores ou credenciais operacionais.
* Somente leitura verificados: nenhum writer do inventário.
* Desabilitados no startup comum: somente a capacidade experimental de PUT protegido, ausente sem composição explícita; não se afirma que os outros writers estejam desabilitados.
* Pendentes de migração/decisão: 16 itens e as três operações não cobertas de W-07.
* Cobertura operacional desconhecida: 17/17.

## Matriz de identidade e privilégio exercitada

| Identidade sintética | Acesso no harness | Prova |
|---|---|---|
| `beta8-1-runtime` | leitura de conteúdo; usuários/sessões/login; sem escrita em `content_blocks` ou `track_publications` | Update Mongo direto e serviço `update_block` legado negados pelo servidor MongoDB |
| `beta8-1-preparer` | coleções Beta 5 de staging, apenas | `CurriculumStagingService.prepare` funcionou; escrita em `_beta8_experimental_heads` negada |
| `beta8-1-authority` | coleções C8/C12 específicas, update de bloco, inserts de history/auditoria e fatos de sessão/usuário transacionais | Caminho autorizado e auditoria persistiram; role não lê coleções de auditoria |
| provisionador root | criação/validação/cleanup exclusivo do harness | Nunca é credencial da API; limitado a execução descartável e removido com o contêiner |

MongoDB não pode restringir update a uma função Python ou a um `_id`. A identidade autoridade consegue escrita direta nas coleções que precisa. Portanto, a prova contém o runtime comum e o preparador, mas não protege a autoridade de seu próprio bypass, não identifica distribuição operacional de segredos e não demonstra contenção global.

Veredito da Entrega B: **WRITERS SELECIONADOS INTEGRADOS E CONTIDOS — COBERTURA GLOBAL PENDENTE**.
