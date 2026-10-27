---
arquivo_id: "f6-29-1-02-runner-ambiente-01-teoria-md"
parent_key: "29.1"
tipo_arquivo: "theory"
assunto: "02_runner_ambiente"
ordem: 2
itens_origem: ["## Microtópico 2 — Configure runner e ambiente coerentes"]
---

## Microtópico 2 — Configure runner e ambiente coerentes
Um runner executa os testes, oferece assertions, isolamento e recursos como mocks. Vitest integra-se ao ecossistema Vite; Jest é uma alternativa estabelecida em outros projetos. Normalmente basta escolher o que combina com a configuração existente. Usar os dois no mesmo projeto adiciona configuração e manutenção sem benefício automático.

Um teste de lógica sem DOM pode rodar em Node. Um teste de componente precisa de um ambiente com APIs de navegador: um DOM simulado como `jsdom` ou `happy-dom`, ou um modo de navegador real quando o projeto e o escopo justificarem. Esses ambientes têm diferenças. DOM simulado é rápido e suficiente para muitos comportamentos; não comprova layout, renderização real de CSS ou todos os detalhes de APIs do navegador.

Confira a versão e as instruções de configuração vigentes para o runner, o framework React e as bibliotecas auxiliares do projeto. O arquivo de setup pode registrar matchers ou configuração compartilhada. Um teste que só passa por causa de globals ou estado residual de outro teste não está isolado corretamente.

