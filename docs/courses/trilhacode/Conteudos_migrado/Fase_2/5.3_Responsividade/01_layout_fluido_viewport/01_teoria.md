---
arquivo_id: "f2-5-3-01-layout-fluido-viewport-01-teoria"
parent_key: "5.3"
tipo_arquivo: "theory"
assunto: "01_layout_fluido_viewport"
ordem: 1
itens_origem: ["Layout adaptável", "Viewport e conteúdo fluido"]
---

## Teoria

### Layout adaptável
Design responsivo é uma abordagem para que o conteúdo funcione em diferentes larguras, orientações, resoluções e formas de interação. Não significa criar uma versão para cada modelo de dispositivo. Estruture conteúdo em fluxo normal, prefira limites flexíveis e deixe os componentes crescerem ou se reorganizarem conforme o espaço.

Medidas como `%`, `rem`, `em`, `vw` e funções `min()`, `max()` e `clamp()` podem expressar dimensões relativas. `max-width` limita a largura de conteúdo; imagens fluidas costumam usar `max-width: 100%` para não ultrapassar o contêiner.

### Viewport e conteúdo fluido
Inclua `<meta name="viewport" content="width=device-width, initial-scale=1">` no documento para que navegadores móveis usem a largura do dispositivo como viewport de layout. Sem essa configuração, o navegador pode apresentar uma viewport virtual mais larga e reduzir a página inteira.

Use limites para evitar extremos. Por exemplo, `width: min(100% - 2rem, 70rem); margin-inline: auto;` deixa uma margem em telas estreitas e limita linhas longas em telas amplas. `clamp(mínimo, valor preferido, máximo)` permite uma variação entre limites, mas não substitui teste de legibilidade; valores tipográficos não devem ficar pequenos demais nem crescer sem controle.

