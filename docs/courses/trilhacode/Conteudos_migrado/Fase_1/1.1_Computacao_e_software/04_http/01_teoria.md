---
arquivo_id: "f1-1-1-04-http-01-teoria"
parent_key: "1.1"
tipo_arquivo: "theory"
assunto: "04_http"
ordem: 4
itens_origem: ["Requisição e resposta HTTP"]
---

### Requisição e resposta HTTP

**HTTP** (Hypertext Transfer Protocol) é um protocolo usado para trocar recursos e mensagens na web. Uma requisição contém informações sobre o que o cliente quer fazer e qual recurso está envolvido. Uma resposta informa o resultado e pode trazer o conteúdo solicitado.

Exemplo simplificado de requisição:

```http
GET /produtos HTTP/1.1
Host: exemplo.com
Accept: text/html
```

`GET` indica o método usado para solicitar a representação de um recurso. `/produtos` é o caminho solicitado. Os cabeçalhos fornecem informações adicionais. Uma resposta pode se parecer com:

```http
HTTP/1.1 200 OK
Content-Type: text/html

<h1>Produtos</h1>
```

O código `200` indica que a requisição foi atendida com sucesso. Outros resultados são possíveis: `301` indica redirecionamento; `403`, que o acesso foi negado; `404`, que o recurso não foi encontrado; `500`, que ocorreu um erro no servidor. O código ajuda a descrever o resultado, mas não explica sozinho todos os detalhes do que aconteceu.

