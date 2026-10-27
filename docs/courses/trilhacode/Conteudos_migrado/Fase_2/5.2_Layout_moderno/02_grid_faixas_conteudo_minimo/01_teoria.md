---
arquivo_id: "f2-5-2-02-grid-faixas-conteudo-minimo-01-teoria"
parent_key: "5.2"
tipo_arquivo: "theory"
assunto: "02_grid_faixas_conteudo_minimo"
ordem: 2
itens_origem: ["Linhas e colunas com Grid", "Itens, faixas e conteúdo mínimo"]
---

### Linhas e colunas com Grid
CSS Grid organiza conteúdo em duas dimensões, definindo linhas e colunas. O contêiner pode usar `grid-template-columns`, `grid-template-rows`, `gap` e posicionamento por linhas/áreas. Unidades flexíveis como `fr` distribuem espaço disponível; funções como `minmax()` ajudam a expressar limites.

```css
.cards {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}
```

Grid é útil quando linhas e colunas precisam se relacionar. Flexbox e Grid podem ser combinados: Grid para a estrutura da página e Flexbox dentro de cada componente, por exemplo.

### Itens, faixas e conteúdo mínimo
Grid cria faixas explícitas quando você as declara; conteúdo que excede essa definição pode criar faixas implícitas. O tamanho mínimo automático de itens pode impedir que uma coluna encolha como esperado, sobretudo quando há conteúdo longo. `minmax(0, 1fr)` permite que a faixa flexível encolha até zero; `min-width: 0` pode ser necessário no próprio item para que seu conteúdo não force o contêiner a transbordar. Antes de aplicar essas regras, confirme qual caixa está causando o overflow e trate palavras ou mídias que não podem quebrar ou encolher.

```css
.cards {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.card { min-width: 0; }
```

