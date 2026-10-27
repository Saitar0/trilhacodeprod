---
arquivo_id: "f7-36-2-01-ambientes-state-isolamento-01-teoria-md"
parent_key: "36.2"
tipo_arquivo: "theory"
assunto: "01_ambientes_state_isolamento"
ordem: 1
itens_origem: ["### Microtópico 1 — Defina o que muda e o que fica isolado", "### Microtópico 2 — Separe configuração, state e permissões Terraform"]
---

### Microtópico 1 — Defina o que muda e o que fica isolado

Um **ambiente** é uma instância da solução com finalidade, configuração, dados, identidade, rede, state e acesso definidos. `dev` serve para iteração rápida; `staging` valida uma versão e configurações relevantes antes de promoção; `prod` atende usuários reais e tem exigências de segurança/disponibilidade próprias. Os nomes variam entre equipes — o importante é declarar propósito, responsáveis, critérios de promoção e limites.

Use módulos para compartilhar estrutura comum e parâmetros para diferenças legítimas como tamanho, domínio, retenção e número de réplicas. Não transforme `environment = "prod"` ou outro tfvars em barreira de segurança: valores escolhem configuração, mas não revogam permissão de quem executa. Dados de teste em dev/staging devem ser sintéticos ou tratados para o uso permitido; secrets e credenciais devem ser independentes por ambiente. Evite copiar dados pessoais de produção para staging sem necessidade e controles apropriados.

Ambientes podem viver em contas AWS distintas. Contas separadas criam um limite administrativo e de faturamento mais claro; roles, policies e organizações governam acesso entre contas. Um laboratório simples pode usar uma conta autorizada com recursos isolados, mas registre que isso não oferece a mesma separação de conta. Não use produção neste projeto didático.

### Microtópico 2 — Separe configuração, state e permissões Terraform

Uma configuração Terraform usa entradas por ambiente (por exemplo `dev.tfvars` e `staging.tfvars`), mas cada ambiente precisa apontar deliberadamente ao state e à identidade corretos. State não deve ser compartilhado entre dev e staging por conveniência, nem o plano de um ambiente deve ser aplicado em outro. State contém dados sensíveis e seus acessos, retenção, criptografia, backup e locking precisam ser configurados conforme o backend.

Há duas coisas chamadas **workspace**:
- Workspace da **Terraform CLI**: estado distinto da mesma configuração no mesmo diretório/backend; comandos atuam no workspace selecionado. É útil para cópias parecidas e temporárias, mas compartilha configuração, backend e geralmente credenciais. Não oferece sozinho separação forte de acesso por ambiente.
- Workspace do **HCP Terraform**: unidade remota com configuração, variáveis, state, histórico e controles de execução/acesso próprios. Não é o mesmo conceito da CLI e continua operando dentro do limite de conta/provedor configurado.

Para ambientes com credenciais, ciclo de vida ou políticas diferentes, prefira configurações/diretórios e backends próprios, ou workspaces remotos configurados com controles próprios, conforme a plataforma. Exemplo de estrutura nativa:

```text
infra/
  modules/app-environment/
  env/dev/       # root module, backend e valores não sensíveis de dev
  env/staging/   # root module, backend e valores não sensíveis de staging
  env/prod/      # estrutura apenas documentada neste laboratório; não aplicar
```

Os diretórios reduzem o risco de operar no alvo errado, mas podem divergir se forem copiados manualmente; mantenha o módulo comum como fonte compartilhada e revise diferenças. Terragrunt pode coordenar muitas configurações/stacks e reduzir repetição em estruturas maiores, mas adiciona ferramenta, sintaxe e operação. Para `dev` e `staging` simples, comece com Terraform nativo; adote Terragrunt quando dependências e repetição reais justificarem seu custo.

