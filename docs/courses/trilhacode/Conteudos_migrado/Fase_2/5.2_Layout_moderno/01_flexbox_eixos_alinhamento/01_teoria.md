---
arquivo_id: "f2-5-2-01-flexbox-eixos-alinhamento-01-teoria"
parent_key: "5.2"
tipo_arquivo: "theory"
assunto: "01_flexbox_eixos_alinhamento"
ordem: 1
itens_origem: ["Eixo principal do layout", "Alinhamento e distribuição"]
---

## Teoria

### Eixo principal do layout
Flexbox organiza itens em uma dimensão por vez: em linha ou coluna. O contêiner flex define o eixo principal e o eixo transversal. `justify-content` distribui espaço no eixo principal; `align-items` alinha itens no eixo transversal; `gap` cria espaçamento consistente. Itens podem crescer, encolher e quebrar linha conforme as regras definidas.

```css
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}
```

Flexbox costuma funcionar bem para barras de navegação, grupos de botões ou alinhamento de itens relacionados em uma direção. Não é limitado a uma única linha; `flex-wrap` permite que itens ocupem novas linhas.

### Alinhamento e distribuição
Identifique primeiro o contêiner e o espaço disponível. Alinhamento controla posição relativa; distribuição define como o espaço livre fica entre ou ao redor dos itens. Não confunda `align-content` (distribuição de linhas/colunas no contêiner) com `align-items` (alinhamento de itens). Nomes e efeitos dependem do modo de layout e dos eixos.

