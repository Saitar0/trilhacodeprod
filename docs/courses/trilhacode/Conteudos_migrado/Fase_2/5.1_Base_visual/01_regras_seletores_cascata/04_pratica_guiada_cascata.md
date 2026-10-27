---
arquivo_id: "f2-5-1-01-regras-seletores-cascata-04-pratica-guiada-cascata"
parent_key: "5.1"
tipo_arquivo: "practice"
assunto: "01_regras_seletores_cascata"
ordem: 1
itens_origem: ["P1"]
---

## Práticas

### 1. Guiada — preveja e corrija uma cascata
Sem executar o código primeiro, preveja as cores aplicadas e explique o motivo. Depois confirme no navegador.

```html
<p class="aviso" id="status">Perfil salvo</p>
```

```css
p { color: #333; }
.aviso { color: #a00; }
#status { color: #075; }
.aviso { color: #06c; }
```

**Tarefa:** anote a cor final; indique qual regra perde e por quê; então altere somente uma regra para que o texto fique `#a00` sem usar `!important`.

**Dicas graduais:** (1) marque os seletores que correspondem ao parágrafo; (2) compare elemento, classe e ID; (3) só use a ordem do arquivo para desempatar declarações da mesma especificidade.

