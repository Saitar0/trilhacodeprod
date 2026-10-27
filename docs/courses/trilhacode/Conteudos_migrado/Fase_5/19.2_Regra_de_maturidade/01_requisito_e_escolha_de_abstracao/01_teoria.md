---
arquivo_id: "f5-19-2-01-requisito-e-escolha-de-abstracao-01-teoria"
parent_key: "19.2"
tipo_arquivo: "theory"
assunto: "01_requisito_e_escolha_de_abstracao"
ordem: 1
itens_origem: ["Microtópico 1 — Comece pela regra e pela consulta", "Microtópico 2 — Escolha a menor abstração que mantém clareza"]
---

## Microtópico 1 — Comece pela regra e pela consulta
A decisão não começa pela preferência por ferramenta. Começa pelo comportamento que a aplicação precisa garantir: quais dados entram e saem, quais invariantes devem permanecer verdadeiras, qual volume é esperado e quais condições de concorrência existem. Identifique também se a operação é CRUD comum, leitura relacional, relatório, atualização em lote ou fluxo transacional.

**Exemplo:** cadastrar um usuário com campos e relações comuns pode caber naturalmente na API do ORM. Um relatório com agregações, agrupamentos e recursos específicos do banco pode pedir um construtor de consultas ou SQL explícito. O nome da operação, sozinho, não determina a escolha.

**Erro comum:** adotar uma regra global como “todo acesso passa pelo ORM” ou “consulta séria sempre é SQL”. As duas regras ignoram o problema concreto e podem esconder custo ou duplicar complexidade.

**Checagem:** antes de escolher uma API, descreva o resultado, as invariantes e o volume esperado da operação.

## Microtópico 2 — Escolha a menor abstração que mantém clareza
Use a API do ORM quando ela expressa a operação de modo legível, preserva tipagem útil e deixa as relações e limites da transação claros. Um query builder pode ser um meio-termo quando a consulta exige composição, joins ou condições dinâmicas, mas ainda se beneficia da integração da ferramenta. SQL explícito é adequado quando a API não expressa bem a consulta, quando um recurso específico do banco é necessário ou quando evidência medida justifica controle mais direto.

A menor abstração não é necessariamente a menor quantidade de linhas. Considere quem vai revisar e manter o código, se os tipos representam o resultado corretamente, se a consulta continua parametrizada e se a lógica de domínio permanece entendível. Evite manter duas implementações equivalentes sem motivo, pois elas podem divergir.

**Exemplo:** um endpoint CRUD permanece na API do ORM; uma consulta de relatório específica pode ficar em SQL versionado e parametrizado, com nome e contrato claros no repositório de acesso a dados.

**Erro comum:** trocar uma consulta apenas porque “SQL parece mais rápido”. A linguagem usada não garante plano, índice, seletividade ou menor custo.

**Checagem:** a escolha reduz surpresa e deixa claro como validar o resultado? Se não, a fronteira ainda precisa de justificativa ou simplificação.

