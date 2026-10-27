---
arquivo_id: "f6-29-2-02-fluxos-e2e-playwright-p02-pratica-md"
parent_key: "29.2"
tipo_arquivo: "practice"
assunto: "02_fluxos_e2e_playwright"
ordem: 2
itens_origem: ["P02"]
---

### Atividade 2 — Automatize um fluxo crítico com Playwright
**Objetivo:** confirmar que um caminho essencial funciona pelo navegador.

**Passos:**
1. Escolha um fluxo crítico, como entrar em uma conta de teste, abrir pedidos, filtrar e visualizar um registro.
2. Decida se o teste usará backend de teste real ou rede interceptada e registre o que essa opção comprova e deixa de comprovar.
3. Localize controles por papel/nome ou label e use assertions que aguardem o estado esperado, sem pausas fixas.
4. Prepare dados identificáveis para o teste e implemente limpeza ou isolamento para que a execução repetida não acumule registros.
5. Rode o fluxo isoladamente e em conjunto com a suíte; verifique que ele não depende da ordem nem da sessão de outro caso.

**Dica:** faça o teste comprovar uma jornada de valor e mantenha detalhes já cobertos pelos testes de componente fora do fluxo E2E quando não acrescentarem confiança.

**Entrega:** um fluxo Playwright reproduzível e um pequeno mapa de serviços reais e simulados.

**Critérios de conclusão:** fluxo passa por interações de navegador; ambiente e dados são seguros e isolados; limites da integração estão declarados.

