# Fase 2.1A.12C.15 — Ratificação das políticas de autoridade editorial

**Natureza:** especificação arquitetural documental e validadores offline. Nenhuma política foi instalada no IAM, nenhuma rota ou writer foi conectado e nenhum estado operacional foi consultado.

## Como interpretar esta ratificação

As políticas P1–P8 abaixo foram expressamente aprovadas pelo responsável para orientar o desenho. Essa ratificação não aprova nomes de responsáveis, schema operacional, concessão de grants, rollout, mudança de API ou implantação. As decisões técnicas e pendências com donos estão no [registro consolidado](editorial-generations-phase-2-1a-12c15-enforcement-contract.md) e na [matriz de prontidão](editorial-generations-phase-2-1a-12c15-readiness-gates.md).

## Políticas ratificadas

| ID | Política aprovada | Evidência anterior | Limite da aprovação |
|---|---|---|---|
| P1 | Grants por trilha devem ter uma autoridade primária capaz de ordenar concessão/revogação com a confirmação editorial. A preferência é estado MongoDB na mesma fronteira transacional. | C11/C12 provaram o mecanismo com dados sintéticos na mesma transação; C12 também produziu contraexemplo para consulta externa/projeção eventual. | Fonte, schema, topologia e grants implantados seguem pendentes de baseline e decisão operacional. |
| P2 | O papel `admin` não implica escopo editorial global; escopo global precisa ser provisionado e auditado explicitamente. | Código tem papéis e permissões globais; C11–C14 separaram papel de grant. | Provisionadores, aprovações independentes e recuperação ainda não foram nomeados. |
| P3 | Administradores devidamente autorizados podem governar grants. Responsáveis por trilha só delegam poderes explícitos que já possuem, sem escalonamento. | Proposta C13/C14; sem lifecycle operacional de grant no código atual. | Responsáveis nominais, separação de funções e exceção emergencial aguardam aprovação. |
| P4 | Revogação confirmada antes do commit impede a edição afetada; edição confirmada primeiro continua historicamente válida. | C11/C12 demonstraram ordenação sintética quando estado de autorização e edição participam da mesma transação. | Não generaliza a estados fora da transação nem à topologia implantada. |
| P5 | Commit deve respeitar mudanças relevantes de papel, sessão e estado do usuário por mecanismo de ordenação demonstrado; checagem inicial não basta. | C12 demonstrou documentos sintéticos; código versionado valida sessão/usuário por request. | A coordenação com o commit e a infraestrutura real não foram verificadas. |
| P6 | Mudança da matriz estática Python requer transição coordenada de versões e writers; deploy isolado não comprova revogação ordenada. | `PERMISSIONS` é código estático; não existe epoch persistido demonstrado. | Epoch, drenagem e plano de rollout ainda são desenho, não mecanismo operacional. |
| P7 | Mutação editorial e mudança relevante de autoridade exigem auditoria consistente. | C7 observou falha parcial de auditoria; C8–C12 validaram atomicidade experimental. | ACL, retenção, schema real e readers continuam pendentes. |
| P8 | Nenhum writer capaz de alterar estado protegido pode contornar a autoridade durante cutover. | C13/C14 enumeraram 17 caminhos versionados e concluíram que não havia onda segura selecionável. | O inventário é estático; operadores, ferramentas externas e runtime continuam `NOT_VERIFIED`. |

## Fatos versionados e recomendações

O código versionado declara `admin`, `editor` e `student`; `PERMISSIONS` concede permissões globais por papel. `security.current_user` valida JWT, sessão, usuário e estado da conta antes de anexar as permissões calculadas. As rotas usam `require(...)`, mas isso não comprova grants por trilha. As referências observadas na base C14 estão em [`security.py`](../../backend/security.py#L35-L110), [`sessions.py`](../../backend/services/sessions.py#L13-L83), [`permissions.py`](../../backend/permissions.py#L1-L31), [`constants.py`](../../backend/constants.py#L1-L16) e [`routes_content.py`](../../backend/routes_content.py#L156-L175). A C14 registrou que a matriz é estática e que grants por trilha não foram encontrados.

**Recomendação técnica:** manter uma única fonte primária de grants por trilha e fazê-la participar da fronteira transacional de confirmação, junto com os estados persistidos de usuário/sessão que a política determinar. A matriz de permissões por papel permanece um estado separado até que uma versão persistida seja coordenada com o rollout; não se deve tratá-la como se pudesse ser lida atomicamente do código dentro da transação. Não escolher nomes ou coleções operacionais nesta fase.

## Governança proposta

* **Conceder/remover operações e delegar:** uma autoridade IAM designada, ou responsável editorial formalmente provisionado com escopo delegável limitado. O código atual não define esse poder. Um grantor pode delegar apenas subconjunto do seu próprio escopo; não pode conceder a si mesmo, criar wildcard, nem delegar administração global se não possuir esse poder expressamente.
* **Revogar:** autoridade que pode conceder, ou autoridade superior independente. Revogação incrementa epoch e preserva o registro histórico; não apaga auditoria nem grants anteriores.
* **Transferir responsabilidade:** operação auditada que revoga a autoridade anterior e estabelece a nova sob uma regra de concorrência. Criador da trilha não é automaticamente proprietário permanente.
* **Escopo global:** registro explícito, versionado e revogável, separado do nome do papel. Recomenda-se provisionamento com separação de funções; autoconcessão é negada. O processo e o mecanismo de recuperação ainda exigem aprovação de produto/segurança.
* **Emergência:** negar por padrão se a autoridade falhar. Um caminho de emergência precisaria de finalidade limitada, aprovadores independentes, expiração, auditoria obrigatória e revisão posterior; sua existência não está aprovada.
* **Consulta de auditoria/histórico:** ACL própria por classe de registro e finalidade; editor não recebe acesso irrestrito por possuir `content.write`; aluno não ganha acesso por estar associado à trilha.

Os nomes “responsável editorial”, “grantor”, “revisor”, “auditor” e “operador de recuperação” são papéis conceituais propostos, não papéis ativos no IAM.

## Decisões ainda humanas

1. Nomear autoridade IAM, responsável de produto, responsáveis editoriais e aprovadores de recuperação.
2. Aprovar se escopo global será permitido e quem o provisiona/revoga, incluindo separação de funções.
3. Aprovar delegação, transferência de responsabilidade e resposta emergencial.
4. Aprovar fonte/grant lifecycle e relação com `users`, `auth_sessions` e permissões estáticas.
5. Aprovar política de API/clientes, ACL, retenção, exclusão, HMAC e recuperação de chaves.
6. Aprovar semântica de publicação, restauração, exclusão, progresso, tentativas e retirada emergencial.
7. Autorizar baseline ADR-008 pelo processo próprio e, depois, autorizar qualquer incremento operacional específico.

## Critério de fechamento

Uma decisão fecha somente quando o dono indicado registra escolha e responsável, os testes do contrato cobrem os casos positivos/negativos e a evidência operacional exigida é obtida em processo autorizado. Testes sintéticos mantêm o estado `VERIFIED_IN_ISOLATION`; não podem ser promovidos a prova operacional. A [matriz de prontidão C15](editorial-generations-phase-2-1a-12c15-readiness-gates.md) mantém esses bloqueios explícitos.

## Histórico preservado

Gates: G1 `PARTIAL`; G2 `NOT_VERIFIED`; G3 `NOT_VERIFIED`; G4 `PARTIAL`; G5 `NOT_VERIFIED`; G6 `PARTIAL`; G7 `PARTIAL`; G8 `NOT_VERIFIED`; G9 `BLOCKED`; G10 `BLOCKED`. ADR-008 permanece bloqueado. A C15 não altera a matriz histórica.
