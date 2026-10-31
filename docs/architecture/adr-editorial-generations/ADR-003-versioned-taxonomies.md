# ADR-003 — Taxonomias e metadados versionados

**Status:** Proposed
**Tipo:** recomendação de escopo de snapshot; não implementada nem aprovada.
**Baseline analisado:** e5bf3147a7f9a5ee02e1a011ffcbf1fb7e0cc636.

## 1. Contexto

Trilhas, relações, tags, taxonomias e tipos de bloco são lidos em caminhos distintos. Atualização de block_type pode alterar capabilities/renderização; remoção de tag executa $pull em referências globais. GET /api/meta lê taxonomias atuais sem pin. Evidência: audit B.2 seções 2-3; backend/services/taxonomy.py:12-28,31-91; backend/routes_taxonomy.py:47-81; confidence alta.

## 2. Problema

Uma geração imutável pode mudar de significado se depender de metadados externos mutáveis que afetam ordem, apresentação, autorização, schema, avaliação ou navegação.

## 3. Requisitos

- Congelar na geração todos os metadados que alterem significado pedagógico, ordem, renderização ou avaliação.
- Separar metadados administrativos/dinâmicos que não afetem semântica pública.
- Identificar versão de schema/render/evaluator necessário para abrir dados antigos.
- Evitar duplicação global desnecessária sem reintroduzir mutabilidade referenciada.

## 4. Alternativas

| Alternativa | Vantagem | Trade-off |
|---|---|---|
| A. Copiar toda taxonomia em cada geração | Sem dependência externa; snapshot autônomo | Duplicação e atualizações administrativas não refletidas |
| B. Referenciar registros globais mutáveis | Menor storage e dados normalizados | Semântica publicada pode mudar sem nova geração |
| C. Versionar taxonomias globalmente | Compartilhamento com estabilidade por versão | Gestão de versões e dependências cruzadas |
| D. Dividir semântica congelada e metadado dinâmico | Equilíbrio entre estabilidade e manutenção | Exige classificação de cada campo e governança |

## 5. Critérios de avaliação

Imutabilidade semântica, tamanho, compatibilidade com renderer, pesquisa/navegação, evolução de schema, operações globais e capacidade de reconstruir a experiência antiga.

## 6. Recommended Decision

Recomenda-se D. Incluir na geração uma representação fechada de metadados que afetam pedagogia, ordem, exibição, validação de resposta e navegação. Referências dinâmicas são aceitáveis apenas para dados puramente administrativos sem efeito na resposta ao aluno; isso precisa de classificação por campo e contrato. Uma identidade de schema deve selecionar renderer/evaluator compatível.

## 7. Matriz campo/coleção proposta

| Campo/coleção observada | Classificação proposta | Política candidata | Confiança / pendência |
|---|---|---|---|
| tracks: título, descrição, status público, ordem e slug | Público/semântico | Congelar no snapshot | Audit B.2; produto confirma campos expostos |
| nodes: título, tipo, ordem, hierarquia, status | Público/semântico | Congelar | Confirmado em nodes.get_track_tree/get_node; e5bf… |
| content_blocks: conteúdo, alternativas, mídia, critérios | Público; parte privada | Separar DTO e definição de avaliação; congelar ambos | Schema amplo; classificar cada tipo de bloco |
| relations/pré-requisitos | Semântico e navegacional | Congelar o conjunto e validar ciclos | backend/services/relations.py:12-50; alta |
| tags | Depende do uso | Congelar IDs e rótulos se afetarem navegação/filtro; campos administrativos dinâmicos somente se aprovados | Uso por campo ainda precisa de validação de produto |
| taxonomies | Misto | Versionar label/ordem/semântica pública; referência administrativa mutável apenas quando irrelevante à leitura | taxonomy.get_metadata:12-28 |
| block_types | Schema/capability/renderer/evaluator | Fixar schema_version e capabilities por geração | Uma mudança pode mudar interpretação; alta |
| activity definition/gabarito/rubrica | Privado e semântico | Referenciar definição privada imutável pela tentativa/geração | activity_publications e activities; atual quiz já tem versioning limitado |
| progresso, notas, submissões, tentativas | Dados do aluno, fora do conteúdo | Não copiar para chunks editoriais; preservar referências à geração | Audit B.2:52 e 66-69 |

## 8. Justificativa

A leitura de metadata é global e não versionada, enquanto conteúdo público agrega registros separados. Fixar apenas chunks de conteúdo sem versões de schema/capabilities deixa renderer e avaliação dependentes de estado corrente.

## 9. Consequências positivas

Experiência antiga pode ser reconstruída; mudança de semântica exige nova publicação; evaluator mantém definição correta.

## 10. Consequências negativas

Snapshots crescem; renderer/evaluator antigos precisam de suporte; classificação campo a campo demanda owner de produto e frontend.

## 11. Riscos

Uma classificação errada de “administrativo” pode mutar experiência publicada. Duplicação pode exceder limites BSON, reforçando chunks limitados e limites medidos.

## 12. Impacto na migração

Mapear campos e consumidores antes do backfill; versionar block_type/schema; comparar DTOs legados com projeção da geração. Alterações globais não são migradas sem regra de propagação.

## 13. Compatibilidade

Manter IDs estáveis de track/node/block. DTO público permanece compatível por adaptação explícita; mudanças em tipo/schema devem ser aditivas ou versionadas. Não assumir que metadados atuais podem ser removidos.

## 14. Estratégia de rollback

Desabilitar publicação de candidatos cujo schema não seja suportado. Não recarregar metadado mutável para “completar” geração antiga. Renderização ausente deve falhar fechada ou apresentar indisponibilidade segura.

## 15. Testes obrigatórios

Alterar taxonomia/tag/block_type após geração A e provar que leitura A não muda; nova geração B vê a alteração aprovada; renderer desconhecido falha fechado; conjunto de relações tem integridade; payload não inclui campos privados.

## 16. Critérios de aceitação

Matriz de campo assinada por backend, produto e frontend; toda dependência semântica é imutável/versionada; todas versões de bloco têm renderer e evaluator conhecidos ou falham fechadas.

## 17. Decisões dependentes

ADR-001 (revisão), ADR-005 (projeção privada), ADR-006 (conteúdo selado), ADR-004 (retention de schemas antigos).

## 18. Perguntas para aprovação humana

Quais tags entram no catálogo? Renomear tag altera geração? Quais metadados de bloco são schema versus configuração? Quais renderers/evaluators antigos serão suportados? Qual política para tipo removido?

## 19. Approved Decision

Nenhuma. A classificação é proposta e requer revisão de campo por campo.

## 20. Evidência e confiança

Confirmado no código: taxonomy.get_metadata e CRUD em backend/services/taxonomy.py:12-91; tags/block_types em backend/indexes.py:7-91; leitor de nó em backend/services/nodes.py:85-149. e5bf…; alta para mecanismo, média para impacto pedagógico por campo. Impacto semântico é inferido até análise de cada consumidor.
