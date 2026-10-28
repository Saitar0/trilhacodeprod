# ADR-007 — Migração gradual e coexistência segura

**Status:** Proposed
**Tipo:** estratégia de rollout proposta; nenhuma etapa está autorizada ou implementada.
**Baseline:** e5bf3147a7f9a5ee02e1a011ffcbf1fb7e0cc636.

## 1. Contexto

O legado contém diversos writers e readers, import recuperável, restore destrutivo e leitura pública baseada em documentos vivos. A auditoria B.2 e seu rollout documentam esses caminhos. Shadow write independente por rota pode duplicar efeitos e divergir.

## 2. Problema

Cutover incompleto deixa escritores capazes de mudar a origem ou leitores capazes de combinar geração e documentos vivos. Uma flag única pode ativar comportamentos incompatíveis de uma vez.

## 3. Requisitos

- Flags separadas para revisão, build sombra, comparação, reader admin, reader público, seleção e restore; todas começam desligadas.
- Primeiro fechar writers e revisão, depois backfill/build, depois readers, depois seleção.
- Backfill nunca altera pointer; shadow não causa efeitos públicos.
- Bypass legado bloqueia cutover.
- Rollback preserva geração íntegra e não retorna a leitura mutável insegura.

## 4. Alternativas

| Estratégia | Benefício | Risco |
|---|---|---|
| Big-bang | Menor período de coexistência | Alto risco e reversão difícil |
| Shadow writes por cada endpoint | Comparação rápida | Efeitos duplicados, divergência e duas fontes de verdade |
| Revisão central + shadow builder + cutover por coorte | Gate incremental e mensurável | Fases longas; disciplina de writer e reader obrigatória |

## 5. Critérios de avaliação

Reversibilidade sem perda; cobertura observável; baixa exposição; operação em standalone; capacidade de provar zero bypass; compatibilidade incremental.

## 6. Recommended Decision

Recomenda-se centralizar comandos revisionados e migrar por fase/coorte. Não habilitar shadow write direto em paralelo. Builder sombra consome somente revisão imutável e escreve candidatos privados; comparator é somente leitura. Cutover de leitura vem depois do bloqueio dos writers antigos e cobertura de cache/frontend.

### Flags propostas, não criadas

editorial_revision_commands_enabled; editorial_generation_shadow_build_enabled; editorial_generation_compare_enabled; editorial_generation_admin_read_enabled; editorial_generation_student_read_enabled; editorial_generation_selection_enabled; editorial_generation_restore_enabled. Cada uma precisa owner, escopo, condição, métricas, parada e rollback próprios.

## 7. Justificativa

Segue dependências reais do B.2 rollout: revisão → writers → taxonomy/import/restore → backfill → sombra/comparação → readers → seleção → remoção legada. Não há ativação ou flag nesta fase documental.

## 8. Consequências positivas

Cada fase tem artefato e gate verificável; falha anterior à seleção não afeta alunos; decisões humanas podem ocorrer antes do cutover.

## 9. Consequências negativas

Coexistência pode durar; instrumentação precisa detectar todos os caminhos; custos operacionais temporários.

## 10. Riscos

Writer legado silencioso, shadow divergente, cache não pinado, flag mal ordenada, deploy sem compatibilidade de schema, backfill interpretado como ativação.

## 11. Impacto na migração

Roadmap detalhado em ../editorial-generations-phase-2-1a-12b3-roadmap.md. É obrigatório executar inventário vivo novamente antes de cada fase de código, pois baseline e tráfego podem mudar.

## 12. Compatibilidade

Endpoints atuais são preservados inicialmente por adapters internos. Só introduzir campo público version/generation quando contrato e frontend estiverem aprovados. Flags não podem permitir payload híbrido.

## 13. Estratégia de rollback

Antes da seleção: desligar builder/comparator, sem impacto público. Depois: parar novas publicações, conservar último head e atender com geração segura ou modo somente leitura; não reabrir caminho legado automaticamente.

## 14. Testes obrigatórios

Teste de cada flag isolada; combinação inválida falha fechado; zero side effect em shadow; zero pointer change em backfill; telemetria legacy writers; teste de cutover e parada; comparação sem conteúdo sensível.

## 15. Critérios de aceitação

Plano de fases aprovado; owners por flag; todos os gates e rollback rehearsed; cobertura de writers/readers atualizada; métricas sem conteúdo pessoal; aprovação separada por etapa.

## 16. Decisões dependentes

ADR-001, 002, 004, 005, 006, 008 e roadmap.

## 17. Perguntas para aprovação humana

Qual coorte piloto? Quais janelas de observação? Quem muda flags? Quais métricas bloqueiam progressão? Pode haver modo somente leitura e por quanto tempo? Como serão aprovados deploys compatíveis?

## 18. Approved Decision

Nenhuma. Todas as flags e sequência continuam propostas.

## 19. Evidência e confiança

O B.2 rollout (linhas 5-27, 42-56) já recomenda sequência e flags; esse documento formaliza a proposta, não aprova. Auditoria e código em e5bf…; confiança alta para inventário naquele snapshot, não para código futuro.

## 20. Gate de implementação

Toda fase futura precisa autorização independente. Nenhuma flag deve ser criada nesta fase e nenhuma ativação pode ocorrer por inferência da homologação da PoC.
