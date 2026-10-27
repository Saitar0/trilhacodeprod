---
arquivo_id: "f2-5-4-01-organizacao-manutencao-css-04-pratica-guiada-escopo-regras"
parent_key: "5.4"
tipo_arquivo: "practice"
assunto: "01_organizacao_manutencao_css"
ordem: 1
itens_origem: ["P1"]
---

## Práticas

### 1. Guiada — localize o alcance de cada regra
Leia este HTML e CSS. Antes de reorganizar, anote qual regra afeta cada elemento e quais alterações poderiam afetar mais de um componente.

```html
<article class="card"><h2>Curso</h2><p class="muted">Em andamento</p></article>
<section class="profile"><h2>Perfil</h2><p class="muted">Pessoa estudante</p></section>
```

```css
div { padding: 1rem; }
.card p { color: #555; }
.profile p { color: #555; }
.card { padding: 1rem; }
.muted { color: #777; }
```

**Tarefa:** identifique a regra que não alcança esses elementos, a duplicação aparente e a regra compartilhada que já expressa uma intenção comum. Proponha uma versão mais simples e diga como confirmaria que o resultado não mudou.

**Dicas graduais:** (1) confira as tags do HTML contra o seletor `div`; (2) compare as declarações de cor e o seletor `.muted`; (3) altere uma regra por vez e verifique ambos os componentes.

