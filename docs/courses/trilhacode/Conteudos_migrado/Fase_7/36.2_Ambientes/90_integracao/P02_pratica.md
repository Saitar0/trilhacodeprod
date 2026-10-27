---
arquivo_id: "f7-36-2-90-integracao-p02-pratica-md"
parent_key: "36.2"
tipo_arquivo: "practice"
assuntos: ["01_ambientes_state_isolamento", "02_pipeline_identidade_gates"]
ordem: 2
itens_origem: ["P02"]
---

### Atividade 2 — Construa pipeline Terraform + deploy para staging

**Desafio:** integre a infraestrutura e aplicação da Fase 7 numa promoção auditável para staging.

**Passos:**
1. Organize CI para executar validações/testes antes de preparar plano Terraform; em pull request, gere plano revisável sem aplicar.
2. Configure role de OIDC de sandbox/staging com permissões mínimas e trust policy limitada ao workflow/repositório/branch/environment necessários.
3. Associe o job ao environment `staging`; aplique gates/branches permitidos e aprovação somente conforme recursos da conta/plano disponíveis.
4. Após aprovação, confirme que diretório/backend/workspace, conta e região correspondem ao plano de staging; aplique o plano revisado e implante o mesmo artefato de aplicação testado.
5. Execute health/smoke check e registre commit, identidade, plano, artefato, ambiente e resultado. Simule falha em check ou plano inseguro e confirme que a etapa seguinte não executa.
6. Documente a rota de promoção a prod, mas não a execute; liste mudanças de identidade, revisão e evidência exigidas para um ambiente real.

**Evidências:** workflow; trust policy sanitizada; plano/revisão; deployment history; logs de smoke check; registro de gate/falha; instruções sem secrets.

**Verificação:** um check falho impede aplicação/promoção; nenhuma credencial permanente está embutida; ambiente e identidade podem ser rastreados; plano aprovado não mudou antes do apply.

**Aceite:** pipeline bloqueia falhas e planos inesperados; staging usa identity/state próprios; artefato corresponde ao commit testado; resultado e limitações do ambiente são reproduzíveis.

