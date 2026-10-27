---
arquivo_id: "f5-22-1-02-controller-provider-e-di-runtime-01-teoria"
parent_key: "22.1"
tipo_arquivo: "theory"
assunto: "02_controller_provider_e_di_runtime"
ordem: 2
itens_origem: ["Microtópico 2 — Controller adapta HTTP; provider executa colaboração", "Microtópico 3 — Injeção e tokens em tempo de execução"]
---

## Microtópico 2 — Controller adapta HTTP; provider executa colaboração
Controller pertence à fronteira HTTP: recebe parâmetros, corpo e contexto da requisição, chama um provider e transforma o resultado em resposta. Deve permanecer fino o suficiente para que regras e integrações possam ser entendidas e exercitadas sem depender do ciclo completo de HTTP.

Provider é qualquer dependência que o container Nest pode fornecer: serviço de aplicação, repositório, adaptador, configuração ou fábrica. Um serviço pode coordenar regra e colaboradores; um repositório/adaptador pode encapsular persistência quando essa fronteira for útil. O decorator Injectable marca classes que participam desse mecanismo, mas a função do componente vem do contrato e do uso, não do nome Service.

**Exemplo:** o controller recebe POST de criação e extrai o DTO; OrdersService verifica a operação e coordena gravação; o provider de persistência executa o armazenamento. A forma do DTO e a autorização por rota são tratadas mais profundamente em 22.2.

**Erro comum:** colocar regra de negócio em controller porque ele já recebe todos os dados, ou criar um service que apenas renomeia cada método do controller sem oferecer uma responsabilidade clara.

**Checagem:** se a mesma regra precisar ser usada por um job ou outro transporte, ela está presa ao objeto de requisição HTTP?

## Microtópico 3 — Injeção e tokens em tempo de execução
O container injeta dependências registradas como providers. Uma classe concreta pode servir como token de DI; uma interface TypeScript descreve um contrato no código, mas desaparece na execução e não pode, sozinha, ser usada pelo Nest para localizar um provider. Para injetar uma implementação por interface, registre um token estável — como símbolo ou string constante — e associe esse token a uma classe, valor ou factory.

Use token explícito quando a dependência precisa variar, representar uma interface ou ser fornecida por configuração. Para dependências diretas e estáveis, a injeção pela classe pode ser suficiente. A criação de conexão/configuração pertence ao ponto de composição da aplicação ou ao módulo apropriado, não deve ficar escondida dentro da regra que usa o recurso.

**Exemplo:** um OrdersService injeta o token ORDERS_REPOSITORY, associado pela configuração do módulo a uma implementação PostgreSQL. O contrato TypeScript descreve operações disponíveis, enquanto o token identifica o provider real no runtime.

**Erro comum:** declarar um parâmetro com tipo de interface e esperar que o runtime a descubra. Outra armadilha é criar provider em vários módulos consumidores, o que pode gerar instâncias independentes em vez de compartilhar a registrada pela feature.

**Checagem:** qual token real o container resolve e em que módulo a implementação é associada a ele?

