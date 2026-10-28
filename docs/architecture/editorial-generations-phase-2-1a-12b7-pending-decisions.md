# Fase 2.1A.12B.7 — Pendências que permanecem abertas

**Regra:** este arquivo não reabre princípios já `APPROVED_IN_PRINCIPLE`; discrimina políticas, contratos e evidências ainda não decididos. Aprovação em princípio não satisfaz gate técnico.

## 1. ADR-001 — o princípio está aprovado; prova e detalhes de execução faltam

**Contrato de implementação:** `PENDING_APPROVAL`. **Cobertura efetiva dos writers:** `BLOCKED_BY_EVIDENCE`.

Deliberado: revisão monotônica por trilha, server-side, CAS, fencing, cobertura de writers, conflitos explícitos, drafts preservados, snapshots coerentes, CAS distinto para publicação, instrumentação/validação prévia e sem dual-write divergente não comprovado.

Pendências de implementação/evidência:

- Lista completa de rotas, scripts, seeds, jobs, workers e identidades que alteram conteúdo em cada ambiente.
- Prova de como writers antigos serão drenados/bloqueados e como bypass é negado; não basta inserir token de fence em caminho novo.
- Contrato detalhado de `operation_id`, fingerprint, conflito HTTP, recuperação de operação parcial, lineage/receipts e período necessário para replay.
- Topologia MongoDB alvo, write concern/journaling e garantias de persistência; a homologação da PoC standalone não comprova o ambiente da aplicação.
- Critérios para alterações globais (reordenação de trilhas, tags/taxonomias) que não cabem num único revision head por trilha.

Não há decisão nova sobre granularidade mais fina ou merge/rebase. A direção por trilha é a aprovada; qualquer exceção futura requer deliberação explícita.

## 2. ADR-002 — políticas de produto ainda pendentes

**Estado das políticas listadas abaixo:** `REQUIRES_CLARIFICATION`.

Princípios aprovados: sessão server-pinned; avaliação usa definição privada original; tentativas em andamento continuam com nova publicação; histórico permanece ligado à geração de origem; atividade nova usa a geração ativa no momento de criação; pode-se impedir abertura de sessões novas para geração retirada.

Decisões pendentes explicitamente:

1. Expiração e renovação de sessão.
2. Revogação urgente de sessões **existentes** e UX/comunicação correspondente.
3. Retomada de sessão após republicação ou desconexão.
4. Compatibilidade e transição de clientes legados.
5. Retenção de tentativas/histórico.
6. Tratamento de progresso legado que não tem generation comprovável.

Ainda falta contrato técnico de autorização do session token, submissões tardias e resultado após revogação; não inferir comportamento definitivo.

## 3. ADR-003 — classificação semântica pendente

**Estado da matriz de campo e contrato semântico:** `REQUIRES_CLARIFICATION`.

Princípios aprovados: identidades estáveis, versionamento semântico quando muda significado, rótulo separado da semântica, referências históricas preservadas, compatibilidade explícita, rejeição controlada e sem migração destrutiva automática.

Pendências: inventário real das taxonomias compartilhadas; classificação campo/consumidor; definição do evento que incrementa versão semântica; contrato entre backend/frontend/renderer/evaluator; migração de dados e compatibilidade com leitores antigos. Não incluir conteúdo curricular nem presumir taxonomias não identificadas.

## 4. ADR-004 — política continua pendente

**Política completa:** `PENDING_APPROVAL`. **Inventário/requisitos ainda ausentes:** `BLOCKED_BY_EVIDENCE`.

Somente os seis princípios listados em [princípios aprovados](./editorial-generations-phase-2-1a-12b7-approved-principles.md) foram aceitos. Permanecem pendentes: grafo completo de referências; política e prazo por categoria; privacidade e requisitos legais; autoridade para hard delete; anonimização quando aplicável; período de graça; critérios técnicos de elegibilidade e concorrência de GC.

Até resolução formal e G9 aprovado: nenhuma garbage collection automática, nenhuma exclusão física por geração e nenhuma janela de retenção inventada. Retirada emergencial de acesso não equivale a purge.

## 5. ADR-005 — implantação técnica da fronteira

**Contrato técnico de isolamento:** `PENDING_APPROVAL`. **Grants/cobertura real:** `BLOCKED_BY_EVIDENCE`.

Princípios aceitos, mas não comprovados: papéis/grants efetivos, isolamento de candidates, serviços/identidades separados, allowlist por DTO/versão, routes/cache/log cobertos, fail-closed em todos os caminhos e segurança de dados legados. O inventário estático B.6 não é grant review e não demonstra produção.

Antes do reader público: threat model de coleções/bancos/processos; prova de principal learner incapaz de ler gabaritos/drafts; auditoria de previews, catálogos, endpoints legados e cache; testes negativos em DB descartável.

## 6. ADR-006 — detalhes de contrato e cutover

**Contrato técnico/cutover:** `PENDING_APPROVAL` após a direção de princípio aprovada.

Princípios aprovados: uma generation da trilha inteira incluindo quizzes; nenhuma publicação independente de quiz inicialmente; único CAS de head; readers fixados; sem fallback live; rollback com histórico preservado.

Pendências: layout final de manifesto/chunks e digests; limites BSON/carga; mecanismo de readiness/selagem; write concerns; manejo de publicação concorrente e resposta perdida; política de cache/revogação; comportamento de indisponibilidade; procedimento de rollback sem leitor legado. Os detalhes devem implementar a escolha de geração integral e não introduzir segundo head de quiz por conveniência.

## 7. ADR-007 — operacionalização da sequência

**Plano detalhado e gates por fase:** `PENDING_APPROVAL`; nenhuma fase operacional está autorizada.

Direção progressiva aprovada, não cronograma/execução. Faltam owners por gate, escopo de coorte, telemetria, limites de parada, procedimento de freeze/drain, critérios de rollback, sequência de compatibilidade de deploy e autorização por subfase. Nenhuma flag foi autorizada.

## 8. ADR-008 — dependência externa bloqueante

**Estado:** `BLOCKED_BY_EVIDENCE`.

Nenhuma aprovação de baseline. Necessário receber a evidência sanitizada do administrador autorizado conforme [pedido existente B.4B](./editorial-generations-phase-2-1a-12b4b-admin-evidence-request.md), confirmar serviço de produção, container/image digest ativos, build/SHA, rota e readiness/tráfego, e escolher explicitamente ambiente/linha de release. Nenhuma consulta a Coolify/GHCR será feita nesta fase.

## 9. Integridade do estado original

Os oito ADRs originais permanecem `Proposed`; as oito linhas da matriz B.3 seguem `PENDING_APPROVAL`. Os novos estados de deliberação são mantidos somente no [registro B.7](./editorial-generations-phase-2-1a-12b7-human-decision-register.md). Isso preserva a distinção entre registro humano posterior e status formal dos artefatos originais.
