# Trilha Code — PRD

## Problema original
Plataforma modular de ensino técnico em programação, altamente escalável e personalizável. Fase 1 = fundação: modelagem orientada a dados, CMS interno forte, área do aluno fundacional, design system, sem conteúdo hardcoded. Stack obrigatória: React + TypeScript, FastAPI, MongoDB.

## Escolhas do usuário
- Auth JWT email/senha (cookies httpOnly), papéis admin/editor/student
- Dependências apenas visuais (flag `enforced` + `track.settings.enforce_prerequisites` prontos para bloqueio futuro)
- Versionamento simples: snapshot completo ao publicar + histórico de edição
- Tema: designer decidiu (dark slate + emerald, Outfit / Plus Jakarta Sans / JetBrains Mono)

## Arquitetura
- Backend: `core.py` (db, auth, permissões por papel), `routes_auth.py`, `routes_taxonomy.py` (meta, taxonomias, tags, block types), `routes_content.py` (tracks, nodes, blocks, relations, publish/versions, search, history, stats), `routes_progress.py`, `seed.py`
- Coleções: users, tracks, nodes (árvore genérica com `kind` + `parent_id` + `order`; hierarquia e nomenclatura por trilha), content_blocks (schema único `type` + `data`), block_types (registro com schema de campos → formulários dinâmicos), taxonomies (pedagogical_type, requirement, depth, relation_type), tags, relations, track_versions, edit_history, progress (nó e bloco), learning_events, user_track_state, login_attempts
- Frontend TS: pages (student/admin), components (admin, student, blocks, common), hooks/useData (react-query), lib/tree (árvore, progresso, filtros), tipagens em `types/`

## Implementado (2026-06)
- Auth + papéis + permissões; perfis; gestão de usuários/papéis
- Admin: dashboard, CRUD/duplicar/derivar/reordenar/excluir trilhas, editor em árvore (drag & drop + setas, criação rápida aninhada, duplicar subárvore, mover pai), formulário de nó (tipo, caráter, profundidade, orientação, notas internas, tags, liberação por data, status), editor de blocos schema-driven com preview, relações pedagógicas, publicar com snapshot, versões, histórico, taxonomias/tags/tipos de bloco editáveis, nomenclatura por trilha
- Aluno: catálogo com progresso e retomada, overview da trilha, sidebar em árvore com filtros/busca, leitor com 15 tipos de bloco (quiz/checklist interativos com progresso por bloco), marcar concluído, anterior/próximo, painel de pré-requisitos/libera/complementos/revisitas/próximo passo; preview para equipe
- Seed: Trilha Code com 3 fases, 4 módulos, 1 submódulo, 9 tópicos, blocos placeholder, 6 relações

## Fase 2 implementada (2026-06)
- Pré-requisitos bloqueantes reais: `track.settings.enforce_prerequisites` + `relation.enforced`; locks calculados no backend (herança por ancestral), enforcement em /nodes, /progress e /submissions; proteção contra ciclos e contra pré-requisito de pai/filho; endpoint de validação; UI com cadeado, painel de desbloqueio, filtro "Bloqueado"
- Submissões: coleção `submissions` (tentativas, status draft/submitted/in_review/graded/returned, rubrica por critérios em block.data.criteria, histórico); capacidade "submission" no registro de block_types; fila /admin/correcoes com filtros; permissão `submissions.grade` (admin+editor)
- Notas (`notes`, por tópico/bloco, autosave) e revisões (`reviews`: hoje/em breve/depois/sugerida pela profundidade/data; histórico de resultado; campos ease/interval prontos para repetição espaçada); página /estudos; aviso no catálogo
- Versões: compare (estado atual ou snapshots) com diff de trilha/itens/blocos/relações; restauração com confirmação vN, backup automático, nova versão `restore`, auditoria; página /admin/trilhas/:id/versoes

## Backlog
- P1: correção automática parcial (objetivos), notas por critério, lembretes de revisão por email, repetição espaçada
- P1: upload de anexos (object storage)
- P2: recomendações inteligentes; analytics a partir de learning_events; múltiplos estilos visuais de trilha; páginas públicas; recuperação de senha
