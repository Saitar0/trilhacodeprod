# Fase 2.1A.12B.7 — Registro consolidado das deliberações humanas

**Data da consolidação documental:** 2026-10-28.
**Data individual das deliberações:** não informada.
**Origem:** texto de deliberação fornecido explicitamente pelo responsável do projeto na solicitação da Fase 12B.7. A procedência é registrada como declaração fornecida; não se afirma assinatura digital, verificação criptográfica ou autenticação independente da identidade.

## 1. Finalidade e leitura dos estados

Este registro documenta decisões arquiteturais em princípio e princípios aprovados, sem alterar os ADRs de origem e sem autorizar implementação. A decisão está limitada ao escopo escrito em cada item.

Estados desta consolidação:

- `APPROVED_IN_PRINCIPLE`: direção/princípios aceitos; contratos, evidências e gates de execução continuam necessários.
- `PRINCIPLES_APPROVED_POLICY_PENDING`: princípios de retenção aceitos; política concreta não aprovada.
- `BLOCKED_BY_EVIDENCE`: decisão não aprovada porque falta evidência necessária.
- `PENDING_APPROVAL` / `REQUIRES_CLARIFICATION`: escolhas não decididas; usar somente quando a pendência está explicitamente identificada.

## 2. Matriz consolidada

| ADR | Estado da deliberação | Escopo declarado | Pendências / limites | Gate técnico | Gate operacional |
|---|---|---|---|---|---|
| ADR-001 | `APPROVED_IN_PRINCIPLE` | Revisão monotônica por trilha, server-side; CAS de revisão; fencing; cobertura de writers; conflitos explícitos; draft preservado sem rebase; snapshot coerente e imutável; CAS separado da geração publicada; instrumentação/validação antes da habilitação; sem dual-write divergente não comprovado. | Aprovação não prova cobertura dos writers, segurança dos caminhos legados, transações/topologia, compatibilidade de runtime nem implementação. | Inventariar, instrumentar e demonstrar CAS/fence/idempotência/snapshot em todos os writers relevantes; ver G1–G3. | Baseline, processos/credenciais e capacidade de drenar/bloquear legado; G10. |
| ADR-002 | `APPROVED_IN_PRINCIPLE` | Sessões vinculadas a geração registrada pelo servidor; avaliar com definição privada original; tentativa em curso continua durante nova publicação; histórico mantém geração original; novas atividades usam geração ativa ao serem criadas; pode-se impedir novas sessões em geração retirada por problema grave. | Expiração, revogação de sessões existentes, retomada, clientes legados, retenção de tentativas/histórico e progresso legado sem geração. “Impedir novas sessões” não decide o destino de sessões já abertas. | Reader/session/attempt pinning, autorização, idempotência e avaliação histórica demonstrados; G4, G6 e G7. | Baseline/linha de release e política de retirada; G10. |
| ADR-003 | `APPROVED_IN_PRINCIPLE` | IDs estáveis; versão semântica quando significado muda; rótulo separado de significado; referências históricas preservadas; compatibilidade explícita; rejeição controlada de versões incompatíveis; sem migração automática destrutiva do histórico. | Inventário de taxonomias compartilhadas, contratos, critério de mudança semântica, estratégia de migração e compatibilidade legada. | Classificação campo/consumidor e testes de compatibilidade; G3, G4 e G7. | Owners de produto/frontend e baseline; G10. |
| ADR-004 | `PRINCIPLES_APPROVED_POLICY_PENDING` | Preservar geração enquanto houver referências válidas; verificar dependências antes de exclusão irreversível; separar retenção editorial e dados pessoais; auditar exclusões; permitir retirada emergencial sem purge físico obrigatório; sem GC automático antes das políticas. | Inventário completo de referências, política/prazos, privacidade, requisitos legais, exclusão/anonimização e elegibilidade de GC. Nenhum prazo é aprovado. | Grafo de referências, concorrência de GC e recuperação demonstrados; G9 permanece bloqueado. | Aprovação de produto, privacidade/jurídico e operação; nenhum GC antes disso. |
| ADR-005 | `APPROVED_IN_PRINCIPLE` | Defesa em profundidade; separação lógica; proteção de gabaritos/definições privadas; menor privilégio MongoDB; DTO público por allowlist; serialização restritiva; fail-closed; testes negativos; verificar grants reais; cobrir endpoints legados. | Não comprova grants, isolamento físico, segurança dos DTOs atuais, ausência de vazamento ou prontidão para implantação. | Projeções, papéis e todas as rotas/caches validados por testes negativos; G4 e G6. | Revisão de segurança e confirmação sanitizada de grants no baseline escolhido; G10. |
| ADR-006 | `APPROVED_IN_PRINCIPLE` | Generation imutável da trilha inteira incluindo aulas, blocos, exercícios e quizzes; preparar e validar antes; selecionar head por CAS único; readers fixados por operação lógica; sem fallback live; rollback preserva histórico; sem publicação independente de quiz inicialmente; habilitação depende de snapshot coerente, writers cobertos e privado protegido. | Aprovação não autoriza implementação, cutover, runtime ou segundo head público de quiz. | Manifest/chunks íntegros, source revision corrente, único head, CAS concorrente e reader fixado; G2–G7. | Baseline e ambiente de implantação comprovados; G10. |
| ADR-007 | `APPROVED_IN_PRINCIPLE` | Migração progressiva, reversível e governada por gates: instrumentar; cobrir/proteger writers; revisão/CAS/fencing; armazenamento privado; generations shadow; comparar/validar; readers compatíveis; cutover gradual; monitorar/rollback. Sequência deve ser detalhada e pode ser subdividida. | Não autoriza migração, dados, flags, backfill, cutover, infraestrutura ou deploy. Cada etapa requer gate e autorização independentes. | Critérios de saída, zero bypass, shadow sem efeito público, rollback seguro e telemetria; G1–G9 conforme escopo. | Baseline/owners/janela operacional; G10 e autorização específica. |
| ADR-008 | `BLOCKED_BY_EVIDENCE` | Nenhum baseline implantado ou linha de integração foi aprovada. | Produção, imagem/digest ativo, cadeia runtime→build→commit, rota/tráfego/readiness e release target não comprovados. Não inferir por nome ou branch. | Comparação de contratos após recebimento da evidência; gate técnico não se satisfaz com HEAD Git. | Administrador autorizado fornece metadados sanitizados solicitados em 12B.4B; G10. |

## 2. Dependências, aceitação técnica proposta e bloqueio

Os critérios abaixo tornam os gates operáveis; são **critérios técnicos propostos**, não conteúdo adicional aprovado pela deliberação humana.

| ADR | Dependências | Evidência/aceitação técnica mínima proposta | Bloqueio atual |
|---|---|---|---|
| 001 | ADR-003 para dependências globais; ADR-008 para base de runtime; G1–G3 | Inventário de writers fechado; cada writer instrumentado/adaptado ou bloqueado; testes de CAS/fence/replay/conflict; snapshot de revisão íntegra. | Cobertura completa e runtime não comprovados. |
| 002 | ADR-005/006 para reader/definition; ADR-004 para retenção; frontend/progresso | Sessão fixada pelo servidor; tentativa segue definition/evaluator originais; decisões de expiração/revogação/retomada; compatibilidade e testes A→B. | Política de sessão e retenção pendentes. |
| 003 | ADR-001/005/006 | Inventário por campo/consumidor; prova de separação ID/rótulo/semântica/schema; leitores aceitam ou rejeitam versões conhecidas de forma controlada. | Inventário e classificação não concluídos. |
| 004 | ADR-002/003/006 e revisão de privacidade/legal | Grafo de referências e policy por categoria aprovados; teste de concorrência de GC; política explícita de retenção, remoção e anonimização. | Policy e evidência de referências ausentes; GC proibido. |
| 005 | ADR-002/003 e baseline G10 | Grants reais verificados; routes/cache/preview cobertos; serializers allowlist; testes negativos provam ausência de gabaritos e dados privados. | Grants e cobertura de readers não comprovados. |
| 006 | ADR-001 obrigatório; ADR-003/005; ADR-002/004 para sessões/histórico | Generation integral válida; readiness/selagem; um head CAS; testes de concorrência, falha, lost response, reader pin e sem fallback. | Snapshot coerente, writers, fronteira e baseline ainda não passaram gates. |
| 007 | ADRs 001–006 conforme etapa; ADR-008 para runtime | Plano de etapa/coorte, owner, métricas e parada; backfill/shadow sem efeito público; rollback demonstrado; autorização por fase. | Nenhuma etapa operacional autorizada; owners e baseline pendentes. |
| 008 | Evidência operacional externa e aprovação do owner de release | Cadeia ambiente→serviço/container→digest→build→commit e rota/readiness/tráfego suficiente; linha alvo confirmada; matriz de compatibilidade revisada. | Dependência de evidência sanitizada do administrador. |

**Fonte humana de cada estado:** deliberações textualmente fornecidas pelo responsável na solicitação da Fase 12B.7.
**Próxima ação permitida:** registrar pendências, obter evidência externa autorizada e solicitar decisões adicionais.
**Próxima ação proibida por esta autorização:** implementar, migrar, alterar runtime/flags, deploy, cutover ou acesso a infraestrutura.

## 3. Níveis de aprovação separados

| Nível | Situação após esta fase |
|---|---|
| Direção/princípios arquiteturais | Aprovada em princípio para ADRs 001, 002, 003, 005, 006 e 007; princípios apenas para ADR-004. ADR-008 bloqueado. |
| Contrato técnico executável | Não aprovado automaticamente; requer detalhamento, evidências e revisão de engenharia/segurança. |
| Implementação de código | Não autorizada. |
| Migração/backfill | Não autorizados. |
| Deployment/alteração de infraestrutura | Não autorizados. |
| Cutover/feature flags | Não autorizados. |

Uma decisão em princípio não satisfaz G1–G10 nem autoriza a próxima etapa.

## 4. Preservação do histórico documental

Os ADRs originais 001–008 permanecem `Status: Proposed`, e a matriz original de B.3 permanece com oito linhas `PENDING_APPROVAL`, por preservação dos artefatos anteriores conforme esta fase. Este registro separado é a fonte documental das deliberações subsequentes; não finge que os arquivos originais foram atualizados.

O pacote B.6 dizia que nenhuma decisão estava aprovada **naquele momento**. A declaração humana fornecida depois, nesta fase, altera a situação decisória por meio deste registro novo, sem reescrever o histórico B.6 nem mudar o status formal dos ADRs originais.

### Deliberações que fecham ou refinam questões B.6

| ADR | Estado anterior em B.6 | Deliberação B.7 | Como preservar ambos os registros |
|---|---|---|---|
| 001 | Direção recomendada, cobertura e mecanismos ainda por deliberação/evidência. | Responsible aprovou em princípio os nove princípios de revisão/fence/CAS listados nesta fase. | Decisão de direção registrada; nenhuma cobertura ou garantia operacional inferida. |
| 002 | Sessão híbrida recomendada; duração, retomada e revogação em aberto. | Ficou explícito que tentativas em curso continuam através de nova publicação, o histórico permanece na geração original e novas atividades usam geração ativa na criação. | Estes pontos são decisões em princípio; expiração, revogação de sessão existente, retomada, clientes legados e retenção continuam abertos. |
| 003 | Matriz semântica/campo a campo pendente. | Princípios de IDs, versionamento semântico, rótulos, histórico e rejeição de incompatibilidade foram aprovados em princípio. | Os princípios foram aceitos; inventário e contratos concretos seguem pendentes. |
| 004 | GC bloqueado por evidência/policy. | Princípios de preservação, verificação de referências, separação PII, auditoria e retirada sem purge físico foram aceitos. | O bloqueio de GC permanece; policy e prazos continuam pendentes. |
| 005 | Defesa em profundidade recomendada; grants desconhecidos. | Princípios de separação lógica, least privilege, allowlist, fail-closed e cobertura de legado foram aprovados em princípio. | Aprovação não prova grant/DTO nem elimina gate de segurança. |
| 006 | Unidade de quiz independente ainda era pergunta de produto; generation track-wide era recomendação inicial. | Ficou decidido em princípio que aula/blocos/exercícios/quizzes pertencem à generation integral da trilha e não há publicação de quiz independente inicialmente. | Questão resolvida para o escopo inicial; nenhum segundo head aprovado; detalhes técnicos e cutover seguem pendentes. |
| 007 | Rollout gradual recomendado, sem execução autorizada. | A direção e a sequência de nove etapas foram aprovadas em princípio. | Plano detalhado, subfases, gates e autorização individual continuam necessários. |
| 008 | Baseline operacional bloqueado. | Nenhuma aprovação; permanece bloqueado por evidência. | B.7 não consulta infraestrutura e não altera status. |

## 5. Referências

- [Contratos fundamentais B.6](./editorial-generations-phase-2-1a-12b6-final-report.md) e [decisões/maturidade B.6](./editorial-generations-phase-2-1a-12b6-human-decisions.md).
- [Matriz original B.3](./editorial-generations-phase-2-1a-12b3-decisions.md).
- [Pacote de aprovação B.5](./editorial-generations-phase-2-1a-12b5-approval-packet.md).
- [Solicitação sanitizada de evidências do ADR-008 B.4B](./editorial-generations-phase-2-1a-12b4b-admin-evidence-request.md).
- Os arquivos de ADR permanecem em [`adr-editorial-generations/`](./adr-editorial-generations/).

## 6. Referências arquiteturais por ADR

| ADR | Fonte anterior mais diretamente relacionada |
|---|---|
| 001 | [`Protocolo de revisão B.6`](./editorial-generations-phase-2-1a-12b6-revision-protocol.md) e [`coexistência de writers B.6`](./editorial-generations-phase-2-1a-12b6-writer-coexistence.md). |
| 002 | [`ADR-002 original`](./adr-editorial-generations/ADR-002-learning-session-generation.md) e [decisões/maturidade B.6](./editorial-generations-phase-2-1a-12b6-human-decisions.md). |
| 003 | [`ADR-003 original`](./adr-editorial-generations/ADR-003-versioned-taxonomies.md) e [contrato de geração B.6](./editorial-generations-phase-2-1a-12b6-generation-contract.md). |
| 004 | [`ADR-004 original`](./adr-editorial-generations/ADR-004-retention-and-deletion.md) e [pendências B.6](./editorial-generations-phase-2-1a-12b6-human-decisions.md). |
| 005 | [`Fronteira público/privado B.6`](./editorial-generations-phase-2-1a-12b6-public-private-boundary.md) e [`ADR-005 original`](./adr-editorial-generations/ADR-005-public-private-data-separation.md). |
| 006 | [`Contrato de geração B.6`](./editorial-generations-phase-2-1a-12b6-generation-contract.md) e [`ADR-006 original`](./adr-editorial-generations/ADR-006-atomic-publication.md). |
| 007 | [`Coexistência de writers B.6`](./editorial-generations-phase-2-1a-12b6-writer-coexistence.md) e [`gates B.6`](./editorial-generations-phase-2-1a-12b6-integrated-invariants.md). |
| 008 | [Evidência do runtime B.4B](./editorial-generations-phase-2-1a-12b4b-final-report.md) e [pedido sanitizado B.4B](./editorial-generations-phase-2-1a-12b4b-admin-evidence-request.md). |
