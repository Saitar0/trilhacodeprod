---
arquivo_id: "f3-7-5-01-reproducao-console-elements-sources-p01-pratica-guiada-seletor"
parent_key: "7.5"
tipo_arquivo: "practice"
assunto: "01_reproducao_console_elements_sources"
ordem: 1
itens_origem: ["P1"]
---

## Práticas

### 1. Guiada — localize um seletor sem correspondência
A página contém:

```html
<input id="nome" />
<button id="enviar">Enviar</button>
<p id="mensagem"></p>
```

O módulo contém:

```js
const entrada = document.querySelector("#nomes");
const botao = document.querySelector("#enviar");

botao.addEventListener("click", () => {
  document.querySelector("#mensagem").textContent = entrada.value;
});
```

Ao carregar, o Console mostra erro ao ler `addEventListener`. Use Elements e Console para verificar a hipótese. Corrija a causa e valide o clique com um breakpoint no handler.

**Dica:** compare o seletor com o `id` real; veja qual variável vale `null` antes de registrar o evento.

