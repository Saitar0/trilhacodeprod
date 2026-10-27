---
arquivo_id: "f2-5-1-01-regras-seletores-cascata-01-teoria"
parent_key: "5.1"
tipo_arquivo: "theory"
assunto: "01_regras_seletores_cascata"
ordem: 1
itens_origem: ["Regras e seletores", "Cascata e especificidade"]
---

## Teoria

### Regras e seletores
CSS (Cascading Style Sheets) descreve a apresentação dos elementos. Uma regra contém um seletor e declarações. Seletores podem apontar para elementos (`p`), classes (`.aviso`), IDs (`#topo`), estados (`:hover`) e relações entre elementos. Prefira classes com nomes relacionados à função do componente; IDs devem ser únicos e seletores excessivamente específicos dificultam manutenção.

```css
.card {
  color: #263238;
  padding: 1rem;
  border: 1px solid #cfd8dc;
}
```

### Cascata e especificidade
Quando várias declarações podem definir a mesma propriedade, o navegador resolve conflitos considerando relevância, origem/importância, camadas, especificidade, escopo e ordem de aparição. Para o nível inicial, compare regras da mesma origem e camada: uma regra mais específica tende a vencer; quando especificidade empata, a última declaração aplicável vence. `!important` altera a prioridade e deve ser evitado como correção padrão.

