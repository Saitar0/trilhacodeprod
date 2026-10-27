---
arquivo_id: "f2-5-3-02-breakpoints-estrategias-teste-conteudo-01-teoria"
parent_key: "5.3"
tipo_arquivo: "theory"
assunto: "02_breakpoints_estrategias_teste_conteudo"
ordem: 2
itens_origem: ["Media queries e breakpoints", "Mobile first e desktop first", "Teste orientado pelo conteúdo"]
---

### Media queries e breakpoints
Uma media query aplica CSS quando uma condição sobre o ambiente é atendida. Breakpoint é o ponto em que uma mudança de layout melhora a leitura ou o uso; escolha-o observando o conteúdo, não copiando uma lista de dispositivos.

```css
.layout { display: grid; grid-template-columns: 1fr; }

@media (min-width: 48rem) {
  .layout { grid-template-columns: 2fr 1fr; }
}
```

### Mobile first e desktop first
**Mobile first** começa com um layout simples para espaço estreito e adiciona capacidades em telas maiores com `min-width`. **Desktop first** começa com o layout amplo e adapta/remova elementos para telas menores, com frequência usando `max-width`. Ambos podem funcionar; escolha a abordagem coerente com o conteúdo e mantenha as regras fáceis de entender.

Flexbox e Grid podem responder naturalmente ao espaço disponível, às vezes sem media queries. Use uma media query quando a composição realmente precisar mudar, não para corrigir toda diferença com valores arbitrários.

### Teste orientado pelo conteúdo
Não existe uma largura que represente todos os dispositivos. Redimensione a viewport e observe onde a navegação quebra, as linhas ficam difíceis de ler, os cartões comprimem ou aparece rolagem horizontal. Registre a largura aproximada do problema e crie um breakpoint onde a mudança de composição o resolve. Teste também conteúdo variável (títulos longos, traduções, imagens) e zoom; uma captura em três larguras é evidência útil, mas não garante funcionamento em todo contexto.

