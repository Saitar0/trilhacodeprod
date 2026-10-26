---
arquivo_id: "f1-1-1-02-aplicacoes-locais-web-camadas-01-teoria"
parent_key: "1.1"
tipo_arquivo: "theory"
assunto: "02_aplicacoes_locais_web_camadas"
ordem: 2
itens_origem: ["Aplicações locais e aplicações web", "Frontend, backend e banco de dados"]
---

### Aplicações locais e aplicações web

Uma **aplicação local** é executada principalmente no dispositivo da pessoa. Ela pode funcionar sem internet, embora possa usar serviços online. Um editor de texto instalado é um exemplo.

Uma **aplicação web** é acessada por meio de um navegador ou de outro cliente conectado à rede. Parte do código pode rodar no navegador; outra parte pode rodar em servidores remotos. Aplicações web também podem guardar dados localmente. Portanto, “local” e “web” descrevem onde partes do sistema são executadas e como são acessadas — não uma separação absoluta entre dois tipos que nunca se misturam.

### Frontend, backend e banco de dados

- **Frontend** é a parte com que a pessoa interage. Na web, costuma incluir a interface apresentada pelo navegador e o código que responde a ações como clicar, preencher um formulário ou navegar.
- **Backend** é a parte que executa regras e operações fora da interface, geralmente em um servidor. Pode validar uma solicitação, aplicar regras de negócio, consultar dados ou chamar outros serviços.
- **Banco de dados** é um sistema usado para organizar e consultar dados de forma persistente. Ele pode ser acessado pelo backend; o navegador normalmente não conversa diretamente com o banco de dados da aplicação.

Esses nomes descrevem papéis, não necessariamente máquinas diferentes. Em um projeto pequeno, vários componentes podem rodar no mesmo computador. Em produção, podem estar distribuídos por muitos servidores. Uma mesma aplicação também pode fazer algumas operações no navegador e outras no backend.

