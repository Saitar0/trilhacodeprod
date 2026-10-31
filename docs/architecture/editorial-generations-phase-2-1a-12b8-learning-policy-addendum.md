# Fase 2.1A.12B.8 — Adendo de políticas de aprendizagem

**Consolidação documental:** 2026-10-28.
**Fonte das deliberações:** declarações explícitas do responsável fornecidas para esta fase. As datas individuais das aprovações não foram informadas; este registro não reivindica assinatura digital nem validação criptográfica.
**Estado das cinco decisões:** `APPROVED_IN_PRINCIPLE`.
**Efeito:** registra decisões posteriores à Fase 12B.7 sem alterar seus documentos históricos e sem autorizar contratos executáveis, implementação, migração ou operação.

## 1. Relação com a Fase 12B.7

A Fase 12B.7 registrou as direções arquiteturais e os gates então conhecidos. Este adendo acrescenta políticas de produto para continuidade de sessões, retomada, retirada emergencial, correção de avaliações e certificados. Ele não modifica os oito ADRs originais nem a matriz original: os ADRs originais continuam `Proposed`, e as oito decisões daquela matriz continuam `PENDING_APPROVAL`. Os estados consolidados na B.7 também permanecem como registrados: ADR-004 continua `PRINCIPLES_APPROVED_POLICY_PENDING`, e ADR-008 continua `BLOCKED_BY_EVIDENCE`.

`APPROVED_IN_PRINCIPLE` aqui significa somente que o escopo descrito abaixo recebeu aprovação humana em princípio. Não aprova contrato técnico, modelo de dados, código, testes executáveis, migração, retenção concreta, feature flag, infraestrutura, deployment ou cutover.

Referências: [registro de deliberações B.7](./editorial-generations-phase-2-1a-12b7-human-decision-register.md), [princípios B.7](./editorial-generations-phase-2-1a-12b7-approved-principles.md), [pendências B.7](./editorial-generations-phase-2-1a-12b7-pending-decisions.md) e [gates B.7](./editorial-generations-phase-2-1a-12b7-implementation-gates.md).

## 2. Decisão 1 — Continuidade entre gerações

**Estado: `APPROVED_IN_PRINCIPLE`.** Relaciona-se aos ADRs 002 e 006.

Escopo aprovado:

1. Uma sessão iniciada permanece vinculada à geração editorial registrada para ela.
2. O aluno pode concluir atividades dessa geração enquanto ela permanecer válida e segura.
3. A correção usa a definição privada associada à geração original.
4. Uma nova sessão usa a geração ativa no momento de sua criação.
5. Uma retirada emergencial pode impedir a continuidade em caso grave.
6. O histórico registrado é preservado conforme as políticas de privacidade e retenção aplicáveis.

Esta decisão **não** define prazo universal de expiração, retenção ilimitada, reescrita de tentativas históricas nem obrigação de continuar após revogação de segurança. A validade, segurança e autorização de continuidade ainda precisam de contrato técnico e critérios aprovados.

## 3. Decisão 2 — Expiração e retomada de atividades

**Estado: `APPROVED_IN_PRINCIPLE`.** Relaciona-se aos ADRs 002, 004 e 006.

Escopo aprovado:

1. Atividades comuns permitem salvamento e retomada.
2. Fechar o navegador ou perder conectividade, por si só, não descarta progresso já persistido.
3. Quiz avaliativo permanece vinculado à tentativa e à geração originais.
4. Limites de tempo podem ser aplicados quando definidos pelas regras da atividade.
5. A recuperação consulta o estado persistido no servidor.
6. Retomada não cria automaticamente uma tentativa duplicada.
7. Sessão comprometida pode ser revogada com motivo auditável.
8. Resultado já registrado não é removido silenciosamente.

Continuam pendentes: prazos concretos de expiração; limites temporais específicos; tratamento de tentativa expirada; política de retenção; compatibilidade detalhada de clientes legados. Nenhuma duração ou comportamento para esses casos é estabelecido por este adendo.

## 4. Decisão 3 — Retirada emergencial de conteúdo

**Estado: `APPROVED_IN_PRINCIPLE`.** Relaciona-se aos ADRs 002, 005, 006 e 007.

Escopo aprovado:

1. Retirada por problema grave bloqueia novas sessões para a geração retirada.
2. Ocorrências são classificadas por gravidade.
3. Erro editorial comum não interrompe automaticamente atividade em andamento.
4. Sessões existentes são interrompidas somente quando necessário para risco grave de segurança ou integridade.
5. Retirada, motivo e tentativas potencialmente afetadas são registrados.
6. Uma geração corrigida pode ser publicada pelo protocolo de publicação já aprovado em princípio.
7. Histórico e respostas anteriores são preservados segundo a política aplicável.
8. Deve existir recuperação controlada para alunos afetados.

Continuam pendentes: critérios objetivos de gravidade; autoridade e permissões para retirada; procedimento operacional; regras exatas para retomada e novas tentativas; regras de notificação. Retirada emergencial não é exclusão física e não autoriza garbage collection.

## 5. Decisão 4 — Correção auditável de avaliações

**Estado: `APPROVED_IN_PRINCIPLE`.** Relaciona-se aos ADRs 002, 003, 004 e 006.

Escopo aprovado:

1. Respostas e avaliações originais são preservadas.
2. Erro identificado e definição corrigida são registrados.
3. Reavaliação auditável é permitida.
4. Nota anterior não é sobrescrita silenciosamente.
5. O aluno é informado quando uma avaliação sua é corrigida.
6. Devem existir mecanismos para ajustar resultados e conceder novas tentativas.
7. Deve ser rastreável a relação entre avaliação original, correção e novo resultado reconhecido.

Continuam pendentes: algoritmo de recálculo; condições de reavaliação; critérios para novas tentativas; efeitos em progresso e domínio de competências; tratamento de avaliações já usadas para certificação. O contrato futuro deve distinguir resultado histórico de resultado reconhecido após correção, sem presumir um modelo de dados específico.

## 6. Decisão 5 — Certificados e conquistas

**Estado: `APPROVED_IN_PRINCIPLE`.** Política transversal de avaliação, competências, gamificação e certificação; relaciona-se especialmente aos ADRs 002, 003 e 004, e aos ADRs 005–007 conforme o fluxo afetado.

Escopo aprovado:

1. Correção favorável permite reconhecer competências, conquistas e certificados que o aluno passou a merecer.
2. Correção desfavorável não revoga automaticamente conquista ou certificado já concedido.
3. Erro grave que comprometa validade de certificação pode levar a revisão excepcional e auditável.
4. Revogação exige decisão fundamentada e não é automática.
5. O aluno recebe comunicação sobre alterações relevantes.
6. São preservados os registros históricos de avaliação, correção, emissão, revisão e eventual revogação.

Continuam pendentes: critérios objetivos da revisão excepcional; processo de contestação; autoridade de revogação; prazos de revisão e notificação; atualização de credenciais; requisitos de retenção e privacidade. Esta decisão não escolhe algoritmo, fluxo administrativo ou esquema de dados.

## 7. Preservação e histórico

Este adendo é um registro posterior, não uma reescrita dos ADRs ou documentos B.7. A deliberação recebida é a fonte declarada; a consolidação documental não acrescenta aprovação ou autenticidade além do que foi informado. As cinco decisões ficam limitadas ao escopo textual acima. As pendências da B.7 e os gates técnicos continuam sujeitos a evidência e validação.

Para a matriz de dependências, critérios futuros e estado dos gates, consulte [dependências de políticas e gates](./editorial-generations-phase-2-1a-12b8-policy-dependencies-and-gates.md). Para limites de autorização e resultado desta fase, consulte o [relatório final](./editorial-generations-phase-2-1a-12b8-final-report.md).
