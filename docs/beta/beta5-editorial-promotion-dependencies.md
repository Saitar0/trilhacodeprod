# Beta 5 — dependências para futura promoção editorial

Esta fase não implementa promoção. Staging validado só poderá tornar-se conteúdo editorial após a fronteira futura:

`STAGING VALIDADO → AUTORIZAÇÃO EDITORIAL → CAS/FENCING → PROMOÇÃO CONTROLADA → AUDITORIA → PUBLICAÇÃO FUTURA`.

Pré-condições herdadas de C8–C16:

1. Aprovação e validação no IAM real da fonte única de grants, escopo administrativo, delegação e revogação.
2. Ordenação demonstrada de usuário, papel, sessão, permissão versionada e grant até o commit; uma capability inicial não basta.
3. Contrato de revisão/fence, idempotência e recibo integrado à autoridade C8/C10, sem autoridade paralela.
4. Writers legados e identidades MongoDB de escrita direta contidos; C16 demonstrou bypass por credencial direta.
5. Auditoria, histórico e revisão consistentes na mesma fronteira da mutação.
6. Tratamento de publicação, snapshots, restauração, importação, reordenação e exclusão que preserve gerações, tentativas e progresso do aluno.
7. Decisões de ACL, visibilidade de projeto, explicações, rubricas, retenção, HMAC e logs.
8. Contrato HTTP e projeções de leitura aprovados, incluindo quiz versionado, exercícios manuais, conclusão e relações.
9. Testes unitários, persistentes, concorrentes, HTTP e E2E adequados, plano de rollback e evidência operacional ADR-008 autorizada.
10. Autorização específica posterior para implementação/integracão e autorização própria para implantação.

O serviço Beta 5 não contém método de promoção, coleção operacional como destino, estado `PUBLISHED` ou ligação com readers/startup. A ausência desses componentes é intencional. Rascunho, conteúdo reservado, progresso e tentativas permanecem fora de qualquer mutação.
