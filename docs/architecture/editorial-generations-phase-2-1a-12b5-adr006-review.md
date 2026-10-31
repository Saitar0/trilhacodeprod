# Fase 2.1A.12B.5 — revisão do ADR-006: publicação e restauração atômicas

**Status do ADR original:** Proposed.
**Decisão nesta ficha:** REQUIRES_CLARIFICATION.
**Dependência bloqueante:** ADR-001.
**Natureza:** decisão proposta; sem implementação.

## Problema e evidência

Na referência `e5bf3147a7f9a5ee02e1a011ffcbf1fb7e0cc636`, `publish_track` prepara snapshots/atividade e pode promover nodes/blocks antes do CAS final da trilha (`backend/services/tracks.py:152-227`). Restore substitui nodes, blocks e relations por delete/reinsert em lotes (`backend/services/versions.py:245-332`). Leitores fazem consultas separadas sobre dados vivos (`backend/services/nodes.py:85-149,234-256`). A ordem que abre a janela está confirmada no código; ocorrência observada em produção não foi demonstrada. Fontes: [auditoria B.2](./editorial-generations-phase-2-1a-12b2-audit.md#5-reevaluacao-do-risco-p1) e [ADR original](./adr-editorial-generations/ADR-006-atomic-publication.md).

A homologação 15/15 da PoC demonstra o mecanismo experimental em MongoDB 7.0.45 standalone; não prova integração com routes/services reais, identidade de banco, cache, schema ou proveniência da revisão de origem.

## Recommended Decision — recomendação técnica

1. A publicação candidata é preparada isoladamente a partir de uma revisão editorial completa e imutável aprovada pelo ADR-001.
2. O builder produz manifests/chunks e representações pública/privada versionadas; valida sequência, hashes, referências, schemas, limites e allowlist; só então sela. Selado é imutável.
3. Um único documento de controle por trilha é a autoridade do `active_generation_id`, revisão editorial corrente, base ativa esperada, fence e receipt resumido. A seleção é uma única escrita CAS que exige revisão, geração ativa e fence esperados, e registra a identidade da operação na mesma atualização atômica.
4. Nenhum campo público de versão/head duplicado em documento mutável (`tracks.version`, status, pointer de atividade) é autoridade concorrente. O leitor resolve o controle uma vez; a resposta usa somente aquele `generation_id`. Dados semânticos públicos, inclusive metadata de trilha necessária à resposta, devem vir da geração ou de referências imutáveis versionadas.
5. Toda leitura de chunks filtra pelo mesmo generation ID e verifica o manifesto. Missing/corrupt chunk/head não retorna resposta parcial e não faz fallback para coleções vivas. O erro público é explícito e sem segredo; a política de disponibilidade para usuário segue aprovada pelo produto/operações.
6. Retry da mesma operação consulta o receipt associado ao CAS e não faz uma segunda seleção. Limite/horizonte dos receipts precisa ser definido com ADR-004; receipt expirado não pode ser tratado como autorização para repetir a publicação.
7. Restore lê uma fonte histórica íntegra, cria nova revisão e nova geração, registra relação `restored_from`, e passa pelo mesmo validate → seal → CAS. A geração histórica não é editada nem apagada.
8. Cache key incorpora geração/sessão e audiência. Uma requisição/paginação fica fixada; consistência entre requisições frontend depende também do pin do servidor definido pelo ADR-002.

MongoDB standalone garante atomicidade de uma atualização de documento; não se assume transação multidocumento. Chunks e manifests são escritos primeiro, mas privados e imutáveis; a troca de um único controle é a linearização pública. Uma segunda fonte pública mutável para atividades/track metadata reintroduziria a necessidade de transação e invalida a alegação de publicação atômica.

## Unidade de publicação ainda precisa de decisão

**Recomendação inicial:** uma geração representa o agregado publicável da trilha inteira, incluindo a árvore/relações/metadados semânticos e referências exatas às definições de atividades. A aplicação e o frontend percorrem árvore e nós em chamadas distintas; o limite track evita que uma navegação combine versões de subárvores sem protocolo adicional.

**Custo:** publicação de uma alteração independente de quiz pode exigir nova geração da trilha, e o snapshot cresce. O caminho atual já versiona atividades por `published_version_id`; produto pode exigir publicação de atividade independente. Se essa independência for requisito, uma identidade de atividade separada terá de participar do token de leitura/sessão e do CAS da trilha de modo explícito. Não basta conservar um pointer de atividade mutável ao lado do head da trilha.

Essa escolha não pode ser inferida do código nem da PoC. Aprovação de produto/backend é necessária antes do contrato de manifesto e das APIs.

## Falhas, concorrência e rollback

| Ponto de falha/intercalação | Estado público exigido |
|---|---|
| Falha antes/depois de cada chunk ou antes do manifesto | Head antigo não muda; candidato privado incompleto não selecionável |
| Manifesto selado mas seleção não ocorreu | Head antigo permanece; candidato pode ser revalidado ou abandonado; nunca reescrito |
| Duas publicações com mesmo `expected_head`/revisão | Um CAS vence; a outra retorna conflito e não altera head |
| Writer perde fence enquanto builder roda | Candidate não sela nem seleciona após fence antigo; dados tardios não alteram geração corrente |
| CAS confirmado e resposta perdida | Receipt da operação retorna o resultado original; não repetir side effect |
| Leitor resolve A e head passa para B durante a leitura | Leitor termina somente A; nova requisição/sessão conforme ADR-002 resolve segundo política aprovada |
| Corrupção ou geração referenciada incompleta | Fail closed sem fallback live; alerta e parada de novas publicações |
| Código/flag novo falha após seleção | Parar novas publicações; manter reader de geração validada ou indisponibilidade explícita; nunca reativar live reader automaticamente |

Rollback editorial normal cria uma geração nova derivada de versão antiga, com receipt/auditoria. Um procedimento operacional de emergência pode re-selecionar uma geração anterior somente como operação autorizada, validada e registrada por CAS; não se edita manifest nem se altera histórico. Produto/segurança devem decidir se isso atende a retirada urgente. Retirada urgente pode exigir revogação de sessão e deve ser conciliada com ADR-002/004.

## Alternativas e trade-offs

| Alternativa | Prós | Contras |
|---|---|---|
| Atualização in-place | Reusa coleções e rotas atuais | Exposição parcial e restore vazio/parcial; não atende invariante |
| Snapshot legado sem head de geração | Histórico reutilizável | Snapshot não representa necessariamente revisão coerente; readers seguem vivos |
| Geração imutável + head CAS | Linearização em um documento, reader pin e fail closed | Exige revisão/fence, storage/roles, cache e migração integral da audiência |
| Coexistência sem corte por escopo | Migração incremental aparente | Payload pode misturar live e generation, ou writers divergir; não aceitável sem fonte canônica e zero bypass |

## Testes e critérios de aceitação

1. Failpoint em cada gravação/validação/seal/CAS: observadores veem somente geração antiga ou nova inteira.
2. CAS concorrente sob mesma base: um vencedor; replay após resposta perdida retorna receipt; operação com fingerprint diferente conflita.
3. Reader pausa após fixar A; selector publica B; leitura antiga devolve exclusivamente A e nova leitura autorizada observa B.
4. Corrupção/ausência/head inválido: nenhuma resposta parcial e nenhum acesso ao live store como fallback.
5. Manifest/refs privados inacessíveis ao public reader, conforme ADR-005.
6. Restore usa nova identidade, preserva histórico, tentativa/progresso e falha sem mudar head se fonte obsoleta/inválida.
7. Testes MongoDB standalone demonstram que o protocolo não usa transação multidocumento.
8. Testes frontend demonstram cache e múltiplas rotas sem mistura; sessões usam token validado pelo servidor.
9. Runbook de parada/rollback exercitado em ambiente descartável antes de seleção real.

## Ficha para aprovação

* **Decisão necessária:** aprovar geração da trilha como unidade inicial, um único controle CAS, restore como nova geração e proibição de fallback live? Como tratar atividade independentemente publicada e retirada urgente?
* **Recomendação:** seleção atômica após revisão coerente, manifest/chunks selados, reader pinado e sem fallback; unidade track para primeira versão.
* **Alternativas:** atualização in-place; snapshots sem ponteiro; geração por atividade; coexistência controlada após writer/reader gate.
* **Dependências:** ADR-001 obrigatório; ADR-005 para armazenamento/identidades; ADR-003 para schema; ADR-002 para sessão/tentativa; ADR-004 para receipts/GC; ADR-008 para implementação; ADR-007 para cutover.
* **Decisão humana:** REQUIRES_CLARIFICATION.
