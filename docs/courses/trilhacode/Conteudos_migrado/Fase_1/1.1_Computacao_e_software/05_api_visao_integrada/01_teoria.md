---
arquivo_id: "f1-1-1-05-api-visao-integrada-01-teoria"
parent_key: "1.1"
tipo_arquivo: "theory"
assunto: "05_api_visao_integrada"
ordem: 5
itens_origem: ["APIs: uma interface de comunicação", "Uma visão integrada"]
---

### APIs: uma interface de comunicação

Uma **API** (Application Programming Interface) é uma interface definida para que um software use capacidades ou dados oferecidos por outro. Ela especifica como fazer solicitações e como interpretar respostas. APIs não são exclusivas da web: existem em bibliotecas, sistemas operacionais e serviços.

Uma API web pode receber requisições HTTP. Por exemplo, a interface de uma loja pode pedir ao backend uma lista de produtos. O backend aplica as regras e talvez consulte o banco de dados; a API devolve os dados em um formato acordado, e o frontend os apresenta. A API é o contrato de comunicação entre partes do software; não é, por si só, o banco de dados nem a tela.

### Uma visão integrada

Ao clicar em “Ver meus pedidos”, o frontend pode enviar uma requisição à API. O backend identifica a operação, verifica as permissões e consulta os dados necessários. O banco de dados devolve os registros ao backend. O backend monta uma resposta HTTP, e o frontend atualiza a interface.

Nem todo clique precisa chegar ao servidor. Abrir um menu, por exemplo, pode ser resolvido inteiramente pelo frontend. A decisão depende do que a aplicação precisa fazer e de quais dados ou regras estão envolvidos.

