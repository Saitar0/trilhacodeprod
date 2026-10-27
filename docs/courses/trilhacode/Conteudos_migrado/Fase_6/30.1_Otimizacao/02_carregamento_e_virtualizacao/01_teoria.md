---
arquivo_id: "f6-30-1-02-carregamento-e-virtualizacao-01-teoria-md"
parent_key: "30.1"
tipo_arquivo: "theory"
assunto: "02_carregamento_e_virtualizacao"
ordem: 2
itens_origem: ["## Microtópico 3 — Divida código e carregue partes quando forem necessárias", "## Microtópico 4 — Virtualize coleções realmente grandes com cuidado"]
---

## Microtópico 3 — Divida código e carregue partes quando forem necessárias
Divisão de código cria fronteiras de carregamento em vez de enviar todo o código inicial à pessoa. Com `lazy` e `Suspense`, um componente pode ser carregado quando a rota ou a interação que o usa torna-se necessária. Isso pode reduzir o JavaScript inicial, mas o primeiro acesso à parte adiada inclui uma espera e uma solicitação adicional.

Escolha a fronteira de acordo com a experiência. Rotas pouco visitadas, editores pesados ou recursos usados apenas depois de uma ação podem ser bons candidatos. Dividir demais pode criar muitos arquivos pequenos, solicitações e estados de carregamento; dividir pouco pode manter dependências grandes no pacote inicial. Compare o bundle inicial e os chunks carregados no fluxo relevante. Projete um fallback que explique a espera, preserve o contexto e permita que a interface continue compreensível.

Code splitting muda quando e quanto código chega ao navegador. Ele não reduz o trabalho do servidor da API, não remove a dependência pesada do total publicado e não garante ganho se o chunk for carregado imediatamente em todas as visitas.

## Microtópico 4 — Virtualize coleções realmente grandes com cuidado
Uma lista longa pode gastar tempo criando, atualizando e mantendo muitos elementos no DOM, mesmo que só alguns estejam visíveis. Virtualização mantém uma janela de itens renderizados perto da área de rolagem e substitui os elementos conforme a pessoa navega. Bibliotecas como TanStack Virtual oferecem primitivas para calcular essa janela.

Virtualização pode reduzir trabalho do DOM; não reduz automaticamente o tamanho dos dados baixados, a consulta no servidor ou o custo de processamento de cada registro. Paginação e virtualização tratam problemas diferentes e podem ser combinadas: paginação controla quais dados são buscados; virtualização controla quantas linhas são montadas ao mesmo tempo.

Linhas de altura variável precisam ser medidas ou estimadas. Teste rolagem, redimensionamento, atualização dos dados e navegação por teclado. Considere como leitores de tela percebem o conjunto parcial e como a pessoa alcança itens fora da janela. Se a coleção é pequena ou a medição mostra que o gargalo está em outro lugar, a complexidade de virtualizar pode não valer a pena.

