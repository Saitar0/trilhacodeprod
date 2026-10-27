---
arquivo_id: "f6-31-2-01-modelo-react-renderizador-nativo-01-teoria-md"
parent_key: "31.2"
tipo_arquivo: "theory"
assunto: "01_modelo_react_renderizador_nativo"
ordem: 1
itens_origem: ["## Microtópico 1 — Reutilize o modelo React, não o renderizador HTML"]
---

## Microtópico 1 — Reutilize o modelo React, não o renderizador HTML
React Native compartilha o modelo declarativo do React: componentes, props, estado, composição e hooks continuam úteis. O que muda é a forma de desenhar a interface. Em vez de elementos HTML do DOM, use componentes fundamentais como `View`, `Text`, `TextInput`, `Pressable`, `Image` e listas nativas como `FlatList`. Texto precisa estar dentro de `Text`; uma `View` não funciona como um `div` que aceita texto solto.

Estilo é escrito em objetos JavaScript, com propriedades como `backgroundColor` em camelCase. Há conceitos familiares do CSS, como Flexbox, mas o conjunto de propriedades e alguns comportamentos diferem. Também mudam teclado, toque, rolagem, áreas seguras da tela e integração com recursos do aparelho. Uma tela pode compartilhar a regra de negócio, mas seu layout precisa ser desenhado e validado para os controles nativos.

