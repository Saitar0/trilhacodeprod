---
arquivo_id: "f9-44-2-01-pagina-postback-ciclo-vida-01-teoria"
parent_key: "44.2"
tipo_arquivo: "theory"
assunto: "01_pagina_postback_ciclo_vida"
ordem: 1
itens_origem: ["### 1. Página server-side, postback e ciclo de vida"]
---


### 1. Página server-side, postback e ciclo de vida
ASP.NET Web Forms é um modelo de páginas server-rendered do ASP.NET sobre .NET Framework. A página `.aspx` descreve HTML e controles server-side; o code-behind pode conter C# ou VB. O runtime processa a página no servidor e envia HTML ao navegador. Um controle como `<asp:Button runat="server" OnClick="Salvar_Click">` gera marcação e liga interação do navegador a um handler no servidor.

Uma página percorre etapas de inicialização, restauração de dados/estado do postback, `Page_Load`, eventos dos controles, `PreRender` e renderização. Um **postback** é uma nova requisição HTTP da página para o servidor, normalmente produzida por um controle. `IsPostBack` indica se aquela solicitação é um postback, não se o usuário já autenticou ou se os dados foram salvos.

Como `Page_Load` pode ocorrer tanto no primeiro acesso quanto em postback, carregamentos iniciais costumam ficar sob `if (!IsPostBack)`. Recriar controles dinâmicos e manter seus IDs no momento correto importa para que o framework consiga restaurar valores e associar eventos. Ao ler uma página, acompanhe a ordem: `Page_Init`/`Page_Load` → validação/evento do controle → resposta renderizada.

**Checagem:** `Page_Load` é executado apenas quando o navegador abre a página pela primeira vez? Não; ocorre também em postbacks; use `IsPostBack` se uma inicialização só deve acontecer na primeira carga.

