---
arquivo_id: "f10-48-2-t01"
parent_key: "48.2"
tipo_arquivo: "theory"
assunto: "01_streaming_contrato_eventos"
ordem: 1
itens_origem: ["### 1. Streaming e contrato de eventos"]
---


### 1. Streaming e contrato de eventos
Sem streaming, a aplicação normalmente espera a resposta completa; com streaming, pode começar a enviar partes antes do término da geração. Para uma aplicação web com fluxo unidirecional servidor → navegador, Server-Sent Events (SSE) é uma opção sobre HTTP. WebSocket permite comunicação bidirecional e pode ser adequado quando cliente e servidor precisam trocar eventos continuamente. Escolha pelo padrão de comunicação, infraestrutura e requisitos, não pela expectativa de que um transporte torne a geração mais correta.

O provedor pode expor uma sequência de eventos com significados diferentes: início, parte de texto, conclusão, erro ou uso de ferramenta. O backend deve entender o protocolo do provedor e, se necessário, traduzir para um contrato estável da aplicação. Não envie eventos internos, dados de raciocínio ou detalhes de erro ao navegador sem necessidade. Delimite cada fluxo por ID de requisição e encaminhe apenas os eventos permitidos.

