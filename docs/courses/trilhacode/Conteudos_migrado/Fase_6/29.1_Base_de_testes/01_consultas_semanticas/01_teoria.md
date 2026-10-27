---
arquivo_id: "f6-29-1-01-consultas-semanticas-01-teoria-md"
parent_key: "29.1"
tipo_arquivo: "theory"
assunto: "01_consultas_semanticas"
ordem: 1
itens_origem: ["## Microtópico 1 — Teste o contrato que a pessoa usa"]
---

## Microtópico 1 — Teste o contrato que a pessoa usa
Um teste de componente deve responder a uma pergunta sobre o comportamento: o formulário informa um campo obrigatório? O botão envia os dados válidos? A lista mostra erro quando a consulta falha? O teste renderiza a interface, interage com ela e verifica o resultado percebido. Ele não precisa conhecer o nome de um `useState`, chamar um handler privado ou depender de uma classe CSS que só organiza o visual.

Testing Library orienta a escrever testes que se aproximem de como o software é usado. Consultas por papel acessível e nome, label ou texto costumam exercitar a semântica da interface. Isso também torna problemas de acessibilidade mais visíveis: se não é possível localizar um botão pelo papel e nome que deveria ter, pode haver uma falha real no markup.

Não transforme cada detalhe de implementação em contrato. Um snapshot enorme pode mudar por alterações irrelevantes e ainda deixar passar um comportamento errado. Prefira assertions específicas: mensagem visível, ação disponível, resultado renderizado ou ausência de um conteúdo após a interação. Escolha cenários de acordo com risco e regra de negócio, não apenas para aumentar a quantidade de testes.

