---
arquivo_id: "f7-36-2-01-resumo-md"
parent_key: "36.2"
tipo_arquivo: "resumo"
ordem: 0
itens_origem: ["Resumo"]
---

## Resumo
- Ambiente combina propósito, parâmetros, dados, identidade, rede, state e política; nome ou tfvars não é fronteira de segurança.
- Contas separadas dão limite mais claro; laboratórios numa conta compartilham riscos e devem declarar esse limite.
- CLI workspaces e HCP Terraform workspaces são conceitos diferentes; só state separado não garante isolamento de identidade.
- Pipeline valida, planeja, aprova, aplica no alvo escolhido e verifica; artefato de app deve ser rastreável.
- OIDC exige trust policy restrita; roles e state devem ser isolados por ambiente conforme a plataforma.
- Destroy e rollback têm efeitos distintos; preserve dados/state necessários e confirme recursos/custos restantes.

