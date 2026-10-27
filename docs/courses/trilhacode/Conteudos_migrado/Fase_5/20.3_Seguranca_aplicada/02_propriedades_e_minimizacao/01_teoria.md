---
arquivo_id: "f5-20-3-02-propriedades-e-minimizacao-01-teoria"
parent_key: "20.3"
tipo_arquivo: "theory"
assunto: "02_propriedades_e_minimizacao"
ordem: 2
itens_origem: ["Microtópico 2 — Proteja propriedades e minimize respostas"]
---

## Microtópico 2 — Proteja propriedades e minimize respostas
A autorização também pode ser específica para campos. Uma pessoa pode ter permissão para ver um perfil, mas não campos internos; pode alterar nome, mas não papel ou tenant. Não serializar indiscriminadamente a entidade inteira: construa respostas com campos permitidos para aquele caso e aceite mudanças por lista de propriedades editáveis.

Minimize dados durante todo o ciclo: colete e mantenha apenas o necessário para a finalidade definida; restrinja quem acessa; evite dados pessoais em respostas, eventos e logs sem necessidade. Não confie em campos enviados pelo cliente como userId, tenantId, papel ou valor calculado pelo servidor. Derive esses valores de contexto autenticado e de regras confiáveis.

**Exemplo:** uma API retorna nome público e status do pedido; omite notas internas e dados de pagamento. Em uma atualização de perfil, aceita nome e imagem, mas ignora ou rejeita campos administrativos não editáveis pelo titular.

**Erro comum:** remover dados sensíveis só da tela e continuar devolvendo-os pela API, ou proteger leitura mas aceitar alteração de propriedades sensíveis por mass assignment.

**Checagem:** a resposta e os campos aceitos contêm apenas o necessário e permitido para esta identidade, ação e recurso?

