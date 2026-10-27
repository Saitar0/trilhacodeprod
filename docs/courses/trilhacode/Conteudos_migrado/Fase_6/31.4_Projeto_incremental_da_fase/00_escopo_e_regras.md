---
arquivo_id: "f6-31-4-00-escopo-e-regras-md"
parent_key: "31.4"
tipo_arquivo: "project_scope"
ordem: 0
itens_origem: ["Escopo e relação com o Trilho B", "Princípios de implementação"]
---

## Escopo e relação com o Trilho B
Continue no mesmo projeto escolhido em 3.5 e use a API construída na Fase 5 como contrato e backend. Implemente uma fatia central e limitada do produto, sem reconstruir todas as funcionalidades. Este projeto forma a base comum do Trilho A.

A unidade 31.5 é uma entrega separada: nela, a pessoa escolhe uma ideia do Trilho B e demonstra o problema técnico específico desse tipo. Não copie toda a implementação desta unidade como se ela fosse a entrega especializada de 31.5. Reaproveite o que for realmente comum, mas mantenha requisitos e evidências próprios para cada projeto.

Antes de implementar, identifique quem usa a fatia, qual ação principal realizará, quais endpoints existentes atendem ao fluxo e que comportamento deve ocorrer em sucesso e falha. Não crie uma API fictícia para declarar integração concluída. Mocks são úteis para reproduzir estados, mas a etapa de integração deve também alcançar a API de teste da Fase 5.

## Princípios de implementação
- Use React com TypeScript e mantenha uma fronteira HTTP identificável entre interface e API.
- Tipos descrevem o contrato, mas não validam automaticamente respostas em runtime; trate respostas externas conforme o nível de validação adotado no curso.
- Mantenha estado de interface local separado do cache de dados remotos e evite cópias concorrentes sem sincronização.
- Exiba carregamento, erro, vazio e sucesso conforme o contrato da API; ofereça retry apenas quando a operação puder ser repetida com segurança.
- Preserve teclado, foco, labels e mensagens compreensíveis durante os fluxos principais.
- Use configuração de ambiente de exemplo sem credenciais reais ou valores secretos no bundle cliente.
- Registre comandos, condições de execução e limites de cada evidência para que outra pessoa consiga reproduzir a entrega.

