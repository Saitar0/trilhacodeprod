# Fase 2.1A.12B.8 — Dependências de políticas e gates

Este documento associa as cinco decisões do [adendo de políticas](./editorial-generations-phase-2-1a-12b8-learning-policy-addendum.md) aos ADRs e aos gates da B.7. Os requisitos aqui registrados são critérios futuros de validação, não evidência de que mecanismos, testes ou políticas já existam.

## 1. Estado histórico dos gates

| Gate B.7 | Estado preservado | Relação com este adendo |
|---|---|---|
| G1 — Cobertura de escritores | `PARTIAL` | Correções, retirada e concessão/atualização de resultados podem introduzir escritores adicionais; inventariá-los se entrarem no escopo. |
| G2 — Revisão editorial | `NOT_VERIFIED` | Mudança de definição que gere novo conteúdo editorial deve respeitar revisão/CAS/fencing; a política de retomada, por si só, não prova G2. |
| G3 — Snapshot coerente | `NOT_VERIFIED` | Definição de avaliação e referências semânticas usadas por uma geração precisam corresponder à sua origem; testar quando o fluxo de correção alterar conteúdo versionado. |
| G4 — Fronteira público/privado | `PARTIAL` | Definições privadas, decisões de retirada, resultados e dados de certificados exigem autorização e projeções apropriadas nos leitores aplicáveis. |
| G5 — Publicação atômica | `NOT_VERIFIED` | Geração corrigida ou restaurada precisa seguir a seleção única aprovada em princípio; retirada deve impedir exposição/novas sessões conforme o contrato futuro, sem criar head paralelo inadvertido. |
| G6 — Leitores e sessões | `PARTIAL` | Principal gate impactado: pinning, retomada, revogação, avaliação histórica, correção auditável e propagação segura do estado ao aluno. |
| G7 — Compatibilidade | `PARTIAL` | Compatibilidade de clientes, progresso legado, tentativas, resultados corrigidos, notificações e credenciais precisa ser definida e testada. |
| G8 — Migração shadow | `NOT_VERIFIED` | Nenhuma correção ou comparação shadow pode alterar resultados, sessões, certificados ou respostas públicas antes dos gates de cutover. |
| G9 — Retenção | `BLOCKED` | Sessões, tentativas, resultados, auditoria e certificados criam referências que precisam ser inventariadas; não há prazo aprovado nem GC. |
| G10 — Baseline operacional | `BLOCKED` | Estados de retirada/emergência e rollout operacional dependem de baseline e autorização; esta fase não acrescenta evidência operacional. |

Os estados acima são os da matriz B.7 e são reproduzidos para rastreabilidade. Nenhum estado foi promovido ou satisfeito nesta fase. Aprovação humana não é evidência técnica.

## 2. Matriz decisão → ADR → gate

| Decisão | ADRs relacionados | Gates diretamente afetados | Critérios adicionais a validar futuramente | Pendências que permanecem |
|---|---|---|---|---|
| D1 — Continuidade entre gerações | ADR-002, ADR-006 | G6, G7, G9; G5 como dependência da identidade/retirada da geração | Testar que sessão persiste a geração escolhida pelo servidor; tentativa antiga usa definição privada original após publicação B; acesso bloqueado quando a geração deixa de ser válida/segura; referências impedem descarte indevido. | Critério de validade/segurança, revogação de sessões existentes, retenção e expiração. |
| D2 — Expiração e retomada | ADR-002, ADR-004, ADR-006 | G6, G7, G9 | Fechar/reabrir cliente e retomar estado do servidor; retry não duplica tentativa; submissão usa tentativa/geração originais; revogação registra motivo; resultado registrado não desaparece silenciosamente. | Prazos, limites por atividade, semântica de tentativas expiradas, retenção e clientes legados. |
| D3 — Retirada emergencial | ADR-002, ADR-005, ADR-006, ADR-007 | G4, G5, G6, G7, G9; G10 como pré-condição operacional | Provar bloqueio de novas sessões na geração retirada; distinguir erro editorial comum de risco grave; interrupção de sessão exige condição de risco definida; registrar motivo/impacto; publicar correção pela geração integral; preservar histórico e recuperação. | Severidade objetiva, autoridade, procedimento, retomada/retry, notificação e evidência operacional. |
| D4 — Correção auditável de avaliações | ADR-002, ADR-003, ADR-004, ADR-006 | G4, G6, G7, G9; G1–G3/G5 se a correção escrever conteúdo editorial versionado | Preservar resposta e resultado originais; ligar correção à definição privada original/corrigida; novo resultado distinguível do histórico; notificação; idempotência e trilha auditável; compatibilidade de progresso e certificados. | Algoritmo, elegibilidade, novas tentativas, impacto em competências, certificações, retenção. |
| D5 — Certificados e conquistas | Política transversal; ADR-002, ADR-003, ADR-004, ADR-005, ADR-006 e ADR-007 conforme fluxo | G6, G7, G9; G4 se dados forem lidos/publicados; G1/G2/G5 se houver writer/geração editorial | Correção favorável reconhece novo direito sem duplicar concessão; desfavorável não revoga automaticamente; revisão excepcional exige decisão fundamentada e auditável; preservar estados históricos; notificar alterações; manter referências protegidas. | Critérios de exceção, contestação, autoridade, prazos, atualização de credenciais, privacidade/retenção. |

**Escopo condicional:** gates adicionais são aplicáveis apenas se a futura implementação tocar o mecanismo que o gate protege. A condição não reduz a exigência já existente do gate correspondente nem declara o trabalho concluído.

## 3. Requisitos de validação por domínio

### Sessões e retomada

- Identidade da geração deve vir do estado autorizado pelo servidor, não de uma escolha arbitrária do cliente.
- Testes futuros devem cobrir nova publicação durante sessão, retomada após desconexão, repetição de requisição e revogação auditável.
- Estado persistido deve ser recuperável sem criar tentativa duplicada por retry.
- O resultado já registrado deve continuar rastreável; esta política não define quando uma tentativa expira nem o que ocorre depois disso.

### Avaliação e correção

- A definição privada usada na tentativa inicial deve permanecer identificável para correção histórica.
- Correção deve acrescentar uma relação auditável e não substituir silenciosamente resposta, nota ou avaliação anterior.
- Testes devem distinguir resultado histórico, reavaliação e resultado reconhecido após correção; a representação física continua em aberto.
- Notificação, concessão de nova tentativa e efeitos em domínio de competências requerem regras de produto antes da implementação.

### Retirada emergencial

- O modelo futuro precisa diferenciar impedimento de novas sessões de interrupção de sessões existentes.
- Interrupção exige critério de gravidade e autoridade definidos; erro editorial comum não pode ser convertido em revogação automática.
- Logs/auditoria devem registrar motivo e escopo afetado sem expor respostas ou dados pessoais desnecessários.
- Recuperação/publicação corrigida deve usar o protocolo aprovado em princípio; retirada não deve virar exclusão física nem GC.

### Conquistas e certificados

- Concessão após correção favorável e revisão excepcional devem ser idempotentes e auditáveis.
- Correção desfavorável não pode provocar revogação automática.
- Revogação, se aplicável, necessita decisão fundamentada, comunicação e histórico preservado; o fluxo e as autoridades ainda não foram definidos.
- Critérios e eventos de certificação precisam de avaliação de privacidade e retenção; não há política completa de retenção aprovada.

## 4. Pendências humanas e evidências

| Tema | Deliberado em princípio | Ainda depende de decisão/evidência |
|---|---|---|
| Sessões | Pinning por geração, conclusão enquanto válida/segura, nova sessão na geração ativa | Expiração, renovação, revogação, retomada detalhada, clientes legados e progresso sem geração. |
| Atividades | Salvamento/retomada do persistido; avaliação ligada à tentativa original; regras da atividade podem definir limite | Duração concreta, estados após expiração e submissões tardias. |
| Emergência | Bloquear novas sessões; interrupção seletiva por risco grave; trilha auditável e recuperação | Taxonomia de gravidade, autoridade, procedimento, tentativas e notificações. |
| Correção | Preservação, reavaliação auditável e comunicação | Recálculo, elegibilidade, competências, novas tentativas e certificações existentes. |
| Certificados | Crédito favorável; sem revogação desfavorável automática; exceção fundamentada | Critérios, contestação, autoridade, prazos, atualização da credencial e retenção. |
| Retenção | Aplicam-se princípios já registrados no ADR-004 | Grafo de referências, prazo/política, privacidade/jurídico e elegibilidade de exclusão; G9 continua `BLOCKED`. |
| Baseline | Nenhuma evidência nova foi coletada nesta fase | ADR-008/G10 permanecem bloqueados; não consultar Coolify/GHCR nesta fase. |

## 5. Estado e autorização

As cinco decisões novas constam como `APPROVED_IN_PRINCIPLE`, exclusivamente no adendo desta fase. O estado B.7 de ADR-004 permanece `PRINCIPLES_APPROVED_POLICY_PENDING`; ADR-008 permanece `BLOCKED_BY_EVIDENCE`. Os oito ADRs originais permanecem `Proposed` e a matriz histórica permanece `PENDING_APPROVAL` conforme o registro B.7.

Esta consolidação não aprova políticas pendentes, contratos de implementação, schemas, testes executáveis, migração, backfill, flags, alteração de grants, operação, deployment, cutover, exclusão ou garbage collection. Os gates continuam exigindo evidência objetiva e autorização específica posterior.

Referências: [gates históricos B.7](./editorial-generations-phase-2-1a-12b7-implementation-gates.md), [pendências B.7](./editorial-generations-phase-2-1a-12b7-pending-decisions.md), [adendo desta fase](./editorial-generations-phase-2-1a-12b8-learning-policy-addendum.md).
