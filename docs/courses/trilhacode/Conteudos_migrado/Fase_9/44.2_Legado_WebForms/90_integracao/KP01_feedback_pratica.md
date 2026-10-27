---
arquivo_id: "f9-44-2-90-integracao-kp01-feedback-pratica"
parent_key: "44.2"
tipo_arquivo: "answer_key_pratica"
assuntos: ["01_pagina_postback_ciclo_vida", "02_controles_viewstate_codebehind"]
ordem: 1
itens_origem: ["P01"]
---


**Feedback de referência:** no primeiro acesso `IsPostBack` é falso; no envio do formulário é verdadeiro. `Page_Load` roda antes do evento do controle; o estado/postdata já é carregado nos estágios do ciclo. Recarregar a grade sem considerar filtro pode sobrescrever valores ou repetir consulta; controles dinâmicos precisam existir a tempo de o estado/evento ser associado.

**Erro comum:** tratar cada clique como chamada isolada a um endpoint moderno e ignorar que a página e seus controles são reconstruídos a cada requisição.

