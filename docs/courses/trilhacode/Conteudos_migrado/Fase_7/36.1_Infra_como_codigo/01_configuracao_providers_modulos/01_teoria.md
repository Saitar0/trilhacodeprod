---
arquivo_id: "f7-36-1-01-configuracao-providers-modulos-01-teoria-md"
parent_key: "36.1"
tipo_arquivo: "theory"
assunto: "01_configuracao_providers_modulos"
ordem: 1
itens_origem: ["### Microtópico 1 — Configuração declarativa e ciclo de trabalho", "### Microtópico 2 — Providers, módulos e entradas/saídas"]
---

### Microtópico 1 — Configuração declarativa e ciclo de trabalho

Terraform descreve o estado desejado da infraestrutura em HCL. Recursos representam objetos gerenciados; expressões, variáveis e módulos organizam a configuração. O Terraform compara configuração, state e leituras do provider para propor ações. Ele não é um script que simplesmente executa linhas na ordem escrita: referências entre recursos formam dependências, e o grafo resultante pode permitir operações paralelas.

O diretório de trabalho forma o **root module**; módulos chamados por blocos `module` são child modules. Um ciclo comum é `init` (inicializa backend e instala providers/módulos), `fmt` (formata), `validate` (valida sintaxe e consistência local), `plan` (mostra mudanças propostas) e `apply` (executa mudanças). `validate` não comprova que a conta tem permissões, que quotas permitem a criação ou que a API da nuvem aceitará cada alteração. O plano pode falhar na aplicação por mudanças externas, permissões, limites ou condições de corrida.

Revisar `plan` é uma barreira operacional. Identifique recursos a criar, atualizar, substituir e destruir, valores relevantes e dependências; substituição pode remover e recriar recurso, e destruição pode apagar dados. Não aplique em conta de produção para aprender. Use sandbox isolado e só execute depois de entender escopo, custo e plano de recuperação.

### Microtópico 2 — Providers, módulos e entradas/saídas

**Provider** é o plugin que conecta Terraform à API de uma plataforma como AWS. Declare fonte e restrição de versão em `required_providers`, configure região/autenticação sem inserir credenciais fixas e mantenha `.terraform.lock.hcl` no controle de versão. A restrição declara versões compatíveis; o lockfile registra a seleção concreta e checksums para instalações consistentes. Atualize providers deliberadamente, revise changelog e gere novo plano depois da atualização.

**Módulos** agrupam recursos relacionados e expõem uma interface. Variáveis são entradas; outputs são valores publicados para o módulo chamador ou para a saída da execução. Defina tipo, descrição, validação útil e defaults seguros. Módulo reutilizável deve esconder detalhes internos sem esconder riscos de recursos destrutivos, permissões ou custo. Evite criar abstrações profundas antes de haver uma repetição ou limite real de responsabilidade.

Não confunda `.terraform.lock.hcl` com state: o primeiro ajuda a selecionar providers consistentes; state mapeia endereços Terraform a recursos remotos e mantém atributos/metadados da infraestrutura gerenciada. Modules também têm origem/versão que deve ser controlada conforme a fonte; não presuma que o provider lockfile fixa automaticamente toda dependência de módulo.

