# ADR-001 — Revisão e concorrência editorial

**Status:** Proposed
**Tipo:** decisão arquitetural proposta; não implementada e não aprovada.
**Baseline analisado:** snapshot e5bf3147a7f9a5ee02e1a011ffcbf1fb7e0cc636.
**Aprovação humana:** pendente; ver [matriz de decisões](../editorial-generations-phase-2-1a-12b3-decisions.md).

## 1. Contexto

Os serviços de trilhas, nós, blocos e relações escrevem em documentos separados. A auditoria não encontrou uma revisão monotônica comum mantida por todos esses caminhos. O snapshot de versões lê coleções separadamente e compara contagens, o que não detecta mudança de campo sem mudança de cardinalidade. Imports e restores têm leases próprios, mas não compartilham um fence com CRUD. Evidência: auditoria B.2, seções 2 e 5; e5bf…; backend/services/tracks.py:51-115, backend/services/nodes.py:61-180, backend/services/blocks.py:12-52, backend/services/relations.py:12-50, backend/services/versions.py:142-159; confiança alta para a ausência no escopo pesquisado.

## 2. Problema

Uma geração pode ser construída a partir de valores lidos em momentos diferentes; CAS apenas no head público não torna coerente a origem editorial. Um writer concorrente pode ser perdido, incorporado parcialmente ou continuar escrevendo após uma captura.

## 3. Requisitos

- Detectar alterações concorrentes inclusive em documentos diferentes e alterações que não mudam contagens.
- Todo caminho de escrita editorial, inclusive import, restore, taxonomy relevante, seed e manutenção, deve participar do mesmo controle ou ser bloqueado no escopo ativado.
- Escrita baseada em revisão obsoleta deve falhar com conflito explícito; não fazer rebase silencioso.
- A revisão identificada deve representar um estado completo e imutável.
- Operações retomáveis devem usar identidade e fingerprint estáveis.

## 4. Alternativas

| Opção | Benefício | Custo/limite |
|---|---|---|
| A. Revisão monotônica otimista por trilha | Conflitos explícitos; não requer manter lock durante cada edição | Todo writer precisa ler e condicionar a revisão; revisão coerente exige comando serializado ou snapshot imutável |
| B. Serializar comandos editoriais | Estado agregado fácil de ordenar | Contenção; exige fila/lock operacional e recuperação de comando interrompido |
| C. Lease e fencing por trilha | Impede writer atrasado após takeover se todas as escritas validam fence | Lease sozinho não define revisão completa; cada writer precisa participar; expiração/relógio precisam de contrato |
| D. Snapshot imutável privado por revisão | Fonte reproduzível e sem leitura de documentos vivos para construir geração | Custo de armazenamento e construção; precisa de revisão de origem coerente |
| E. Híbrida: revisão otimista + snapshot imutável + fence em operações longas | Combina conflito curto com proteção de builder/import/restore | Mais estados e observabilidade; migração de todos os escritores é gate |

## 5. Critérios de avaliação

Coerência verificável; compatibilidade com MongoDB standalone; cobertura de todos os writers; recuperação idempotente; contenção aceitável; sem transação multidocumento implícita; erro compatível com API.

## 6. Recommended Decision

Recomenda-se E: manter um controle monotônico de revisão por trilha, aplicar comandos por compare-and-swap da revisão-base e produzir snapshots privados imutáveis. Operações longas e retomáveis recebem lease com fencing token; a revisão, e não o lease, identifica o conteúdo. Mudança de conteúdo aceita incrementa a revisão uma única vez. Comando com revisão-base antiga retorna conflito controlado e deixa o estado corrente intacto. Não recompor automaticamente comandos sobre conteúdo novo.

### Máquina de estados proposta

| Estado | Significado | Transições permitidas |
|---|---|---|
| received | Comando validado superficialmente; sem escrita editorial | claimed, rejected |
| claimed | operation_id/fingerprint e revisão-base registrados; fence atual | building, conflict, abandoned |
| building | Produção de candidato privado | validated, failed, abandoned |
| validated | Snapshot completo e referencias verificadas | committed, conflict |
| committed | Revisão imutável tornou-se a revisão editorial corrente por CAS | terminal |
| conflict | Revisão/fence mudou; nenhuma publicação do candidato | nova operação explícita ou abandono |
| failed/abandoned | Falha ou cancelamento; nunca selecionável | recuperação limitada pelo mesmo fingerprint/fence ou retenção para diagnóstico |

Um processo que perde o fence não pode gravar, validar ou confirmar novas partes. A persistência do candidato e a atualização do controle devem ser ordenadas; no MongoDB standalone a garantia final deve depender de writes imutáveis e CAS de um único documento de controle, não de transação multidocumento.

## 7. Justificativa

A abordagem cobre escritores em documentos distintos e deixa o snapshot reproduzível. O protocolo experimental já demonstra conceitos de fencing/CAS em namespace isolado, mas não integra os escritores da aplicação. A auditoria B.2 registra que immutable_publications ainda marca a origem como unverified e activation_eligible false; e5bf…; backend/services/immutable_publications.py:487-510; confiança alta.

## 8. Consequências positivas

- Conflitos deixam de ser sobrescritas silenciosas.
- Builder pode apontar para uma revisão imutável e auditável.
- Candidatos obsoletos permanecem não selecionáveis.
- Edições concorrentes em campos ou documentos diferentes são detectáveis.

## 9. Consequências negativas

- Todos os escritores e caminhos administrativos precisam ser encontrados e migrados.
- Edições simultâneas podem produzir 409/conflict e exigir UX de resolução.
- Revisões e candidatos aumentam storage e exigem política de retenção.

## 10. Riscos

O maior risco é um writer legado contornar o controle e invalidar a alegação de coerência. Não existe prova de cobertura integral de scripts operacionais fora do snapshot auditado. Severidade crítica antes de qualquer cutover.

## 11. Impacto na migração

Primeiro inventariar e instrumentar writers; em seguida introduzir controle/revisão; migrar CRUD, import, restore, taxonomy semântica e maintenance; só então criar snapshots e habilitar seleção. O gate deve exigir zero bypass no escopo ativado.

## 12. Compatibilidade

Manter IDs de trilha/nó/bloco e payloads existentes. Revisão-base pode ser campo interno/aditivo inicialmente; conflito HTTP deve ser aprovado e documentado antes de alterar respostas públicas. Não há interface implementada para esse contrato.

## 13. Estratégia de rollback

Antes de seleção pública, parar novos comandos e descartar apenas candidatos não referenciados com propriedade comprovada. Após cutover, não reabrir writers legados; preservar a última revisão íntegra e bloquear escrita ou servir leitura segura até procedimento aprovado.

## 14. Testes obrigatórios

Dois comandos sobre mesma revisão em documentos diferentes; atualização sem mudança de contagem durante captura; reorder versus edit; import versus CRUD; restore versus edit; perda de resposta; replay; writer atrasado após takeover; falha em cada estado; verificação de que nenhum comando conflitante altera o head.

## 15. Critérios de aceitação

100% dos caminhos de escrita conhecidos têm owner e contrato; escritores desconhecidos bloqueiam o gate; uma revisão vencedora por CAS; comando obsoleto não some nem altera o estado; testes concorrentes passam repetidamente em MongoDB 7 standalone; sem assumir transação multidocumento.

## 16. Decisões dependentes

ADR-006 depende deste ADR. ADR-007, backfill, restore e retenção dependem da semântica de revisão. ADR-008 precisa liberar o baseline antes de implementação.

## 17. Perguntas para aprovação humana

1. Uma edição conflitante retorna 409 e exige reaplicação explícita pelo editor?
2. A revisão é incrementada por comando lógico aceito ou por cada alteração persistida?
3. Serialização é exigida para todos os comandos ou somente operações longas?
4. Quais escritores automatizados podem ser bloqueados durante a migração?
5. Qual é o contrato de recuperação de um comando em building?

## 18. Evidências e confiança

- **Confirmado no código:** CRUD direto e snapshot multi-consulta; e5bf…; backend/services/tracks.py:51-115, backend/services/nodes.py:61-180, backend/services/versions.py:142-159; alta.
- **Confirmado por teste:** imports têm ocultação/retomada; audit B.2 seção 2; alta para os casos testados, não prova de integração com revision fence.
- **Homologado na PoC:** CAS, fencing, replay e reader pin no ambiente experimental; package commit 8a087fd5… e run 40686021030; não prova integração da aplicação.
- **Proposto:** revisão monotônica e snapshot privado; não implementado.

## 19. Approved Decision

Nenhuma. A decisão permanece proposta até aprovação humana específica.

## 20. Dependências e limites

Baseline do ADR-008, decisão de tratamento de conflitos, inventário atualizado de writers e política de retenção do ADR-004 são gates prévios.
