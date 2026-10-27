---
arquivo_id: "f2-5-3-01-layout-fluido-viewport-04-pratica-guiada-overflow-viewport"
parent_key: "5.3"
tipo_arquivo: "practice"
assunto: "01_layout_fluido_viewport"
ordem: 1
itens_origem: ["P1"]
---

## Práticas

### 1. Guiada — investigue overflow e viewport
Considere o documento e as regras abaixo. Em uma tela estreita, a página tem rolagem horizontal e uma faixa de conteúdo muito pequena.

```html
<head>
  <title>Agenda</title>
  <link rel="stylesheet" href="styles.css">
</head>
<main class="conteudo">
  <img src="evento.jpg" alt="Pessoas em uma oficina">
  <h1>Programação completa do encontro de desenvolvimento web</h1>
</main>
```

```css
.conteudo { width: 960px; margin: 0 auto; }
img { width: 800px; }
```

**Tarefa:** identifique as causas prováveis, proponha uma sequência mínima de correções e diga o que observaria após cada mudança.

**Dicas graduais:** (1) verifique as dimensões fixas; (2) confira se há configuração de viewport; (3) defina largura fluida com limite e permita que a imagem caiba no contêiner.

