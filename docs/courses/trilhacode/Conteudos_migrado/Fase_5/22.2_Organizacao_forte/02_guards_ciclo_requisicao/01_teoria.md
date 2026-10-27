---
arquivo_id: "f5-22-2-02-guards-ciclo-requisicao-01-teoria"
parent_key: "22.2"
tipo_arquivo: "theory"
assunto: "02_guards_ciclo_requisicao"
ordem: 2
itens_origem: ["Microtópico 3 — Guards e posição no ciclo da requisição"]
---

## Microtópico 3 — Guards e posição no ciclo da requisição
Guard decide se a requisição pode prosseguir para o handler. Ele tem ExecutionContext para consultar handler e controller, o que permite usar metadados de rota. É adequado para autenticação e decisões de acesso associadas ao endpoint, como exigir um papel ou permissão geral. Um padrão comum usa decorator para declarar metadados e Reflector para lê-los no guard.

A sequência geral do Nest é middleware, guards, interceptors, pipes, controller e provider. Logo, guards executam antes dos pipes. Evite basear uma decisão de segurança no corpo da requisição como se já tivesse passado pela validação. Autenticação identifica a pessoa; autorização compara identidade e contexto com a política; validação verifica a forma dos dados. São decisões relacionadas, porém distintas.

Configure rotas públicas e protegidas de modo explícito e entenda a ordem entre guards global, de controller e de rota. Um guard de papel pode bloquear uma rota administrativa, mas a ausência de metadados precisa ter comportamento deliberado, não permitir tudo acidentalmente.

**Exemplo:** AuthenticationGuard valida a credencial e estabelece contexto de usuário; RolesGuard consulta metadados do handler e exige papel de operação. A alteração de um pedido específico ainda precisa verificar se aquela pessoa pode alterar aquele objeto.

**Erro comum:** colocar toda autorização dentro de um guard genérico ou deixar rota sem decorator passar por acidente.

**Checagem:** o guard usa contexto confiável e decide sobre endpoint/papel antes dos pipes; como o caso de uso confirma acesso ao objeto específico?

