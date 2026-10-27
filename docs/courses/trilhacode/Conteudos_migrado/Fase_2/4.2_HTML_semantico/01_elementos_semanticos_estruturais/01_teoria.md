---
arquivo_id: "f2-4-2-01-elementos-semanticos-estruturais-01-teoria"
parent_key: "4.2"
tipo_arquivo: "theory"
assunto: "01_elementos_semanticos_estruturais"
ordem: 1
itens_origem: ["Significado além da aparência", "Elementos estruturais comuns", "Exemplo de estrutura"]
---

## Teoria

### Significado além da aparência
HTML semântico usa elementos que comunicam a função do conteúdo a navegadores, tecnologias assistivas, mecanismos de busca e outras ferramentas. Uma `<div>` é um contêiner genérico; ela pode agrupar conteúdo quando não há um elemento mais específico apropriado. Não escolha elementos apenas pelo estilo visual que o navegador aplica por padrão — CSS controla apresentação, HTML expressa estrutura e significado.

### Elementos estruturais comuns
- `<header>` reúne conteúdo introdutório de uma página ou seção, como título e elementos de apoio.
- `<nav>` agrupa navegação principal ou relevante.
- `<main>` identifica o conteúdo principal da página; normalmente há um `main` principal visível.
- `<section>` agrupa conteúdo temático, geralmente identificado por um título.
- `<article>` representa conteúdo independente ou que pode fazer sentido por si, como uma publicação.
- `<aside>` contém informação complementar relacionada ao conteúdo ao redor.
- `<footer>` reúne informações de encerramento da página ou seção, como autoria ou links auxiliares.

Esses elementos podem ser aninhados conforme a estrutura real. O nome do elemento não substitui uma hierarquia de títulos clara. Uma seção não é automaticamente necessária para todo grupo visual e um `article` não é apenas um cartão com borda.

### Exemplo de estrutura

```html
<header><h1>Diário de viagens</h1></header>
<nav aria-label="Navegação principal">
  <a href="/">Início</a>
  <a href="/destinos">Destinos</a>
</nav>
<main>
  <article>
    <header><h2>Uma semana em Recife</h2></header>
    <p>Relato da viagem...</p>
    <aside><p>Melhor época: consulte a previsão local.</p></aside>
  </article>
</main>
<footer><p>© Diário de viagens</p></footer>
```

O exemplo é uma possibilidade, não um molde universal. Escolha a estrutura que descreve o conteúdo que existe.

