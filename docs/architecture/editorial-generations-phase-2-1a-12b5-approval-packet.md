# Fase 2.1A.12B.5 — pacote de aprovação humana dos ADRs

Este documento resume as decisões para discussão. **Todos os ADRs originais permanecem `Proposed`; nenhuma opção abaixo está aprovada.** Os estados `PENDING_APPROVAL`, `REQUIRES_CLARIFICATION` e `BLOCKED_BY_EVIDENCE` são triagem desta fase, não substituem o status original. Fontes e análise detalhada: [revisão ADR-001](./editorial-generations-phase-2-1a-12b5-adr001-review.md), [ADR-005](./editorial-generations-phase-2-1a-12b5-adr005-review.md), [ADR-006](./editorial-generations-phase-2-1a-12b5-adr006-review.md), [demais ADRs](./editorial-generations-phase-2-1a-12b5-remaining-adrs.md) e [matriz de dependências](./editorial-generations-phase-2-1a-12b5-dependency-matrix.md).

## Ordem recomendada para revisão

1. ADR-001 fixa consistência e unidade de concorrência.
2. ADR-005 define fronteiras de dados e identidades; ADR-003 classifica dependências semânticas. Podem ser discutidos em paralelo, mas ambos alimentam o builder/leitor.
3. ADR-006 escolhe unidade e linearização de publicação, após 001/003/005.
4. ADR-002 define sessão/avaliação; ADR-004 fecha retenção depois do inventário de referências de sessão, tentativa, receipt e histórico. Até isso ocorrer, manter GC desativado.
5. ADR-007 formaliza rollout somente depois das decisões anteriores.
6. ADR-008 é gate operacional independente: sua triagem permanece bloqueada por evidências; não autoriza branch ou implementação.

## Fichas resumidas

### ADR-001 — revisões editoriais e concorrência

**Problema:** writers alteram partes do agregado editorial sem revisão monotônica comum; snapshot por leituras separadas/cardinalidades não garante consistência; CAS do head isoladamente não fecha a origem.
**Proposta:** revisão monotônica por trilha controlada pelo servidor; candidata construída de snapshot privado coerente; CAS sobre revisão esperada; fencing para operações longas; conflito explícito; operação lógica identificada e retry idempotente; sem rebase silencioso.
**Alternativas:** serialização de todos os comandos; lease global; snapshots sem revisão comum; merge/rebase automático.
**Consequências:** conflitos visíveis e mudanças testáveis; exige adaptar todos os writers e potencialmente manter rascunho no cliente; não há transação multidocumento presumida.
**Riscos:** writers legados contornarem controle; dual-write divergente; taxonomia global mutável fora do contador; recuperação de receipt expirado.
**Evidências:** auditoria B.2 em `e5bf3147a7f9a5ee02e1a011ffcbf1fb7e0cc636`, contratos/invariantes B.3 e testes da PoC em ambiente isolado.
**Pendências:** agregado/unidade final, campos no-op, política de conflito/API, integração de import/restore/CRUD, modelo contra dados legados durante transição.
**Aceitação:** inventário de writers fechado; testes para campo alterado sem contagem, corrida em docs distintos, fence expirado, interrupção e replay; nenhum writer seleciona estado fora do controle.
**Dependências:** ADR-003, ADR-008; precede ADR-006.
**Bloqueia implementação?:** sim, para qualquer escopo com múltiplos writers.
**Decisão humana:** aprovar princípio, depois resolver questões listadas antes do contrato executável.
**Status:** `REQUIRES_CLARIFICATION`.

### ADR-005 — separação público/privado

**Problema:** auditoria observou schema genérico permissivo e serializer que remove campos conhecidos sem ser allowlist geral; roles reais e identidades efetivas não foram auditadas.
**Proposta:** defesa em profundidade: partição de dados privados, principal MongoDB público mínimo, evaluator privilegiado isolado, DTO/serializer de allowlist por tipo e versão, rejeição de campo/tipo desconhecido, auditoria de todos os leitores e cache segregado.
**Alternativas:** filtrar no controller; apenas negar campos conhecidos; separar armazenamento sem mudar DTO; usar somente principals.
**Consequências:** superfície pública mais clara e testes negativos; mais schemas/identidades e trabalho de compatibilidade.
**Riscos:** endpoint/preview/cache/log legado contornar a projeção; grants não corresponderem ao desenho; definição privada copiada para cache.
**Evidências:** auditoria B.2; a PoC demonstrou reader restrito em testes isolados, não roles do backend real.
**Pendências:** classificação de campos por domínio, principal por processo, endpoint alternativo e compatibilidade do payload.
**Aceitação:** testes de acesso negado por papel, payload sem campos privados em todos readers, unknown fields fail closed, cache sem mistura.
**Dependências:** ADR-003 para classificar metadados; ADR-002 para evaluator; precede ADR-006.
**Bloqueia implementação?:** sim, para reader público, definição de quiz e cache.
**Decisão humana:** aprovar o princípio de menor privilégio e negação por padrão; roles e desenho exato requerem threat model.
**Status:** `PENDING_APPROVAL`.

### ADR-006 — publicação e restauração atômicas

**Problema:** a auditoria identificou alterações públicas intermediárias em publicação/restauração; leitores consultam documentos vivos em etapas separadas.
**Proposta:** construir geração privada de revisão coerente, validar e selar imutavelmente, depois trocar um único controle/head por CAS; leitor fixa uma geração e falha fechado sem live fallback; restore cria geração nova.
**Alternativas:** update in-place; snapshot sem ponteiro; transação multidocumento; geração global ou publicação independente de atividade.
**Consequências:** seleção com ponto de linearização único e leitura reproduzível; conteúdo duplicado/retido e exigência de todos readers seguirem generation ID.
**Riscos:** revisão de origem inconsistente; ponteiro duplicado (`tracks.version` vs novo control); receipt/head parcialmente observável; atividade independente criar segundo head; fallback inseguro.
**Evidências:** auditoria B.2 e homologação da PoC (15/15 testes integrados); a homologação não prova integração real.
**Pendências:** unidade publicável (recomendação: trilha agregada), autoridade única do head, receipt durável, política de retirada urgente e disponibilidade quando geração corrompe.
**Aceitação:** falhas em cada estágio, CAS concorrente, lost response, leitura A/B, corrupções, restore e confirmação de zero readers live no escopo.
**Dependências:** ADR-001 obrigatório; ADR-003 e 005; ADR-002/004 para sessão e retenção.
**Bloqueia implementação?:** sim, publicação/restauração e readers públicos.
**Decisão humana:** produto decide unidade e urgência; arquitetura aprova ponto único de seleção após fechar autoridade/receipt.
**Status:** `REQUIRES_CLARIFICATION`.

### ADR-002 — sessão e progresso vinculados à geração

**Problema:** `published_version_id` pode existir em tentativas de quiz, mas outras leituras/progresso não compartilham identidade imutável confirmada.
**Proposta:** servidor fixa geração à sessão; tentativa fixa atividade e definição privada; submissão é avaliada contra essa definição mesmo após nova publicação.
**Alternativas:** head mais recente; pin por requisição; pin só por tentativa.
**Consequências:** coerência pedagógica/histórica; requer estado de sessão, retenção e UX para conteúdo antigo.
**Riscos:** sessão sem política de expiração, retirada urgente, links antigos e progresso órfão.
**Evidências:** inventário B.2; contratos conceituais B.3.
**Pendências:** duração/renovação, submissão tardia, nota histórica, acesso após retirada.
**Aceitação:** A→B em sessão, resposta tardia, retomada, revogação e acesso cruzado de usuário.
**Dependências:** ADR-005/006/003; ADR-004 para retenção.
**Bloqueia implementação?:** sim para qualquer leitor/quiz/progresso migrado.
**Decisão humana:** produto educacional e privacidade.
**Status:** `REQUIRES_CLARIFICATION`.

### ADR-003 — taxonomias e metadados versionados

**Problema:** referência semântica global mutável pode alterar apresentação/interpretação sem nova geração.
**Proposta:** congelar semântica/ordenação pública; IDs estáveis separados de rótulos; schema versionado e referência de taxonomia imutável quando necessário.
**Alternativas:** copiar todo catálogo; referências dinâmicas; versão global; dividir estável/dinâmico.
**Consequências:** histórico reproduzível; custo de catalogar e manter renderer antigo.
**Riscos:** classificação errada, duplicação e incompatibilidade de frontend.
**Evidências:** coleções/áreas tags, taxonomies e block_types no snapshot B.2; semântica de certos campos não comprovada.
**Pendências:** classificação campo a campo, existência/uso de dificuldade/competências/objetivos, impacto de renomeações.
**Aceitação:** matriz de dados aprovada e teste de mudança de dependência durante build/leitura.
**Dependências:** inventário de domínio; ADR-001/005/006.
**Bloqueia implementação?:** sim para campos não classificados que afetam resposta pública.
**Decisão humana:** produto/currículo e frontend.
**Status:** `REQUIRES_CLARIFICATION`.

### ADR-004 — retenção e exclusão

**Problema:** gerações são necessárias para sessões, avaliação, restore e auditoria, mas retenção indefinida custa e pode conflitar com privacidade.
**Proposta:** retenção por referências/obrigações; sem GC até haver grafo completo e política aprovada; separar PII do conteúdo pedagógico quando possível.
**Alternativas:** ilimitada, prazo fixo, referência, política por curso, híbrida.
**Consequências:** preserva referências; exige indexar ownership e tratar remoção/anonimização.
**Riscos:** remover dado ainda referenciado ou reter indevidamente; receipt expirado antes de reconciliação.
**Evidências:** B.2 não fecha o grafo de referência; ADR-002 ainda não fixa sessões.
**Pendências:** bases legal/produto, dados apagáveis, responsáveis e horizonte de sessão/receipt.
**Aceitação:** grafo e owners, política revisada, teste de corrida referência×GC e recuperação.
**Dependências:** ADR-002/005/006.
**Bloqueia implementação?:** bloqueia GC e exclusão física; não impede protótipo de escrita privado se nada for coletado.
**Decisão humana:** produto, privacidade/jurídico e operação.
**Status:** `BLOCKED_BY_EVIDENCE`.

### ADR-007 — migração gradual

**Problema:** rollout amplo pode criar divergência ou deixar writers/readers legados contornarem geração.
**Proposta:** instrumentação passiva → revisão/fence e writers completos → isolamento privado → backfill sem head → shadow comparison → readers/coorte → CAS/publicação → restore → desativação do legado. Flags independentes off.
**Alternativas:** big bang; shadow/dual write; leitor primeiro; migrate por coleção.
**Consequências:** gates e rollback por escopo; maior duração e observabilidade necessária.
**Riscos:** dual write não atômico, flag parcial, fallback live.
**Evidências:** inventário B.2, roadmap B.3 e gates B.4; não comprovam runtime atual.
**Pendências:** owner, limites das coortes, métricas e procedimento de autorização.
**Aceitação:** cada etapa reversível, head invariável no backfill, zero bypass antes do cutover, alerta e runbook.
**Dependências:** ADR-001–006 e ADR-008 para runtime.
**Bloqueia implementação?:** a sequência pode ser aprovada; execução de cada etapa requer autorização independente.
**Decisão humana:** engenharia, produto, segurança e operação.
**Status:** `PENDING_APPROVAL`.

### ADR-008 — baseline e compatibilidade

**Problema:** referências Git, build histórico e deployment não identificam a revisão efetivamente atendendo usuários.
**Proposta:** manter baseline implantado não comprovado; selecionar linha de desenvolvimento apenas após compatibilidade documentada e aprovação humana; não inferir produção por nome de recurso/branch.
**Alternativas:** main, staging, snapshot auditado ou branch de integração reconciliada.
**Consequências:** evita mudança sobre baseline errado; posterga runtime até evidência operacional apropriada.
**Riscos:** evidências históricas podem estar desatualizadas; branch escolhida não refletir deployment.
**Evidências:** B.4B parcial; staging histórico com commit, mas sem digest/container/rota/tráfego; G2 é build, não runtime. Não repetir consulta de infraestrutura nesta fase.
**Pendências:** identificação de produção, digest ativo/proveniência, confirmação autorizada do ambiente e escolha de linha/release.
**Aceitação:** matriz compatível + cadeia runtime/build/Git suficiente ou risco formalmente aceito pela autoridade competente; plano de testes compatíveis; decisão registrada.
**Dependências:** gate paralelo para ADR-007 e qualquer runtime.
**Bloqueia implementação?:** sim para integração na aplicação e cutover; não para revisão conceitual documental.
**Decisão humana:** owner de engenharia/produto e infraestrutura.
**Status:** `BLOCKED_BY_EVIDENCE`.

## Decisões bloqueadas vs prontas para princípio

**Prontas para avaliação de princípio, sem ativação:** defesa em profundidade/negação por padrão (005), sequência gradual com flags off (007).
**Requerem esclarecimento antes de aprovação completa:** unidade/conflict model (001), unidade publicável e autoridade do head (006), sessão/retirada/progresso (002), classificação semântica (003).
**Bloqueadas por evidência/política ausente:** retenção/GC (004), baseline e compatibilidade operacional (008).

## Perguntas humanas que não são respondidas pelo código

1. Por quanto tempo uma sessão mantém a geração e como renová-la?
2. Um aluno pode concluir quiz antigo após republicação? Como preservar nota e avaliação?
3. O que deve ocorrer numa retirada urgente, com sessão ou tentativa aberta?
4. Quais partes do progresso e histórico permanecem, e quais podem ser anonimizadas/removidas?
5. Quais taxonomias são semânticas e quais rótulos podem mudar dinamicamente?
6. Quem aprova prazos de retenção e exclusão definitiva?
7. Qual ambiente/linha será primeira validação e qual baseline foi implantado?
8. Quem aprova cutover, quais evidências exige e quem pode autorizar rollback?
9. A unidade inicial de publicação é trilha inteira ou atividade independente?
10. Como a API preserva o rascunho do editor em conflito sem merge automático?

## Registro final

O pacote organiza recomendações e critérios verificáveis, não decisões aprovadas. Para a próxima reunião, recomenda-se decidir primeiro princípio/unidade do ADR-001, fronteira de segurança do ADR-005 e unidade/autoridade do ADR-006; manter ADR-008 bloqueado e não iniciar código até seus gates e demais questões de produto/privacidade estarem tratados. Os estados completos e dependências estão na [matriz transversal](./editorial-generations-phase-2-1a-12b5-dependency-matrix.md).
