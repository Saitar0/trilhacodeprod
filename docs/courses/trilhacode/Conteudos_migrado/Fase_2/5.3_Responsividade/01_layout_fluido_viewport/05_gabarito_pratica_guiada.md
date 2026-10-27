---
arquivo_id: "f2-5-3-01-layout-fluido-viewport-05-gabarito-pratica-guiada"
parent_key: "5.3"
tipo_arquivo: "answer_key_pratica"
assunto: "01_layout_fluido_viewport"
ordem: 1
itens_origem: ["P1"]
---

**Solução comentada:** adicione `<meta name="viewport" content="width=device-width, initial-scale=1">`; limite `.conteudo` com largura fluida, por exemplo `width: min(100% - 2rem, 70rem); margin-inline: auto;`; use `img { max-width: 100%; height: auto; }`. Teste uma largura estreita e outra ampla. Se o título ainda causar uma linha desconfortável, decida onde a composição ou tipografia deve mudar, em vez de adicionar um breakpoint sem evidência.

**Erros comuns:** reduzir toda a página com zoom; trocar 960 px por outro valor fixo; definir `width: 100vw` sem considerar margens e barras de rolagem; esconder o overflow sem encontrar o elemento que o causa.

