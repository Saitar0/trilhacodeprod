---
arquivo_id: "f5-22-2-03-autorizacao-contextual-respostas-01-teoria"
parent_key: "22.2"
tipo_arquivo: "theory"
assunto: "03_autorizacao_contextual_respostas"
ordem: 3
itens_origem: ["Microtópico 4 — Autorização contextual e formato de saída"]
---

## Microtópico 4 — Autorização contextual e formato de saída
Guard baseado em metadados atende bem a decisões amplas de rota. Uma permissão por recurso pode depender de carregar o registro e conhecer dono, tenant, estado ou compartilhamento; faça essa verificação junto à operação de aplicação/domínio que tem o contexto. Uma pessoa pode passar no guard por ter papel válido e ainda não poder acessar aquele pedido.

Resposta também atravessa uma fronteira. DTO de entrada não define formato de saída. Projete propriedades de saída explicitamente ou use o mecanismo de serialização escolhido pelo projeto: Nest documenta ClassSerializerInterceptor para classes e StandardSchemaSerializerInterceptor para schemas compatíveis. Confirme qual forma de objeto o mecanismo espera. Não devolva entidade completa sem revisar campos sensíveis.

**Exemplo:** uma rota exige usuário autenticado e papel de suporte; o serviço verifica tenant antes de abrir chamado e a resposta serializada contém apenas identificador, estado e resumo, não notas privadas.

**Erro comum:** proteger rota e validar o corpo, mas retornar todos os campos do banco ou aceitar que um usuário de um tenant use o ID de outro.

**Checagem:** o usuário pode executar esta classe de ação? Pode fazê-la neste objeto específico? A resposta contém somente propriedades autorizadas?

