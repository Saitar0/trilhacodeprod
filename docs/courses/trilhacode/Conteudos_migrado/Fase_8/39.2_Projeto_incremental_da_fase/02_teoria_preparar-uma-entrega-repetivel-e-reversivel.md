---
arquivo_id: "f8-39-2-02-teoria-preparar-uma-entrega-repetivel-e-reversivel-md"
parent_key: "39.2"
tipo_arquivo: "theory"
ordem: 1
itens_origem: ["MT01"]
---


### Microtópico 1 — Preparar uma entrega repetível e reversível

Antes de alterar a aplicação, registre o estado inicial do projeto: versão/commit, ambiente, fluxo principal, dependências e como saber se o serviço está saudável. Confirme que dev/staging e produção não compartilham credenciais, variáveis, state ou recursos por engano. Na pipeline existente, localize os gates, o health check e as evidências de implantação; não adicione etapas duplicadas sem necessidade.

Para a infraestrutura, revise o plano antes de aplicar: os recursos a criar, alterar e destruir devem corresponder à mudança planejada. Separe aprovação e aplicação quando o fluxo de equipe exigir revisão. Não trate o Terraform como mecanismo universal de rollback: aplicar uma configuração antiga pode não reverter dados, migrations, mensagens já processadas, alterações externas ou recursos irreversíveis. Faça rollback de aplicação ou infraestrutura conforme o tipo de mudança, pré-condições, estado e plano ensaiado.

**Entrega 1 — Baseline e deploy controlado.** Descreva o fluxo, o estado inicial, a configuração por ambiente e o caminho de deploy/rollback. Execute ou simule os gates e faça uma implantação em teste, com evidência do commit, resultado de pipeline, health check e plano revisado. Documente como evitar segredos no repositório e nos artefatos.

**Critérios de aceite:** ambientes e configuração estão identificados; pipeline executa o fluxo previsto; plano não contém mudanças surpresa; health check comprova resposta; rollback tem pré-condições e não depende de presumir que dados persistentes podem ser desfeitos.

