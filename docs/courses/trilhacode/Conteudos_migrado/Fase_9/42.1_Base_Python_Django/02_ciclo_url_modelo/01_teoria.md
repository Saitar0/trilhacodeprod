---
arquivo_id: "f9-42-1-02-ciclo-url-modelo-01-teoria"
parent_key: "42.1"
tipo_arquivo: "theory"
assunto: "02_ciclo_url_modelo"
ordem: 2
itens_origem: ["### 2. Do URL ao modelo: ciclo Django"]
---


### 2. Do URL ao modelo: ciclo Django
Uma requisição entra pelo servidor e passa pelo middleware configurado. O resolvedor compara o caminho com `urlpatterns` e chama uma view. A view interpreta a solicitação, pode consultar ou alterar dados pelo ORM e devolve uma resposta. Modelos definem campos e comportamento dos dados; migrations registram mudanças de esquema que podem ser aplicadas ao banco.

Mapa aproximado com conceitos já vistos em Node:

| Django | Papel aproximado | Analogia possível em Node |
|---|---|---|
| URLconf | associa caminho à execução | router |
| middleware | lógica ao redor de várias requisições | middleware |
| view | coordena requisição e resposta | controller/handler |
| model e ORM | dados e consultas | model/repositório/ORM |
| migration | histórico declarativo do schema | migration de ORM |
| settings e apps | configuração e organização | configuração e módulos |

As equivalências são guias de leitura, não correspondências exatas. Convenções do framework participam da resolução e execução; siga o caminho concreto no projeto em vez de presumir que um nome tem a mesma função em toda stack.

**Checagem:** onde procurar a rota e onde procurar a estrutura persistida? Em `urls.py`/URLconf para o mapeamento e em `models.py` e migrations para dados e evolução do esquema.

