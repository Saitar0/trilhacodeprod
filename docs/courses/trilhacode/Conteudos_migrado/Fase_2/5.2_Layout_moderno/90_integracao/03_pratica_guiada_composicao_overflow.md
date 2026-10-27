---
arquivo_id: "f2-5-2-90-integracao-03-pratica-guiada-composicao-overflow"
parent_key: "5.2"
tipo_arquivo: "practice"
ordem: 1
itens_origem: ["P1"]
---

## Práticas

### 1. Guiada — diagnostique e corrija a composição
Considere este HTML e CSS. O cartão longo empurra a grade para fora do contêiner e os botões da barra não mantêm espaçamento.

```html
<nav class="toolbar"><a href="/inicio">Início</a><a href="/ajuda">Ajuda</a></nav>
<main class="cards">
  <article class="card"><h2>Guia</h2><p>Introdução</p></article>
  <article class="card"><h2> identificador-extremamente-longo-sem-quebras </h2><p>Detalhes</p></article>
</main>
```

```css
.toolbar { display: block; justify-content: space-between; }
.cards { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; }
```

**Tarefa:** explique por que `justify-content` não distribui os links na barra, identifique o risco de overflow na grade e proponha uma correção sem posicionar cada item manualmente.

**Dicas graduais:** (1) confira o `display` do contêiner que deveria distribuir os links; (2) confirme que Grid cria duas faixas; (3) inspecione a largura mínima do item e decida como a sequência longa deve quebrar.

