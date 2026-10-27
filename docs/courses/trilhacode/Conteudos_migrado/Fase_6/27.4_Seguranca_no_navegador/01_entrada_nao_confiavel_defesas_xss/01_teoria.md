---
arquivo_id: "f6-27-4-01-entrada-nao-confiavel-defesas-xss-01-teoria-md"
parent_key: "27.4"
tipo_arquivo: "theory"
assunto: "01_entrada_nao_confiavel_defesas_xss"
ordem: 1
itens_origem: ["### 1. Rastrear entrada não confiável até a renderização (XSS)", "### 2. Escolher defesa conforme o contexto"]
---

### 1. Rastrear entrada não confiável até a renderização (XSS)
Cross-site scripting (XSS) ocorre quando dado controlável por alguém é interpretado pelo navegador como código ou conteúdo ativo. O dado pode vir de formulário, URL, API, conteúdo armazenado ou dependência. XSS refletido aparece em resposta ligada à requisição; XSS armazenado persiste e pode alcançar outros usuários; XSS baseado em DOM surge quando código do cliente move dado não confiável para um contexto perigoso.

Procure a cadeia **fonte → transformação → destino**. Renderizar texto interpolado em React normalmente escapa caracteres de marcação, mas isso não protege toda saída: HTML bruto (`dangerouslySetInnerHTML`), APIs do DOM, atributos/URLs perigosos, templates e bibliotecas podem reabrir a interpretação. Se o requisito for mostrar texto, use o destino de texto/renderização normal. Se HTML rico for indispensável, aplique sanitizador mantido e política allowlist apropriada antes de inserir o HTML. Escapar codifica para um contexto; sanitizar remove/limita estruturas permitidas. Não tente remover strings suspeitas com substituições improvisadas.

### 2. Escolher defesa conforme o contexto
Validação de entrada ajuda a impor regras de produto, mas não substitui a codificação/segurança de saída. Uma string segura como texto pode não ser segura em URL, CSS, atributo ou script. Evite construir código executável com dado dinâmico. Para links fornecidos pelo usuário, valide e permita apenas esquemas e destinos esperados; não confie apenas no nome/forma visual do link.

Content Security Policy (CSP) limita origens e tipos de conteúdo que o navegador pode executar ou carregar. Uma política bem projetada pode reduzir impacto e ajudar a detectar violações, mas não corrige o ponto de injeção e pode ser configurada permissivamente. Trate CSP como defesa em camadas, teste-a em aplicação própria e evite depender de `unsafe-inline` sem necessidade. Não habilite relatórios que enviem conteúdo sensível a coletores não aprovados.

