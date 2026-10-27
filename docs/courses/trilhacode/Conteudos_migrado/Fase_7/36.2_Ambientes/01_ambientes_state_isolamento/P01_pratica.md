---
arquivo_id: "f7-36-2-01-ambientes-state-isolamento-p01-pratica-md"
parent_key: "36.2"
tipo_arquivo: "practice"
assunto: "01_ambientes_state_isolamento"
ordem: 1
itens_origem: ["P01"]
---

### Atividade 1 — Modele ambientes e limites de state

**Desafio:** prepare uma estrutura para `dev`, `staging` e `prod`, mantendo dev/staging executáveis apenas em sandbox e deixando produção documentada sem aplicar.

**Passos:**
1. Defina propósito, responsável, dados permitidos, configuração, região/conta, identidade, recursos e critério de promoção para cada ambiente.
2. Escolha entre diretórios/backend separados, CLI workspaces ou HCP Terraform workspaces; justifique a opção com diferenças reais de credencial, acesso e state.
3. Reutilize módulos para estrutura comum; liste valores não sensíveis por ambiente e indique onde secrets/credenciais serão obtidos.
4. Faça o plano de dev e staging apontarem a states e recursos distintos; inclua checks para workspace, conta AWS, região e backend antes de qualquer apply.
5. Registre que um mesmo account de sandbox é um limite menor que contas isoladas e não use dados reais.

**Evidências:** árvore de diretórios/diagrama; matriz dos três ambientes; configuração de backend/identidade descrita; planos separados ou simulação sem apply; validações do alvo.

**Verificação:** pessoa revisora consegue determinar, antes de apply, qual conta, state, role, região e variáveis serão usados; prod não pode ser escolhido por padrão no laboratório.

**Aceite:** isolamento é declarado sem chamar tfvars de controle de acesso; dev/staging não compartilham state; acesso e dados têm escopo explícito; produção permanece fora de execução.

