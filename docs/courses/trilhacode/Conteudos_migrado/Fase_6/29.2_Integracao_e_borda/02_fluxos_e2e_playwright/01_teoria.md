---
arquivo_id: "f6-29-2-02-fluxos-e2e-playwright-01-teoria-md"
parent_key: "29.2"
tipo_arquivo: "theory"
assunto: "02_fluxos_e2e_playwright"
ordem: 2
itens_origem: ["## Microtópico 3 — Percorra um caminho crítico no navegador com Playwright"]
---

## Microtópico 3 — Percorra um caminho crítico no navegador com Playwright
Playwright automatiza um navegador real e observa a aplicação por meio de páginas, locators e assertions que esperam condições. Um fluxo crítico pode abrir a aplicação, autenticar em um ambiente de teste, navegar para uma lista, aplicar um filtro e confirmar o resultado. Locators por papel, nome e label expressam melhor o contrato visível que seletores baseados em estrutura interna ou classes instáveis.

Escolha conscientemente o backend:

- **Backend de teste real:** valida a integração selecionada entre navegador, frontend e serviços configurados. Exige ambiente isolado, dados previsíveis e limpeza segura.
- **Rede interceptada:** valida o fluxo de interação no navegador com respostas controladas, mas a comunicação com aquele serviço não foi validada.

Ambos são úteis e respondem perguntas diferentes. Se o objetivo inclui confirmar comunicação com o backend, o cenário precisa realmente alcançá-lo em um ambiente de teste. Nunca use contas ou dados de produção para o exercício. Para operações que alteram dados, prepare contas dedicadas e uma maneira repetível de criar e remover dados.

