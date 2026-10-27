---
arquivo_id: "f6-29-2-01-fronteiras-e-mocks-de-rede-01-teoria-md"
parent_key: "29.2"
tipo_arquivo: "theory"
assunto: "01_fronteiras_e_mocks_de_rede"
ordem: 1
itens_origem: ["## Microtópico 1 — Escolha qual fronteira cada teste precisa atravessar", "## Microtópico 2 — Simule a rede na fronteira com MSW"]
---

## Microtópico 1 — Escolha qual fronteira cada teste precisa atravessar
Um teste de integração verifica se partes que trabalham juntas cumprem um contrato. Na interface web, isso pode significar renderizar um componente, fazer uma interação e permitir que a chamada HTTP atravesse o cliente real até um handler controlado. O teste observa a resposta no DOM sem substituir a função de busca interna do componente.

Um teste com rede simulada pode comprovar que o cliente constrói e envia a requisição esperada, interpreta respostas previstas e apresenta os estados correspondentes. Ele não comprova que o servidor implantado implementa o endpoint, que o banco persiste dados ou que autenticação real está configurada corretamente. Um fluxo Playwright pode usar backend de teste real ou interceptar parte da rede; o que ele valida depende dessa escolha.

Planeje a confiança por pergunta, não por rótulo. Um teste unitário rápido pode verificar transformação isolada; um teste da interface com MSW cobre componentes e protocolo HTTP simulado; um fluxo de navegador pode percorrer as interações e integrações selecionadas. Contrato e backend precisam de verificações próprias para as responsabilidades que o frontend não controla.

## Microtópico 2 — Simule a rede na fronteira com MSW
Mock Service Worker intercepta requisições HTTP na fronteira de rede e permite definir handlers para os endpoints. O cliente de dados continua executando o fluxo normal da aplicação, em vez de uma função interna ser trocada por um mock. Em testes Node, handlers são registrados com a integração de servidor do MSW; no navegador, a integração usa service worker. A API exata muda entre versões: acompanhe a versão instalada e a documentação atual; nas versões atuais, handlers HTTP usam a API `http` e respostas como `HttpResponse`.

Use cenários explícitos que representem o contrato relevante: resposta com dados, coleção vazia, validação rejeitada, sessão não autorizada, falha de servidor e latência. Teste o efeito visível e, quando fizer parte do contrato, a requisição formada: método, caminho, parâmetros e corpo. Uma resposta mockada precisa manter formato e status coerentes com o contrato esperado, ou o teste pode ensinar uma suposição falsa.

Mantenha handlers compartilhados para o comportamento padrão e substitua-os localmente para o caso específico. Restaure handlers após cada caso e encerre o servidor de teste no ciclo de vida configurado. Evite chamadas de rede reais acidentais: um endpoint sem handler deve ser detectável, e o teste deve falhar de modo claro em vez de depender da internet.

