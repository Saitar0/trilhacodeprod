---
arquivo_id: "f7-32-2-02-ambientes-autorizacao-promocao-01-teoria-md"
parent_key: "32.2"
tipo_arquivo: "theory"
assunto: "02_ambientes_autorizacao_promocao"
ordem: 2
itens_origem: ["### Microtópico 2 — Ambientes, autorização e promoção"]
---

### Microtópico 2 — Ambientes, autorização e promoção

**Staging** deve se aproximar de produção nos aspectos que importam para o comportamento — runtime, configuração relevante, integração e processo de deploy — mas usa recursos, contas, credenciais e dados isolados. Se staging não reproduz uma dependência essencial, registre essa diferença porque a aprovação não cobre o cenário ausente.

Um GitHub Environment representa um alvo como `staging` ou `production`. Um job que referencia o ambiente pode usar suas regras de proteção e secrets; o histórico de deployments ajuda a rastrear o que foi publicado. Regras podem restringir branches/tags e exigir aprovação. A disponibilidade de revisores obrigatórios e outras proteções depende do plano GitHub e da visibilidade/configuração do repositório; confirme no repositório do exercício antes de afirmar que a aprovação é aplicada.

Uma aprovação controla a passagem do job, mas não prova que o artefato é seguro ou saudável. Restringir branches de deploy, usar permissões mínimas, aprovar mudanças com contexto e manter secrets no ambiente adequado são controles complementares. Se o provedor permitir OIDC, configure confiança com condições específicas para repositório, branch ou ambiente; `id-token: write` permite solicitar o token OIDC, mas a policy no provedor é que limita quais identidades recebem credenciais temporárias.

Serializar deployments para o mesmo ambiente evita concorrência sobre recursos compartilhados. Para um job de deploy, avalie o comportamento de cancelamento: cancelar um deploy já ativo pode deixar a aplicação num estado intermediário. Use uma política deliberada e documente como uma nova versão aguarda ou substitui uma implantação pendente.

