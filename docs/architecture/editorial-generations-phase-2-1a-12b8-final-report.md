# Fase 2.1A.12B.8 — Relatório final

## A. Resumo executivo

As cinco deliberações humanas posteriores à Fase 12B.7 foram registradas fielmente em documentação nova: continuidade entre gerações, expiração/retomada, retirada emergencial, correção auditável de avaliações e proteção de certificados/conquistas. Cada decisão foi classificada `APPROVED_IN_PRINCIPLE`, sem ampliar o escopo aprovado.

O adendo explicita pendências de produto, privacidade, retenção, contrato técnico e operação. Os gates da B.7 foram reproduzidos com os mesmos estados e critérios adicionais propostos foram separados de evidência verificada. Nenhuma implementação está autorizada.

## B. Git e isolamento

- Worktree exclusiva: `C:\Users\Joao\.codex\worktrees\trilhacode-fase2-1a-12b8-learning-policy-addendum\trilhacodeprod`.
- Branch: `codex/fase2-1a-12b8-learning-policy-addendum`.
- Base e parent esperado: `d8a02fe6c2e8fe0bf5fdc33871af2501df56edc5`.
- Sparse-checkout configurado para `docs/architecture/` antes da materialização.
- Os diretórios protegidos não foram materializados.
- O checkout original e outras worktrees não foram modificados.
- Commit local documental: criado após as validações finais; SHA completo registrado no relatório de entrega da fase.

## C. Origem e fidelidade das decisões

A fonte é o conteúdo de deliberação fornecido explicitamente pelo responsável nesta fase. A consolidação não inventa data individual, assinatura ou verificação criptográfica. As cinco decisões estão descritas no [adendo](./editorial-generations-phase-2-1a-12b8-learning-policy-addendum.md), incluindo os limites e itens ainda pendentes.

ADR-004 continua `PRINCIPLES_APPROVED_POLICY_PENDING`; nenhum prazo ou regra de GC foi inventado. ADR-008 continua `BLOCKED_BY_EVIDENCE`. As decisões da B.7, os oito ADRs originais (`Proposed`) e a matriz original (`PENDING_APPROVAL`) não foram alterados.

## D.–H. Decisões consolidadas

- **Continuidade de sessões:** sessão e tentativa seguem a geração original enquanto válida e segura; nova sessão usa a geração ativa. Sem TTL universal ou continuidade obrigatória após revogação.
- **Expiração/retomada:** progresso persistido é recuperado pelo servidor; retry não duplica automaticamente tentativas; resultados não desaparecem silenciosamente. Prazos e estados de expiração continuam pendentes.
- **Retirada emergencial:** bloquear novas sessões em problema grave; interromper as existentes seletivamente; manter auditoria, histórico e recuperação. Não equivale a exclusão física.
- **Correção de avaliação:** preservar original e registrar correção/reavaliação; comunicar o aluno; não sobrescrever nota silenciosamente. Algoritmo e efeitos em progresso/certificação seguem pendentes.
- **Certificados/conquistas:** correção favorável pode conceder reconhecimento; desfavorável não revoga automaticamente; revisão excepcional é fundamentada, auditável e comunicada. Processo, autoridade e retenção seguem pendentes.

## I. Gates

A [matriz de dependências e gates](./editorial-generations-phase-2-1a-12b8-policy-dependencies-and-gates.md) relaciona as deliberações principalmente a G6 (leitores/sessões), G7 (compatibilidade) e G9 (retenção), e a G4/G5/G10 ou G1–G3 quando o futuro escopo tocar segurança, publicação, operação, escritores ou snapshots. Os estados de B.7 permanecem: G1 `PARTIAL`, G2 `NOT_VERIFIED`, G3 `NOT_VERIFIED`, G4 `PARTIAL`, G5 `NOT_VERIFIED`, G6 `PARTIAL`, G7 `PARTIAL`, G8 `NOT_VERIFIED`, G9 `BLOCKED`, G10 `BLOCKED`. Nenhum gate foi promovido por aprovação humana ou documentação.

## J. Alterações documentais e verificações

Foram criados somente três novos arquivos Markdown em `docs/architecture/`. Nenhum ADR original, matriz histórica, documento B.7, arquivo funcional, dado ou infraestrutura foi alterado. Foram verificados escopo, links relativos, estados preservados, pendências, ausência de política de retenção inventada e `git diff --check`. Não foram executados testes da aplicação, Docker, MongoDB, workflows nem consultas externas.

## K. Riscos e próximas ações

Permanecem pendentes políticas de expiração e retomada, gravidade/autoridade de retirada, correção de avaliações, consequências para competências e certificados, retenção/privacidade e compatibilidade legada. G9 permanece bloqueado até inventário e política de retenção aprovados; ADR-008/G10 dependem de evidência operacional sanitizada do administrador autorizado, conforme [pedido B.4B](./editorial-generations-phase-2-1a-12b4b-admin-evidence-request.md).

A menor próxima ação é deliberar apenas sobre as políticas ainda abertas que afetem o primeiro escopo de implementação e obter, por canal autorizado, as evidências pendentes do ADR-008. Trabalho de implementação isolada poderá ser proposto depois, mas exige autorização própria e gates pertinentes. Nenhuma dessas ações foi iniciada nesta fase.

## L. Operações e veredito

Não houve acesso a serviços externos, bancos ou infraestrutura, nem escrita remota. A worktree será deixada limpa após o commit local exclusivamente documental.

**Veredito: ADENDO DOCUMENTAL CONSOLIDADO — IMPLEMENTAÇÃO NÃO AUTORIZADA.**
