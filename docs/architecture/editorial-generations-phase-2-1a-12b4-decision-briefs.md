# Fase 2.1A.12B.4 — fichas resumidas para aprovação

As fichas resumem os ADRs completos em [adr-editorial-generations](adr-editorial-generations/). Os oito ADRs originais permanecem Proposed. Cada status desta página é PENDING_APPROVAL.

## ADR-001 — Revisão e concorrência editorial

**Decisão necessária:** como todos os comandos editoriais formam uma revisão coerente e resolvem edição concorrente?
**Recomendação:** revisão monotônica por trilha; escritores validam a revisão-base; snapshot privado associa-se a uma revisão coerente; seleção usa CAS; operação longa pode usar lease/fencing; revisão obsoleta retorna conflito compreensível preservando o trabalho do editor.
**Justificativa:** os CRUDs de trilha, nó, bloco e relação não compartilham revisão; contagens iguais não demonstram que o conteúdo não mudou.
**Outras opções:** serializar todos os comandos; lease/fence comum; snapshot imutável versionado; estratégia híbrida. Merge/rebase automático silencioso não é comportamento recomendado.
**Consequências:** mais conflitos explícitos e trabalho de integração; reduz lost updates e snapshot misto se todo writer participar.
**Dependências:** ADR-008 e inventário de todos os writers.
**Bloqueia implementação?:** sim, publicação e snapshot dependem da origem coerente.
**Status:** PENDING_APPROVAL.

## ADR-002 — Geração de sessão e progresso

**Decisão necessária:** quando o servidor fixa a geração e como continuam sessão, atividade e progresso depois de republicação, restore ou retirada?
**Recomendação:** sessão vinculada a geração validada pelo servidor; tentativa fixa a definição privada original e avaliação não consulta o head atual.
**Justificativa:** tentativa de quiz pode guardar published_version_id, enquanto progresso genérico e submission não têm identidade global de geração; frontend faz chamadas/cache separados.
**Outras opções:** sempre latest; pin por requisição; pin apenas por tentativa; híbrida sessão + tentativa.
**Consequências:** requer retenção de conteúdo e avaliação históricos; pode manter aluno em conteúdo antigo ou exigir reabertura após revogação, conforme decisão de produto.
**Dependências:** ADR-003, ADR-004, ADR-005 e ADR-008.
**Bloqueia implementação?:** sim para leitor de sessão, atividade e progresso afetados; duração e exceções são decisões de produto.
**Status:** PENDING_APPROVAL.

## ADR-003 — Taxonomias e metadados

**Decisão necessária:** quais metadados devem ficar estáveis junto da geração e quais podem mudar dinamicamente?
**Recomendação:** congelar ou referenciar versão para qualquer campo que altere sentido pedagógico, ordenação, navegação, renderização, capacidade de envio ou validação; manter fora apenas metadados administrativos sem efeito público. Classificação individual exige validação de produto/frontend.
**Justificativa:** taxonomias, tags e block_types são consultados globalmente e não são fixados por revisão; mudança pode alterar uma geração sem nova publicação.
**Outras opções:** incorporar todas as taxonomias; referências mutáveis; catálogo global versionado; modelo híbrido.
**Consequências:** estabilidade pode duplicar metadados; catálogo global pode exigir retenção/compatibilidade por versão.
**Dependências:** ADR-001, ADR-005 e ADR-008.
**Bloqueia implementação?:** sim para campos cujo efeito pedagógico/público não esteja classificado.
**Status:** PENDING_APPROVAL.

## ADR-004 — Retenção e exclusão

**Decisão necessária:** quais referências preservam uma geração e quem aprova exclusão definitiva?
**Recomendação:** retenção por referências ativas e obrigações de progresso, tentativas, avaliação, histórico e restauração; nenhuma duração ou período de graça é assumido; bloquear GC até inventário e política aprovados.
**Justificativa:** exclusão atual pode apagar dados relacionados; versões podem ser necessárias a avaliações e notas históricas.
**Outras opções:** ilimitada; janela fixa; por curso; híbrida e baseada em referências.
**Consequências:** armazenamento e complexidade aumentam; remoção de dados pode exigir anonimização/separação de conteúdo.
**Dependências:** ADR-002 e revisão jurídica/privacidade.
**Bloqueia implementação?:** bloqueia exclusão/GC e qualquer backfill com descarte; leitura versionada necessita retenção mínima aprovada.
**Status:** PENDING_APPROVAL.

## ADR-005 — Separação de dados públicos e privados

**Decisão necessária:** onde ficam gabaritos e quem pode consultá-los?
**Recomendação:** defesa em profundidade: partição/coleção privada quando adequada, identidade Mongo restrita do reader público, identidade privilegiada do avaliador, DTO público allowlist e negação por padrão a campo desconhecido.
**Justificativa:** schema genérico aceita extras; serializer genérico não é allowlist; grants reais não foram consultadas. A PoC demonstra contrato experimental, não roles em produção.
**Outras opções:** filtrar só no controller; DTO somente; storage/identidade segregados; combinação recomendada.
**Consequências:** mais identidades, wiring e testes de autorização; reduz impacto de bug isolado.
**Dependências:** ADR-008 e classificação de modelos/campos.
**Bloqueia implementação?:** sim para qualquer novo leitor público ou acesso de avaliador a conteúdo versionado.
**Status:** PENDING_APPROVAL.

## ADR-006 — Publicação e restauração atômicas

**Decisão necessária:** como uma nova revisão se torna pública e como restore preserva o estado válido?
**Recomendação:** montar candidato imutável privado, validar integridade/revisão, selar e alterar um único head por CAS; leitura fixa um único head; restore produz nova geração; falha fecha sem fallback a documentos mutáveis.
**Justificativa:** o código auditado promove filhos antes do CAS final e restore apaga/reinsere coleções vivas em lotes. A janela no fluxo está confirmada; ocorrência de uma requisição no intervalo é hipótese testável.
**Outras opções:** atualização in-place; snapshots legados; ponteiro de geração; coexistência progressiva.
**Consequências:** exige origem coerente, retenção e novo contrato de reader; fallback inseguro não pode ser usado para rollback.
**Dependências:** ADR-001 obrigatório; também ADR-003, ADR-004 e ADR-005.
**Bloqueia implementação?:** sim.
**Status:** PENDING_APPROVAL.

## ADR-007 — Migração gradual e coexistência

**Decisão necessária:** qual sequência, coorte, ownership e evidência autorizam cada mudança de leitor/publicação?
**Recomendação:** inventariar e instrumentalizar; cercar escritores; preparar storage/backfill sem seleção pública; comparar sombra sem efeito público; migrar leitores e avaliações; habilitar publicação; migrar restore; desativar legado somente com prova de zero bypass. Flags começam desabilitadas e não combinam efeitos distintos.
**Justificativa:** há writers separados em CRUD, import, restore, taxonomy, seed, migrations e manutenção; shadow writes por rota podem duplicar divergências.
**Outras opções:** big-bang; sombra por endpoint; rollout gradual controlado.
**Consequências:** coexistência prolongada e necessidade de telemetria; reduz risco de cutover conjunto.
**Dependências:** todos os ADRs e baseline aprovado.
**Bloqueia implementação?:** não bloqueia documentação/instrumentação passiva após ADR-008; bloqueia qualquer cutover sem os gates.
**Status:** PENDING_APPROVAL.

## ADR-008 — Baseline e compatibilidade

**Decisão necessária:** qual SHA é implantado por ambiente e qual linha reconciliada receberá implementação?
**Recomendação:** não declarar baseline implantado com evidência atual. Solicitar digest em execução associado a SHA/proveniência e saúde por ambiente; depois selecionar uma linha de integração específica derivada do baseline de release aprovado e reconciliar commits/campos de e5 explicitamente.
**Justificativa:** main e staging remotos são identificáveis; e5 é snapshot local de auditoria. Há runs de build ligados a SHAs, mas não evidência de digest ativo nem deploy; os runs recentes de CI tiveram jobs de deploy ignorados.
**Outras opções:** main; staging; e5; linha própria reconciliada.
**Consequências:** atrasa código até obter evidência e decisão; evita implementar contra contratos não servidos.
**Dependências:** decisão inicial de infraestrutura e responsável pelo release.
**Bloqueia implementação?:** sim para runtime.
**Status:** PENDING_APPROVAL.
