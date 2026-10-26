---
arquivo_id: "f1-1-1-03-cliente-servidor-fluxo-pagina-01-teoria"
parent_key: "1.1"
tipo_arquivo: "theory"
assunto: "03_cliente_servidor_fluxo_pagina"
ordem: 3
itens_origem: ["Cliente e servidor", "O que acontece ao abrir uma página"]
---

### Cliente e servidor

Um **cliente** é o programa ou dispositivo que inicia uma solicitação a outro sistema. O navegador costuma ser o cliente quando você acessa um site. Um **servidor** é o programa que recebe solicitações e fornece respostas. “Servidor” também pode designar a máquina onde esse programa roda; pelo contexto, o termo pode se referir ao software ou ao computador.

O cliente e o servidor se comunicam por uma rede. O cliente pede um recurso ou uma operação; o servidor interpreta o pedido, executa o que for necessário e devolve uma resposta. O cliente pode então apresentar o resultado ou fazer outra solicitação.

### O que acontece ao abrir uma página

Considere a visita a `https://exemplo.com/produtos`:

1. O navegador interpreta o endereço e identifica o nome de domínio `exemplo.com`.
2. Para encontrar o destino de rede associado a esse nome, o dispositivo consulta o **DNS** (Domain Name System). O DNS funciona como um sistema distribuído de consulta de nomes; não é o próprio site nem o conteúdo da página.
3. O navegador estabelece a comunicação necessária com o servidor e envia uma **requisição HTTP** para obter o recurso solicitado. Em HTTPS, a comunicação HTTP é protegida por TLS.
4. O servidor recebe a requisição. Conforme a aplicação, pode consultar um banco de dados ou outros serviços.
5. O servidor envia uma **resposta HTTP**, que inclui um código de status e pode incluir conteúdo, como HTML ou dados.
6. O navegador interpreta o conteúdo recebido e apresenta a página. Para completar a tela, pode fazer novas requisições para arquivos CSS, imagens, fontes e código JavaScript.

Esse fluxo é um modelo introdutório. Cache, proxies, redes de distribuição de conteúdo, vários serviços e renderização no servidor podem acrescentar etapas ou mudar onde cada parte é executada. O princípio central continua útil: clientes enviam solicitações; sistemas respondem; o navegador pode compor a página a partir de vários recursos.

