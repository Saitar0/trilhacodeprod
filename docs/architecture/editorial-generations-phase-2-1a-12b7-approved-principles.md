# Fase 2.1A.12B.7 — Princípios aprovados em princípio

**Fonte:** deliberações explicitamente fornecidas pelo responsável nesta fase.
**Consolidação:** 2026-10-28; datas individuais das decisões não foram informadas.
**Natureza:** aceitação de direção arquitetural; não é aprovação de contrato implementável, implementação, migração, deployment ou cutover.

## ADR-001 — Revisão editorial e concorrência

Estado: `APPROVED_IN_PRINCIPLE`.

O escopo exato aprovado em princípio é: revisão monotônica por trilha atribuída pelo servidor; CAS para confirmar revisões; fencing contra writers obsoletos; cobertura de todos os writers relevantes; conflitos explícitos; preservar drafts sem rebase silencioso; snapshots editoriais coerentes/imutáveis; CAS distinto para seleção da generation publicada; instrumentar/validar writers antes de habilitar; proibir depender de dual-write divergente sem protocolo comprovado.

Limite: isso não prova cobertura de writers, segurança do legado, topologia/transações reais, compatibilidade do runtime ou mecanismo implementado. Os gates G1–G3 e G10 continuam abertos.

## ADR-002 — Sessões, tentativas e progresso

Estado: `APPROVED_IN_PRINCIPLE`.

Princípios aceitos: sessão vinculada a geração escolhida/registrada pelo servidor; avaliação pela definição privada da geração original; tentativas já em andamento continuam durante nova publicação; histórico mantém geração de origem; novas atividades vinculam-se à generation ativa no instante de criação; é possível impedir **novas sessões** em geração retirada por problema grave.

Não inferir que sessão já aberta será automaticamente revogada ou encerrada. Permanecem pendentes expiração, revogação urgente de sessões existentes, retomada, clientes legados, retenção de tentativas/histórico e progresso legado sem generation. Gates G4/G6/G7/G9/G10 aplicam-se conforme o caminho alterado.

## ADR-003 — Taxonomias

Estado: `APPROVED_IN_PRINCIPLE`.

Princípios aceitos: IDs estáveis; versão semântica quando o significado mudar; rótulos separados de significado; referências históricas preservadas; compatibilidade de leitores explícita; rejeição controlada de versões incompatíveis; nenhuma migração automática destrutiva do histórico.

Não foram aprovados schema, formato de versão, lista de taxonomias nem migração específica. Permanecem o inventário compartilhado, contratos, critérios de mudança semântica, estratégias de migração e compatibilidade legada. Gate G3/G7 continua aberto.

## ADR-004 — Retenção e exclusão

Estado: `PRINCIPLES_APPROVED_POLICY_PENDING` — somente os princípios abaixo estão aprovados.

1. Preservar gerações enquanto houver referências válidas.
2. Verificar dependências antes de exclusão irreversível.
3. Separar retenção editorial da retenção de dados pessoais.
4. Auditar exclusões.
5. Permitir retirar conteúdo emergencialmente sem exigir exclusão física.
6. Proibir garbage collection automático até aprovação das políticas necessárias.

Não há prazo, período de graça, política de retenção, elegibilidade de GC, decisão de anonimização ou aprovação de exclusão automática. ADR-004 não está integralmente aprovado; G9 permanece `BLOCKED`.

## ADR-005 — Segurança público/privado

Estado: `APPROVED_IN_PRINCIPLE`.

Princípios aceitos: defesa em profundidade; separação lógica de dados sensíveis; gabaritos e definições privadas protegidos; menor privilégio no MongoDB; DTOs públicos por allowlist explícita; serialização restritiva; fail-closed; testes negativos contra exposição; verificação posterior de grants reais; cobertura de endpoints legados.

Não implica que roles, separação física ou DTOs atuais já sejam seguros. Não autoriza alteração de usuário, role, grant ou schema. Gates G4/G6/G10 continuam abertos.

## ADR-006 — Publicação atômica

Estado: `APPROVED_IN_PRINCIPLE`.

Princípios e escopo aceitos: generation imutável da trilha inteira contendo aulas, blocos, exercícios e quizzes; preparação completa e validação prévia; seleção do head por um único CAS; leitores fixam generation por operação lógica; sem fallback silencioso para coleções mutáveis; rollback controlado que preserve histórico; sem publicação independente de quiz no início; habilitação só depois de consistência do snapshot, cobertura dos writers e proteção dos dados privados.

Não há autorização para implementar, selecionar head, cutover, modificar runtime ou criar segundo head de quiz. G2–G7/G10 continuam abertos.

## ADR-007 — Migração gradual

Estado: `APPROVED_IN_PRINCIPLE`.

Sequência arquitetural aceita para planejamento: (1) instrumentação passiva; (2) proteção e cobertura dos writers; (3) revisão, CAS e fencing; (4) armazenamento privado; (5) construção shadow; (6) comparação e validação; (7) leitores compatíveis; (8) cutover gradual; (9) monitoramento e rollback.

A sequência deve ser detalhada antes de executar, pode ser repartida em subfases e requer gates/autorizações separados. Esta aprovação não permite código, dados, flags, backfill, infraestrutura ou deployment. G1–G10 aplicam-se conforme etapa.

## ADR-008 — Baseline e compatibilidade

Estado: `BLOCKED_BY_EVIDENCE`; nenhuma aprovação foi concedida.

O baseline permanece parcialmente comprovado segundo 12B.4B. Não estão comprovados serviço de produção, imagem/digest ativo, cadeia container→imagem→build→commit, rota ativa, tráfego, readiness independente ou linha de release. Não escolher branch por nome/conveniência. G10 está bloqueado até chegar evidência sanitizada do administrador autorizado e decisão explícita da linha alvo.

## Aprovações que continuam separadas

Estas deliberações não aprovam: contrato de implementação; mudança de código/teste; schema/índice; migração/backfill; feature flag; acesso a staging/produção; alteração de infraestrutura; deployment; cutover; criação de generation pública; garbage collection; alteração de role/grant. Cada uma requer gates pertinentes e autorização específica posterior.

Matriz completa: [registro de deliberações](./editorial-generations-phase-2-1a-12b7-human-decision-register.md). Pendências e gates: [decisões pendentes](./editorial-generations-phase-2-1a-12b7-pending-decisions.md) e [gates técnicos](./editorial-generations-phase-2-1a-12b7-implementation-gates.md).
