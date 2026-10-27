---
arquivo_id: "f3-7-1-02-texto-seguro-dom-01-teoria"
parent_key: "7.1"
tipo_arquivo: "theory"
assunto: "02_texto_seguro_dom"
ordem: 2
itens_origem: ["Texto e marcação no DOM"]
---

### Texto e marcação no DOM
Para texto visível, `textContent` escreve texto sem interpretá-lo como HTML. `innerHTML` interpreta a string como marcação e substitui os descendentes do elemento; não use conteúdo não confiável com `innerHTML` sem um processo adequado de sanitização. Para mostrar o que alguém digitou como texto, prefira `textContent`.

