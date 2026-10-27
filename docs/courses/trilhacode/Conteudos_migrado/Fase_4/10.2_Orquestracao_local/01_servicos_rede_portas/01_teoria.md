---
arquivo_id: "f4-10-2-01-servicos-rede-portas-01-teoria"
parent_key: "10.2"
tipo_arquivo: "theory"
assunto: "01_servicos_rede_portas"
ordem: 1
itens_origem: ["1. Descreva a aplicação como serviços", "2. Configure portas, rede e descoberta de serviços"]
---

## Teoria

### 1. Descreva a aplicação como serviços
Compose usa um arquivo declarativo, normalmente `compose.yaml), para descrever serviços, imagens ou builds, portas, variáveis, redes, volumes e dependências. Cada serviço define uma função da aplicação, como API, PostgreSQL, Redis ou MongoDB. O arquivo pode ser revisado e versionado junto ao projeto para que outra pessoa recrie um ambiente semelhante.

Um serviço não precisa corresponder a uma máquina. Compose cria containers para executar os serviços e recursos de rede/armazenamento necessários. A chave `services` organiza as definições; os nomes dos serviços funcionam também como nomes de descoberta de rede.

Compose pode usar uma imagem publicada com `image` ou construir a partir de um Dockerfile com `build`. Se a configuração muda, `docker compose up` reconcilia os containers conforme necessário. O comando `docker compose config` combina e valida a configuração e ajuda a inspecionar o modelo que será aplicado.

**Erro comum:** tratar o arquivo como uma sequência de comandos imperativos; ele descreve o estado desejado dos serviços.

### 2. Configure portas, rede e descoberta de serviços
Por padrão, Compose cria uma rede para o projeto e conecta nela os serviços. Containers da mesma rede resolvem uns aos outros pelo nome do serviço. Assim, uma API dentro do Compose conecta-se a PostgreSQL em `db:5432), Redis em `cache:6379) e MongoDB em `documentdb:27017). Use portas internas entre serviços; não use o IP atual do container, pois ele pode mudar quando for recriado.

A seção `ports` publica uma porta para clientes fora da rede dos serviços, como ferramentas executadas no host. A forma `127.0.0.1:5432:5432` restringe a publicação à interface local do host; `5432:5432` pode expor a porta em outras interfaces conforme a configuração do ambiente. Não publique um serviço para o host se o uso previsto não precisar dele.

**Erro comum:** configurar a API com `localhost:5432); dentro do container, localhost aponta para a própria API. Para acessar o banco pelo host, use a porta publicada e localhost no cliente do host.

