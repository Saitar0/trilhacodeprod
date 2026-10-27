---
arquivo_id: "f6-31-1-03-route-handlers-endpoints-01-teoria-md"
parent_key: "31.1"
tipo_arquivo: "theory"
assunto: "03_route_handlers_endpoints"
ordem: 3
itens_origem: ["## Microtópico 4 — Trate Route Handlers como endpoints públicos"]
---

## Microtópico 4 — Trate Route Handlers como endpoints públicos
Um arquivo `route.ts` no App Router implementa métodos HTTP com as APIs `Request` e `Response`, como `GET`, `POST`, `PATCH` e `DELETE`. Route Handlers não são componentes de página e não participam dos layouts nem da navegação visual. Uma URL pode ser criada em qualquer segmento adequado dentro de `app`, respeitando o conflito entre `page` e `route` no mesmo nível.

Pense nesses handlers como endpoints de API expostos a requisições externas. Valide parâmetros e corpo, autentique a sessão, autorize a ação para aquele recurso, trate erros e retorne status apropriados. Esconder um link na interface não protege o endpoint. Dados personalizados não podem ser servidos de um cache compartilhado sem uma chave e política seguras. Os padrões de cache de Route Handlers também dependem da versão e da configuração; confira a documentação vigente antes de assumir que uma resposta `GET` é ou não armazenada.

Antes de publicar, verifique se a plataforma oferece o runtime e os recursos exigidos pelo projeto. Um site estático pode servir páginas já geradas, mas endpoints e conteúdo dinâmico precisam de uma plataforma que execute o código correspondente. Segredos devem ser configurados no ambiente de servidor da hospedagem, nunca inseridos no bundle do navegador.

