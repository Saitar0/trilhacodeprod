# Beta 8.2 — priorização de risco dos writers

| Prioridade | Caminhos | Motivo | Decisão Beta 8.2 |
|---|---|---|---|
| P1, mutação de rascunho limitada | W-07 `PUT /blocks/{id}`, W-07 `POST /blocks`, W-05 `PUT /nodes/{id}` | Alvo e trilha resolvíveis; permite testar grant, revisão, CAS, fence, auditoria e retry sem publicação ou cascata de dados de aluno. | PUT de bloco foi revalidado; POST de bloco e PUT de nó foram integrados. Sem capacidade explícita, rotas selecionadas falham fechadas. |
| P0, potencial de perda/indisponibilidade | W-02 exclusão de trilha, W-06 exclusão de subárvore, W-11 restore | Cascatas ou restauração podem remover/trocar conteúdo, publicações e referências usadas por aprendizagem. | Não executados nem convertidos para exclusão lógica. Exigem política humana de retenção/recuperação e contrato transacional. |
| P0, exposição pública | W-04 publicação; W-15 publicação imutável | Pode tornar conteúdo acessível e alterar a geração ativa. | Não executados. Dependem de autoridade operacional, política de geração, readers e ADR-008. |
| P1, substituição ampla | W-01, W-03, W-08, W-10, W-12 | Criação/duplicação/importação/relações/snapshot podem gerar estados parciais, ciclos, duplicações ou interpretar progresso contra conteúdo diferente. | Permanecem `REQUIRES_MIGRATION`; o bridge testou somente staging Beta 5 + transição experimental, não o import writer operacional. |
| P1, efeitos globais/administrativos | W-09, W-13, W-14 | Catálogos, seed e comandos de administração podem atravessar trilhas ou bancos e são heterogêneos. | `REQUIRES_OPERATIONAL_DECISION`; não executados. |
| P2, observabilidade/prova incompleta | W-16, W-17 | Auditoria legada e PoC de gerações não foram usados como writers de aplicação nesta prova. | `UNVERIFIED`; não classificados como contidos. |

A seleção evitou usar operações destrutivas ou publicar conteúdo como “prova”. O avanço de cobertura é mensurado em **operações**: três operações autenticadas passaram pela autoridade nesta linha de trabalho (incluindo reexecução do PUT W-07 da Beta 8.1). Isso não equivale a três famílias inteiras nem a contenção de todos os 17 caminhos.
