---
arquivo_id: "f5-24-2-02-integracao-rota-e-persistencia-01-teoria"
parent_key: "24.2"
tipo_arquivo: "theory"
assunto: "02_integracao_rota_e_persistencia"
ordem: 2
itens_origem: ["Microtópico 3 — Exercite a rota pela aplicação Nest de teste", "Microtópico 4 — Prove a persistência com o banco real"]
---

## Microtópico 3 — Exercite a rota pela aplicação Nest de teste

Um teste HTTP pode criar a aplicação com o módulo de teste, inicializá-la, enviar uma requisição pelo servidor e verificar resposta. Isso integra a rota com os componentes que foram deixados reais: por exemplo, controller, ValidationPipe global, guards e filtro de exceções. Um cliente como Supertest consegue chamar o servidor de teste sem exigir um deploy.

Verifique a interface pública: status, campos do corpo, cabeçalhos relevantes e, se a operação promete persistência nesse cenário, estado consultável. Envie também uma entrada inválida e observe status/erro e ausência de gravação. Para autorização, cubra ao menos acesso permitido e negado se fizer parte do fluxo.

Se substituir o provider do banco neste teste, declare que a resposta HTTP foi exercitada com persistência simulada. Se usar o banco real, explique que a suíte cruza também a fronteira do banco. Não conte o mesmo teste como prova de ambos sem mostrar o que efetivamente executou.

## Microtópico 4 — Prove a persistência com o banco real

Constraints são garantias da base de dados e precisam ser verificadas com a tecnologia que as implementa. Para uma constraint de unicidade, aplique as migrations ao banco de teste, crie um registro e tente criar a duplicata pelo caminho escolhido. Confirme que a segunda operação falha e que a API converte o erro conforme o contrato, sem expor detalhes internos sensíveis.

Uma tabela vazia por teste não é suficiente se a migration ou constraint não foi aplicada. A configuração do teste deve criar uma instância descartável ou um banco/schema exclusivo, executar as migrations e usar registros próprios. Ao concluir, descarte o ambiente ou remova apenas o estado pertencente ao teste.

Não use credenciais de produção, banco compartilhado de desenvolvimento ou comando de limpeza amplo. Se vários workers executarem em paralelo, cada worker precisa de isolamento que impeça colisões. Uma transação aberta no processo de teste não desfaz necessariamente gravações feitas pela aplicação em outra conexão; rollback só isola quando a aplicação participa da mesma transação/contexto. Escolha e confirme uma estratégia compatível com a arquitetura real.

