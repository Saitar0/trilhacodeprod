---
arquivo_id: "f7-36-2-02-pipeline-identidade-gates-01-teoria-md"
parent_key: "36.2"
tipo_arquivo: "theory"
assunto: "02_pipeline_identidade_gates"
ordem: 2
itens_origem: ["### Microtópico 3 — Promova mudanças com identidade e gates"]
---

### Microtópico 3 — Promova mudanças com identidade e gates

Um pipeline de deploy separa validação, plano, aprovação, aplicação e verificação. Execute fmt/validate/plan e checks da aplicação antes de deploy; confira exatamente a conta AWS, região, backend/state, diretório e alvo. Mostre o plano ao revisor e aplique o plano aprovado no mesmo ambiente. State ou configuração alterados entre revisão e apply exigem novo plano. O pipeline precisa falhar fechado se o target estiver ambíguo, o plano tiver destroy/replacement não esperado ou os checks falharem.

Use GitHub Environments (ou equivalente) para registrar `staging`, restringir branches e proteger secrets/execução conforme plano disponível. Aprovação, quando configurada e suportada, libera o job; ela não confirma sozinha que o plano é seguro. Em seguida, implante o artefato de aplicação já construído/testado, em vez de recompilar uma versão diferente, e execute health/smoke check. Este projeto entrega staging; promoção para produção fica documentada como caminho sujeito às políticas reais do serviço, sem executar publicação produtiva.

Para autenticação AWS, OIDC pode trocar uma identidade de workflow por credenciais temporárias. Exige `id-token: write` no job que solicita token e uma trust policy na AWS que restrinja sujeito/audience e as condições necessárias ao repositório, branch ou environment. Conceda à role de `dev` só acesso ao state e recursos daquele ambiente, e à role de `staging` apenas operações requeridas. Não coloque access keys da AWS nos secrets permanentes do workflow sem necessidade, e nunca reutilize role de produção no exercício.

O caminho de promoção deve poder responder: qual commit/artifact, qual configuração e plano, qual identidade executou, quem aprovou, em qual ambiente e qual smoke check confirmou saúde? Armazene logs e outputs sem credenciais ou payload sensível. Rollback da aplicação para artefato anterior é diferente de reverter Terraform: alteração de infraestrutura pode destruir/substituir recursos ou dados, então requer plano e análise própria.

