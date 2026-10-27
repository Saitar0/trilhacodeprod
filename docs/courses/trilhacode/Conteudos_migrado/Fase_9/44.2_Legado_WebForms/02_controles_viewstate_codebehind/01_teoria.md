---
arquivo_id: "f9-44-2-02-controles-viewstate-codebehind-01-teoria"
parent_key: "44.2"
tipo_arquivo: "theory"
assunto: "02_controles_viewstate_codebehind"
ordem: 2
itens_origem: ["### 2. Controles server-side, ViewState e code-behind"]
---


### 2. Controles server-side, ViewState e code-behind
Controles como `GridView`, `TextBox` e `Button` abstraem partes da interação HTTP e podem simplificar aplicações de negócio antigas. O code-behind frequentemente coordena exibição, validação, acesso a dados e regra de negócio. Se essas responsabilidades estiverem concentradas em handlers de página, regras podem ficar difíceis de testar e reaproveitar; identifique primeiro o que é UI, aplicação e persistência.

**ViewState** guarda estado de página/controles entre postbacks, geralmente serializado no HTML num campo oculto como `__VIEWSTATE`. Isso dá uma experiência de formulário com estado sem manter uma página executando no servidor entre as requisições, mas pode aumentar o tamanho da resposta e o custo de cada round-trip. Não presuma que todo estado está em sessão; determine se vem de ViewState, ControlState, Session, banco ou campos enviados pelo cliente.

**Não coloque segredos ou dados sensíveis em ViewState** e não desative verificações de integridade/event validation por tentativa. O campo oculto é parte do tráfego enviado ao cliente; integridade, confidencialidade e autorização são controles diferentes. Verifique configuração do projeto e versão antes de propor mudança de segurança.

Sinais para localizar no repositório: `.aspx`, `.aspx.cs`/`.aspx.vb`, `runat="server"`, `Page_Load`, `IsPostBack`, handlers `OnClick`, `GridView`, `ViewState`, `web.config`, `Global.asax`, master pages, autenticação e dependências/controles de terceiros.

**Checagem:** ViewState é um banco no servidor que mantém a página aberta entre requisições? Não; ele transporta estado serializado junto da resposta e de postbacks subsequentes, conforme configuração.

