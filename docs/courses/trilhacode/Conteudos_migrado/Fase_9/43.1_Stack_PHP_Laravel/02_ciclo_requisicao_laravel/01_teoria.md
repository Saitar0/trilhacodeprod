---
arquivo_id: "f9-43-1-02-ciclo-requisicao-laravel-01-teoria"
parent_key: "43.1"
tipo_arquivo: "theory"
assunto: "02_ciclo_requisicao_laravel"
ordem: 2
itens_origem: ["### 2. Ciclo de requisição no Laravel"]
---


### 2. Ciclo de requisição no Laravel
Uma aplicação Laravel usa convenções para encaminhar e processar requisições. Um percurso comum é:

1. `routes/web.php` ou rotas de API declara método e caminho;
2. middleware pode aplicar sessão, autenticação, CSRF ou outros filtros;
3. rota chama closure ou controller;
4. request/Form Request valida entrada e pode executar verificação de autorização;
5. controller ou camada de domínio aplica regra de negócio;
6. Eloquent consulta/persiste modelos e migrations versionam mudanças no schema;
7. policy/gate verifica autorização para ação ou recurso;
8. framework constrói resposta HTTP/JSON.

O mapa com Node é aproximado: rotas/controllers têm papéis reconhecíveis; middleware envolve o ciclo; service container resolve dependências; migrations versionam schema; Eloquent é ORM; filas delegam trabalho a workers. Names e APIs não correspondem um a um.

Eloquent facilita consultas e relações, mas SQL continua importante: use índices adequados, transações quando necessárias, limite dados retornados e procure padrões N+1 (uma consulta para a lista e consultas adicionais repetidas para relações). O model não elimina necessidade de compreender as consultas executadas.

Autenticação responde quem fez a chamada; autorização responde se pode realizar essa ação sobre aquele recurso. Middleware `auth` protege rotas para usuários identificados, enquanto policies organizam decisões por modelo/ação. O fato de existir login não prova que o usuário só consulte ou altere registros próprios; confira policy, binding e consultas com escopo apropriado.

