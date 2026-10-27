---
arquivo_id: "f5-18-1-02-fluxo-de-requisicao-e-camadas-01-teoria"
parent_key: "18.1"
tipo_arquivo: "theory"
assunto: "02_fluxo_de_requisicao_e_camadas"
ordem: 2
itens_origem: ["3. Fluxo de uma requisição e responsabilidades"]
---

### 3. Fluxo de uma requisição e responsabilidades
No Express, o método e o caminho selecionam uma rota; middlewares e handlers executam em cadeia. Middleware pode preparar contexto compartilhado ou tratar preocupação transversal, como identificador de requisição, autenticação e parsing do corpo. Controller interpreta a entrada HTTP, chama um serviço e monta a resposta. Serviço aplica regras de negócio e coordena operações sem depender de detalhes da resposta HTTP. Repositório ou camada de acesso a dados pode encapsular persistência quando isso simplifica o desenho.

A ordem da cadeia importa: parsing e contexto necessários devem ocorrer antes da rota; autenticação e autorização devem proteger operações restritas; middleware de tratamento de erro deve ficar depois das rotas. Cada fluxo deve responder ou delegar de forma definida, sem enviar duas respostas nem deixar a requisição pendurada. O modo de encaminhar rejeições assíncronas varia por versão do Express: confira a versão instalada e a documentação correspondente. [Express — routing](https://expressjs.com/en/guide/routing.html) e [Express 5 — error handling](https://expressjs.com/en/5x/guide/error-handling/).

