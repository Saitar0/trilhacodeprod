---
title: "1.1 — Computação e software"
key: "1.1"
tipo: integrado
carater: obrigatorio
profundidade: media
estimativa_minutos: 90
tags:
  - fundamentos
  - web
status: rascunho
---

# 1.1 — Computação e software

## Objetivo

Entender o que é software, como um programa é executado e como cliente, servidor e banco de dados se relacionam na web. Ao final, você deverá conseguir narrar o caminho de uma ação no navegador até a resposta exibida, usando corretamente os termos requisição, resposta, HTTP, DNS e API.

## Teoria

### Do problema ao programa

Um computador executa instruções representadas de uma forma que seu hardware consegue processar. Um **programa** é um conjunto organizado dessas instruções. **Software** é um termo mais amplo: inclui programas, arquivos de configuração, dados e outros componentes que juntos oferecem uma função. Um navegador, por exemplo, é um software composto por muitos programas e recursos; uma aplicação web também pode reunir código executado no navegador, serviços no servidor e dados persistidos.

Quando você inicia um programa, o sistema operacional carrega o que ele precisa para funcionar, reserva recursos e inicia sua execução. O processador executa instruções; a memória mantém temporariamente dados em uso; arquivos podem guardar dados de forma persistente. Não é necessário conhecer ainda os detalhes de arquitetura do computador: por ora, guarde que um programa em execução recebe entradas, realiza operações e produz saídas.

Exemplo: em uma calculadora, os números digitados são entradas, as operações são processadas pelo programa e o resultado exibido é uma saída. Em uma aplicação web, clicar em “Entrar” também inicia um fluxo: a interface coleta dados, um serviço verifica a solicitação e a aplicação devolve uma resposta.

### Aplicações locais e aplicações web

Uma **aplicação local** é executada principalmente no dispositivo da pessoa. Ela pode funcionar sem internet, embora possa usar serviços online. Um editor de texto instalado é um exemplo.

Uma **aplicação web** é acessada por meio de um navegador ou de outro cliente conectado à rede. Parte do código pode rodar no navegador; outra parte pode rodar em servidores remotos. Aplicações web também podem guardar dados localmente. Portanto, “local” e “web” descrevem onde partes do sistema são executadas e como são acessadas — não uma separação absoluta entre dois tipos que nunca se misturam.

### Frontend, backend e banco de dados

- **Frontend** é a parte com que a pessoa interage. Na web, costuma incluir a interface apresentada pelo navegador e o código que responde a ações como clicar, preencher um formulário ou navegar.
- **Backend** é a parte que executa regras e operações fora da interface, geralmente em um servidor. Pode validar uma solicitação, aplicar regras de negócio, consultar dados ou chamar outros serviços.
- **Banco de dados** é um sistema usado para organizar e consultar dados de forma persistente. Ele pode ser acessado pelo backend; o navegador normalmente não conversa diretamente com o banco de dados da aplicação.

Esses nomes descrevem papéis, não necessariamente máquinas diferentes. Em um projeto pequeno, vários componentes podem rodar no mesmo computador. Em produção, podem estar distribuídos por muitos servidores. Uma mesma aplicação também pode fazer algumas operações no navegador e outras no backend.

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

### APIs: uma interface de comunicação

Uma **API** (Application Programming Interface) é uma interface definida para que um software use capacidades ou dados oferecidos por outro. Ela especifica como fazer solicitações e como interpretar respostas. APIs não são exclusivas da web: existem em bibliotecas, sistemas operacionais e serviços.

Uma API web pode receber requisições HTTP. Por exemplo, a interface de uma loja pode pedir ao backend uma lista de produtos. O backend aplica as regras e talvez consulte o banco de dados; a API devolve os dados em um formato acordado, e o frontend os apresenta. A API é o contrato de comunicação entre partes do software; não é, por si só, o banco de dados nem a tela.

### Uma visão integrada

Ao clicar em “Ver meus pedidos”, o frontend pode enviar uma requisição à API. O backend identifica a operação, verifica as permissões e consulta os dados necessários. O banco de dados devolve os registros ao backend. O backend monta uma resposta HTTP, e o frontend atualiza a interface.

Nem todo clique precisa chegar ao servidor. Abrir um menu, por exemplo, pode ser resolvido inteiramente pelo frontend. A decisão depende do que a aplicação precisa fazer e de quais dados ou regras estão envolvidos.

## Resumo

- Programa é um conjunto de instruções em execução; software inclui os componentes que formam uma solução.
- Aplicações web podem executar partes no navegador e partes em servidores, além de usar armazenamento local.
- Frontend cuida da interação; backend aplica operações fora da interface; banco de dados mantém dados organizados e persistentes.
- Cliente inicia uma solicitação; servidor recebe e responde.
- DNS ajuda a localizar o destino associado a um nome de domínio.
- HTTP define mensagens de requisição e resposta usadas para transferir recursos na web.
- API é um contrato pelo qual softwares oferecem e utilizam capacidades ou dados.
- Um navegador pode fazer várias requisições para montar uma página; detalhes de infraestrutura podem adicionar etapas.

## Verificação — quiz

### Questões

1. Qual alternativa descreve melhor a relação entre software e programa?
   - A. São sinônimos exatos em qualquer contexto.
   - B. Programa é um conjunto de instruções; software é um termo mais amplo para os componentes de uma solução.
   - C. Software é apenas o hardware que executa instruções.
   - D. Programa é sempre uma página web.

2. Ao abrir uma página, qual papel o DNS desempenha?
   - A. Renderiza o HTML na tela.
   - B. Armazena os dados da aplicação.
   - C. Ajuda a encontrar o destino de rede associado ao nome de domínio.
   - D. Garante que o servidor sempre responderá com sucesso.

3. Qual afirmação sobre frontend, backend e banco de dados é correta?
   - A. São sempre três computadores diferentes.
   - B. O frontend é a interface e a interação; o backend executa operações; o banco de dados persiste dados.
   - C. O navegador deve conectar diretamente ao banco de dados em toda aplicação web.
   - D. O backend é o nome dado ao domínio do site.

4. O que HTTP define no fluxo básico da web?
   - A. Mensagens de requisição e resposta para troca de recursos e dados.
   - B. A linguagem usada exclusivamente para criar estilos visuais.
   - C. O endereço físico do computador do usuário.
   - D. O formato interno de todos os bancos de dados.

5. Uma API web pode usar HTTP. Qual é a melhor descrição de API?
   - A. Um contrato/interface que permite a softwares solicitar capacidades ou dados.
   - B. Um tipo específico de servidor físico.
   - C. Uma cópia local do navegador.
   - D. Um banco de dados obrigatório em qualquer projeto.

### Gabarito comentado

1. **B.** Programa descreve instruções; software pode incluir programas, configurações e recursos relacionados.
2. **C.** DNS resolve nomes para informações de localização. Não entrega o conteúdo da página nem garante que o destino esteja disponível.
3. **B.** São papéis lógicos; podem compartilhar uma máquina, mas desempenham funções diferentes.
4. **A.** HTTP organiza a comunicação em mensagens. A resposta inclui informações de resultado e, muitas vezes, um corpo com conteúdo.
5. **A.** API define como uma parte de software pode interagir com outra; HTTP é um dos meios possíveis para expor uma API.

## Prática — três níveis

Faça as atividades em ordem. A primeira é guiada e trabalha a identificação dos papéis; a segunda pede que você modele dois fluxos; a terceira transfere o raciocínio para uma página real. Você pode desenhar à mão ou usar texto e setas.

### 1. Guiada — identifique os papéis

Para cada situação, indique o componente ou papel mais diretamente envolvido. Alguns fluxos envolvem mais de um componente. Responda também se há uma consulta a banco de dados necessariamente.

| Situação | O que identificar |
|---|---|
| A pessoa abre uma página digitando `loja.exemplo/produtos`. | Cliente, DNS e quem envia/recebe a requisição HTTP. |
| A pessoa abre um menu já carregado e a tela apenas mostra opções. | Onde a ação pode ser processada e se uma solicitação ao servidor é obrigatória. |
| A pessoa envia um formulário de login. | Qual parte recebe os dados, onde a regra de autenticação deve ser aplicada e como o resultado volta. |
| A aplicação precisa buscar o endereço de entrega salvo. | Qual componente deve solicitar os dados persistidos e qual componente os mantém. |
| O navegador precisa saber a que destino de rede corresponde `loja.exemplo`. | Para que serve o DNS e o que ele não fornece. |

**Gabarito comentado**

1. O navegador é o cliente; ele pode consultar o DNS para localizar o destino e envia uma requisição HTTP ao servidor. A resposta volta ao cliente. DNS não entrega os produtos.
2. A interação pode ser resolvida pelo frontend já carregado. Uma chamada ao servidor só é necessária se a ação depender de dados, regras ou operações remotas.
3. O frontend coleta e envia o formulário; o backend valida a solicitação e aplica as regras. O servidor devolve uma resposta que o frontend usa para atualizar a interface. Dados de conta podem ser consultados, mas isso depende da implementação.
4. O backend normalmente consulta o banco de dados e devolve ao cliente somente o resultado permitido pela aplicação. O navegador não deve receber acesso direto ao banco da aplicação.
5. DNS ajuda a resolver o nome de domínio para informações de localização de rede. Não armazena o conteúdo do site, não autentica a pessoa e não garante que o servidor responderá.

### 2. Independente — compare dois fluxos

Uma enciclopédia fictícia tem uma página pública `/sobre` e uma página `/minha-conta` que mostra o nome da pessoa autenticada. Represente os dois fluxos, da ação da pessoa até a tela atualizada.

**Entregue:**

1. Dois diagramas com participantes e setas nomeadas.
2. Uma indicação do que pode ser resolvido no frontend e do que exige processamento no backend.
3. Uma indicação explícita de onde o banco de dados pode ser consultado — e por que ele não é obrigatório no primeiro fluxo.
4. Uma frase dizendo quando o DNS entra no fluxo e por que não precisa aparecer como uma consulta nova em toda requisição.

**Dicas progressivas**

- Primeiro, escreva quem inicia a ação e quem recebe cada mensagem. Depois, nomeie a mensagem (por exemplo, requisição HTTP, consulta ao banco ou resposta HTTP).
- Na página pública, considere que o conteúdo pode estar no próprio servidor ou em cache. Na página da conta, considere que o servidor precisa verificar a sessão e obter dados autorizados. Não suponha que o navegador fale diretamente com o banco.

**Referência para autocorreção**

```text
Fluxo público (um modelo possível):
pessoa → navegador (cliente)
navegador → DNS (se ainda precisar resolver o domínio)
navegador → servidor: requisição HTTP por /sobre
servidor → navegador: resposta HTTP com a página ou seus dados
navegador → pessoa: apresenta o conteúdo
Banco de dados: não é obrigatório; o conteúdo pode ser estático, estar em cache ou vir de outra fonte.

Fluxo da conta (um modelo possível):
pessoa → frontend: abre /minha-conta
navegador → servidor/API: requisição autenticada
backend → serviço de sessão e/ou banco: valida a sessão e busca dados necessários
backend → navegador: resposta HTTP com os dados permitidos ou um erro adequado
frontend → pessoa: apresenta o resultado
```

Há outras arquiteturas válidas. O essencial é manter as responsabilidades claras, mostrar requisição e resposta e não tratar DNS nem banco de dados como etapas invariáveis de qualquer navegação.

**Critérios de autocorreção (0–2 pontos cada; total 8)**

- Identifica corretamente cliente/navegador e servidor/backend nos dois diagramas.
- Nomeia as mensagens e mostra a resposta voltando ao cliente.
- Distingue uma página pública que pode ser servida sem consulta ao banco do fluxo autenticado que pode exigir dados persistidos.
- Explica DNS como resolução de nome e considera cache/resolução já existente.

Considere a atividade concluída com pelo menos 6 pontos e sem erro conceitual sobre DNS ou acesso direto do navegador ao banco. Se ficar abaixo disso, revise o critério perdido e redesenhe o fluxo correspondente.

### 3. Transferência — desenhe o caminho de uma página real

Escolha uma página que você usa e represente o que acontece quando você a abre. Inclua cliente/navegador, DNS, servidor, requisição, resposta, frontend, backend e banco de dados quando fizerem parte do fluxo.

Use setas nomeadas. Não desenhe o banco como etapa obrigatória: marque-o como “consultado, se necessário”. Depois, escreva de cinco a oito frases explicando o fluxo e identifique pelo menos uma simplificação do desenho.

**Exemplo de esqueleto:**

```text
Pessoa → navegador (cliente)
       → consulta DNS para o domínio (se necessário)
       → requisição HTTP ao servidor
       → backend (se a aplicação precisar processar a solicitação)
       → banco de dados (se precisar consultar ou salvar dados)
       ← resposta HTTP
       ← navegador interpreta os recursos e apresenta a página
```

**Verificação final:** o seu diagrama mostra quem inicia cada mensagem, identifica o que é opcional, não confunde DNS com armazenamento e não coloca o banco de dados como destino direto do navegador?

## Critério de conclusão

Sem consultar o material, a pessoa consegue explicar a diferença entre frontend, backend e banco de dados; narrar o fluxo navegador → DNS → requisição/resposta HTTP → página; e explicar para que serve uma API. O diagrama deve mostrar corretamente cliente e servidor e não tratar DNS como armazenamento ou banco de dados como etapa obrigatória de toda navegação.

## Conexões

- Complementar: [[Fase_1_Base_Tecnica#1.2 — Ambiente de desenvolvimento|1.2 — Ambiente de desenvolvimento]]
- Relacionado: [[Fase_3_Base_da_Web_JS_TS_Node#7.3 — Dados e comunicação|7.3 — Dados e comunicação]]
- Relacionado: [[Fase_5_Backend_e_Arquitetura#18.1 — Estrutura|18.1 — Estrutura]]

## Referências

- **MDN — How the web works** · https://developer.mozilla.org/en-US/docs/Learn_web_development/Getting_started/Web_standards/How_the_web_works · papéis de cliente e servidor, DNS, fluxo de navegação e noções de HTTP. Link e cobertura conferidos em 14/10/2026.
- **MDN — Overview of HTTP** · https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview · modelo cliente-servidor, mensagens, requisição, resposta, status e APIs baseadas em HTTP. Link e cobertura conferidos em 14/10/2026.
