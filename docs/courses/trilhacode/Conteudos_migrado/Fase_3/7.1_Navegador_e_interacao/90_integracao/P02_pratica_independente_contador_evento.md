---
arquivo_id: "f3-7-1-90-integracao-p02-pratica-independente-contador-evento"
parent_key: "7.1"
tipo_arquivo: "practice"
assuntos: ["01_dom_selecao", "03_eventos_comportamento_padrao"]
ordem: 2
itens_origem: ["P2"]
---

### 2. Independente — implemente um contador acionado por evento
Parta deste HTML:

```html
<button id="adicionar" type="button">Adicionar</button>
<p id="total" aria-live="polite">Itens: 0</p>
```

Implemente o JavaScript para que cada clique incremente o número e atualize o parágrafo. Confira se os elementos existem antes de registrar o listener. Teste também com teclado e explique por que um `<button>` nativo é adequado para essa ação.

**Dicas graduais:** (1) o estado numérico muda, então use `let`; (2) registre `click` com `addEventListener`; (3) atualize o texto com `textContent` e não recrie o parágrafo.

