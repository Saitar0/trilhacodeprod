# ADR-006 — Publicação e restauração atômicas por geração

**Status:** Proposed
**Tipo:** decisão de consistência proposta; não implementada nem aprovada.
**Baseline analisado:** e5bf3147a7f9a5ee02e1a011ffcbf1fb7e0cc636.
**Dependência bloqueante:** ADR-001 — revisão e consistência da origem.

## 1. Contexto

publish_track prepara snapshots e publicações, promove filhos draft para published e só depois atualiza o documento track por CAS; services/tracks.py:152-227. Restore exclui/reinsere nós, blocos e relações em lotes antes de concluir; services/versions.py:245-332. Os leitores consultam documentos vivos em separado; backend/services/nodes.py:85-149,234-256. A janela de publicação parcial e restore parcial está confirmada na sequência do código; uma requisição concorrente que observe a janela é cenário possível/inferido. Fonte: audit B.2 seção 5; confiança alta para ordem, média para ocorrência em produção.

## 2. Problema

Atualização in-place pode tornar conteúdo intermediário visível, misturar coleções de momentos diferentes ou sobrescrever edição concorrente. CAS no head não protege writes que ocorreram antes do CAS.

## 3. Requisitos

Geração candidata privada; validação integral; selagem imutável; origem vinculada a revisão coerente; seleção por um único CAS; leitores fixam uma identidade; restore cria nova geração; retry/replay não duplica efeito; nenhuma dependência implícita de transação multidocumento.

## 4. Alternativas

| Opção | Propriedade | Risco/custo |
|---|---|---|
| Atualização in-place | Pouca mudança de storage | Exposição parcial e restore destrutivo |
| Snapshot histórico + documentos vivos | Histórico recuperável | Leitor ainda pode usar conteúdo mutável; versão não é autoridade pública completa |
| Geração imutável + ponteiro CAS | Leitura consistente; head troca em um documento | Depende de revisão/fence completo e projeções fechadas |
| Coexistência gradual | Permite migração por coorte | Alto risco de bypass e fallback misto sem gates rígidos |

## 5. Critérios de avaliação

Atomicidade de seleção em standalone; origem coerente; leitura pinada; compatibilidade API; recuperação após resposta perdida; custo e retenção; possibilidade de stop seguro.

## 6. Recommended Decision

Recomenda-se construir e validar uma geração imutável antes de selecionar um head por CAS de documento único, condicionando expected active generation, revisão editorial e fence. O leitor resolve head uma vez e lê apenas geração correspondente; corrupção falha fechada. Restore cria candidata nova a partir de snapshot histórico validado, não reescreve a geração original.

### Invariantes mínimos propostos

1. Geração incompleta ou sem manifest/hash validado nunca é selecionável.
2. Chunk/manifest selado nunca é alterado; correção cria nova identidade.
3. Head ativo só referencia geração selada, íntegra e proveniente de revisão aceita.
4. Seleção é CAS sobre o controle esperado; uma disputa tem um vencedor.
5. Retry por mesma operation_id e fingerprint retorna o recibo original.
6. Writer com fence obsoleto não sela nem seleciona.
7. Leitor fixa generation_id antes de ler chunks e não mistura A/B.
8. Leitura pública nunca faz fallback para documentos vivos após erro de integridade.
9. Restore conserva histórico e segue a mesma sequência prepare → validate → seal → select.
10. Nenhuma garantia depende de transação multidocumento não comprovada.

## 7. Justificativa

O mecanismo reduz mudança pública à atualização atômica de um único controle, mas somente depois de ADR-001 assegurar que a origem é coerente e todos os writers obedecem ao fence. Homologação da PoC (commit 8a087fd5…, run 40686021030) cobre o protocolo isolado em MongoDB 7.0.45 standalone; não cobre os services reais.

## 8. Consequências positivas

Leitores podem continuar numa geração completa durante troca; restore deixa de esvaziar coleção ativa; resposta perdida pode ser recuperada por recibo.

## 9. Consequências negativas

Storage e builder aumentam; todos readers, caches e writers precisam migrar; incidentes podem exigir indisponibilidade em vez de fallback.

## 10. Riscos

Origem incoerente, writer legado, GC prematuro, cache sem generation key, segredo em projeção, CAS de head sem CAS de revisão editorial.

## 11. Impacto na migração

Somente após revisão/fence e separação público/privado. Backfill não seleciona head. Shadow build é read-only quanto à resposta pública. Cutover bloqueia legado para escopo ativado.

## 12. Compatibilidade

Manter IDs e endpoints; adicionar token de geração interno/aditivo. Resposta antiga não pode ser montada com alguns campos do legado e outros da geração.

## 13. Estratégia de rollback

Antes do CAS, manter head antigo e abandonar candidato. Depois do CAS, não fazer fallback live; parar novas publicações, servir última geração íntegra ou indisponibilidade segura. Reverter conteúdo é nova seleção validada com receipt, não alteração manual do ponteiro.

## 14. Testes obrigatórios

Failpoint após cada gravação; candidato incompleto não selecionável; disputa CAS; resposta perdida; writer atrasado; reader durante swap; corrupção de chunk/manifest/head; restore com conflito; teste standalone sem transações; projeção privada.

## 15. Critérios de aceitação

Todos invariantes passam em integração MongoDB real descartável; leitores públicos 100% cobertos; zero writer bypass; manifesto e referências verificados; rollback drill comprovado; observabilidade e runbook revisados.

## 16. Decisões dependentes

ADR-001 obrigatório; ADR-002 e ADR-004 definem refs e retenção; ADR-005 define armazenamento e identidade; ADR-007 define cutover; ADR-008 baseline.

## 17. Perguntas para aprovação humana

Qual unidade é publicada (track inteira ou subárvore)? Restore para versão anterior gera nova geração? Qual comportamento público em corrupção? Há SLA para indisponibilidade? Como fazer retirada urgente?

## 18. Approved Decision

Nenhuma. A recomendação de publicação atômica não está autorizada para produção.

## 19. Evidência e confiança

Confirmado: ordem de publish e restore em backend/services/tracks.py:152-227 e backend/services/versions.py:245-332; reader multi-consulta em backend/services/nodes.py:85-149,234-256. e5bf…; alta. Possibilidade de observação intermediária decorre da ordem e ausência de transação; ocorrência concreta não foi medida.

## 20. Critério de bloqueio

Sem ADR-001 aprovado, sem baseline escolhido e sem prova de cobertura total de writers/readers, não habilitar seleção pública por geração.
