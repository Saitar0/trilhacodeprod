---
arquivo_id: "f3-7-1-90-integracao-p01-pratica-guiada-texto-seguro"
parent_key: "7.1"
tipo_arquivo: "practice"
assuntos: ["01_dom_selecao", "02_texto_seguro_dom"]
ordem: 1
itens_origem: ["P1"]
---

## Práticas

### 1. Guiada — selecione e escreva conteúdo com segurança
Considere:

```html
<p id="resultado"></p>
```

```js
const resultado = document.querySelector("#resultdo");
const entrada = "<strong>Olá</strong>";
resultado.innerHTML = entrada;
```

**Tarefa:** identifique os dois problemas, preveja o que aconteceria se o seletor fosse corrigido e reescreva para exibir a entrada literalmente como texto. Inclua uma proteção para o caso de o seletor não encontrar elemento.

**Dicas graduais:** (1) compare o `id` do HTML ao seletor; (2) lembre-se de que `querySelector` pode retornar `null`; (3) escolha a API que não interpreta a string como marcação.

