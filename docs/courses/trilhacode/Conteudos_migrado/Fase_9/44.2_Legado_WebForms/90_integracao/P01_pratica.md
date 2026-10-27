---
arquivo_id: "f9-44-2-90-integracao-p01-pratica"
parent_key: "44.2"
tipo_arquivo: "practice"
assuntos: ["01_pagina_postback_ciclo_vida", "02_controles_viewstate_codebehind"]
ordem: 1
itens_origem: ["P01"]
---


### Atividade 1 — Leia o ciclo de uma página
**Contexto:** uma página `Produtos.aspx` tem um `GridView`, botão `Atualizar` e `Page_Load`. O handler carrega produtos do banco; o usuário vê a página e depois atualiza um filtro.

**Instruções:** desenhe a carga inicial e o postback do botão. Marque quando `IsPostBack` será verdadeiro, quando `Page_Load` roda, quando o evento do botão acontece, de onde podem vir valores restaurados e em que ponto a página é renderizada. Aponte um risco se o código carrega a grade em toda solicitação e outro se controles dinâmicos não são recriados no ciclo correto.

**Entrega:** duas sequências curtas (primeiro acesso e postback) e uma lista de três pontos do code-behind que inspecionaria.

**Dica gradual:** compare `if (!IsPostBack)` com a chamada do handler; consulte o ciclo de página para distinguir load, postback event handling e render.

