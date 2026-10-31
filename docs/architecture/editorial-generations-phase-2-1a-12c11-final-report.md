# Fase 2.1A.12C.11 — Relatório final

## A. Resultado executivo

Foi implementado e validado em MongoDB 7 descartável um modelo C11 de autorização por trilha, capability assinada no servidor de teste, revalidação de permissão, revogação ordenada com commit, reconciliação interna escopada, consulta externa sujeita à autorização atual e redução do conteúdo privado a metadados/HMAC na fronteira experimental. Não houve integração com aplicação ativa.

**Veredito:** **POLÍTICA EDITORIAL PARCIALMENTE VALIDADA — DECISÕES E EVIDÊNCIAS PENDENTES**. A prova persistente C11 passou; JWT, sessão, escopo IAM, armazenamento de segredos e revogação operacionais não foram exercitados.

## B. Git e isolamento

* Base exata: `760a045354cce922fe19cf74bea8d42f8f7e0ac5`.
* Worktree: `C:\Users\Joao\.codex\worktrees\trilhacode-fase2-1a-12c11-editorial-authorization-replay\trilhacodeprod`.
* Branch: `codex/fase2-1a-12c11-editorial-authorization-replay`.
* Checkout preparado com sparse-checkout antes de materializar arquivos; diretórios de curso e migração não foram materializados.
* Nenhuma outra worktree, branch remota ou checkout original foi alterado.
* A documentação e o código experimental desta fase são entregues em commit exclusivamente local; o identificador imutável está no `HEAD` desta revisão.
* Nenhum push/PR/merge/rebase foi executado.

## C. IAM observado e limites

A inspeção C10 registrou `PUT /api/blocks/{block_id}`, dependência `require("content.write")`, JWT/sessão verificadas em `current_user` e permissões por papel. Não demonstrou autorização de escrita por trilha. A evidência e linhas estão em [contrato API/IAM C10](editorial-generations-phase-2-1a-12c10-api-iam-async-contract.md#fronteira-http-atual), que aponta para os arquivos reais versionados.

C11 usa principal atestado, sessão, papel, grant e revogação inteiramente sintéticos. O código C11 exige simultaneamente autenticação atestada, sessão válida, `content.write`, escopo explícito da trilha e operação permitida. Administrador não recebe escopo global por papel; um grant `*` somente é aceito quando explicitamente provisionado como política de teste. Nenhuma alegação de validação de IAM real é feita.

## D–F. Capability, revogação e autorização

A capability de teste é HMAC-assinada pelo gate após autorizar o principal. Seus claims incluem ator, papel, digest da sessão, trilha, escopo do grant, operação, operation ID, epoch, writer, credencial, fence, revisão-base e preparação C8. Alterações em claims são rejeitadas; fence e capability não são permissão equivalente.

Antes da preparação, consulta ao grant falha fechada. Antes do commit, o estado é revalidado; o participante C11 condicionalmente grava no documento de grant dentro da transação C8. Essa escrita participa da mesma transação da autoridade de revisão/fence, auditoria e recibo. **Testado:** revogação antes da preparação, após preparação e antes de confirmar; corrida real entre cliente de commit e cliente revogador; não houve estado parcial. O teste de papel também rejeita a reutilização da capability quando o mesmo ator mantém `content.write`, mas muda de `editor` para `admin`.

Isso demonstra ordenação somente no store sintético compartilhado pela transação. Se o IAM real estiver fora do MongoDB editorial, uma consulta inicial não elimina corrida de revogação. A capability Python e sua chave sintética não são uma fronteira de segurança de produção.

## G. Replay

O replay de uma operação confirmada não repete alteração nem auditoria e devolve somente o resultado histórico mínimo. O cenário após remover o bloco mantém o recibo e não recria o documento. A consulta externa exige principal/capability/grant atuais; após revogação, mudança de papel, sessão inválida, ator ou assinatura divergente, é negada.

A reconciliação interna exige passe assinado vinculado exatamente ao DB, namespace, trilha e operação e lê com primary/majority; o resultado não contém payload. O teste rejeita outro ator/segredo e tentativa de reutilizar o passe em outra trilha. A chave de idempotência não concede acesso. O passe interno não expira nem é de uso único, pendência para um serviço real protegido.

## H–J. Privacidade, HMAC, ACL e retenção

O builder aceita apenas campos editáveis conhecidos e não armazena valores de patch. A intenção protocolar guarda versão, operação, nomes de campos e HMACs com separação de domínio. Auditoria sintética inclui ator sintético e referência keyed; recibo inclui revisão e revisão-pai. O teste inspecionou registros e não encontrou o valor privado sintético. HMAC não é criptografia: não protege o conteúdo do próprio bloco nem define sua ACL.

Versão de chave e coexistência foram exercitadas: replay de operation ID antigo funciona enquanto a chave antiga permanece; chave ausente falha fechado. Chaves são fixas/sintéticas em memória. Não foram definidas rotação operacional, retenção, revogação emergencial, ACL real para auditoria/histórico, prazos ou elegibilidade de garbage collection. O C8 genérico aceita payload arbitrário, então minimização é garantida somente pela fronteira C11 testada, não por todos os chamadores C8.

## K–M. Transação, cancelamento e commit indeterminado

O adaptador usado foi `AsyncEditorialRevisionAdapter` da C10, com a mesma autoridade C8 de revisão/fence. A autorização sintética é gravada junto à transação; o teste C11 executou MongoDB 7. Falha de auditoria e cancelamento no callback pré-commit abortam grant-use, bloco, auditoria, revisão e recibo. A corrida entre autorização/revogação usa clientes independentes.

Uma exceção C11 `CommitOutcomeUnknown` foi injetada **depois** de um commit real para modelar resposta perdida; reconciliação persistente encontrou o recibo original, sem segunda revisão/auditoria. Isso não é uma falha de rede, não é o driver emitindo `UnknownTransactionCommitResult` e não testa cancelamento durante o commit. Também não houve failover ou reinício do servidor.

## N–O. Testes e ambiente

Ambiente: Python 3.11.9, PyMongo 4.18.2, Pytest 9.1.1, MongoDB oficial `7.0.43`, replica set descartável de nó único `rsC11`, WiredTiger, sessões lógicas ativas. A imagem usada foi `mongo:7.0.43`; topologia limitada a um nó, sem prova de failover multinó.

* Integrações persistentes C11: **9/9 aprovadas em duas execuções limpas**; 0 falhas, 0 skips, além de uma execução direcionada aprovada para a guarda da URI.
* Unitários C11 de política e privacidade: **13 aprovados**.
* Regressões offline C1/C2/C5/C6/C10 e PoC: **136 testes + 38 subtests aprovados**.
* Ruff: aprovado para os seis módulos/testes novos C11.
* Mypy: aprovado em quatro módulos C11.
* Compilação sintática: aprovada.
* `git diff --check`: sem problemas.

As suítes persistentes de fases anteriores com URI/porta/replica set próprios não foram executadas nem reutilizadas. Os cenários C11 exercitam o adaptador async C10 no banco exclusivamente C11, e as regressões offline foram executadas separadamente.

## P. Segurança, escopo e Gates

Nenhum writer, rota, serviço, schema operacional, configuração, worker, IAM ativo ou conteúdo curricular foi alterado. Novos módulos são importados apenas por testes. Durante uma tentativa inicial de teste negativo, o parser PyMongo tentou resolver DNS SRV para `example.invalid` e recebeu `NXDOMAIN`; nenhum banco, API ou serviço operacional foi contatado. O harness passou a rejeitar `mongodb+srv` antes do parser, e a regressão passou sem DNS. Não houve acesso a banco operacional, staging, produção, Coolify ou GHCR. Os documentos não contêm segredos reais ou dados pessoais.

Estados históricos preservados, sem promoção: G1 `PARTIAL`; G2 `NOT_VERIFIED`; G3 `NOT_VERIFIED`; G4 `PARTIAL`; G5 `NOT_VERIFIED`; G6 `PARTIAL`; G7 `PARTIAL`; G8 `NOT_VERIFIED`; G9 `BLOCKED`; G10 `BLOCKED`. ADR-008 continua bloqueado.

## Q–R. Limpeza e arquivos

MongoDB e rede exclusivos foram verificados pela identidade e removidos após os testes; o banco de cada teste foi removido somente depois de comprovar seu marcador C11. Não há volume persistente. Nenhum recurso de outra fase foi encerrado. A worktree será limpa pelo commit exclusivamente local.

Arquivos novos:

* `backend/curriculum_contract/experimental_editorial_authorization.py`
* `backend/curriculum_contract/experimental_editorial_privacy.py`
* `backend/curriculum_contract/experimental_editorial_replay_policy.py`
* `backend/integration_tests/editorial_authorization_harness.py`
* `backend/integration_tests/test_editorial_authorization.py`
* `backend/unit_tests/test_experimental_editorial_privacy_policy.py`
* `docs/architecture/editorial-generations-phase-2-1a-12c11-authorization-replay-policy.md`
* `docs/architecture/editorial-generations-phase-2-1a-12c11-final-report.md`

## S. Próximo incremento

Uma decisão de produto/IAM sobre a fonte oficial de autorização por trilha e a ordenação de sua revogação com uma confirmação editorial. Sem essa escolha, não há base para ligar a capability experimental à identidade operacional. Isso não autoriza integração nesta fase.

## T. Veredito

**POLÍTICA EDITORIAL PARCIALMENTE VALIDADA — DECISÕES E EVIDÊNCIAS PENDENTES.** O núcleo sintético persistente demonstrou os cenários previstos no escopo, mas as condições de IAM, chaves, ACL, retenção, commit indeterminado real e runtime implantado continuam pendentes; integração operacional não autorizada.
