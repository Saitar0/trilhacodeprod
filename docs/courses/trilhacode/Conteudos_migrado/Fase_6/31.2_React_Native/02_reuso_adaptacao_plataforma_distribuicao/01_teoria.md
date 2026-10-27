---
arquivo_id: "f6-31-2-02-reuso-adaptacao-plataforma-distribuicao-01-teoria-md"
parent_key: "31.2"
tipo_arquivo: "theory"
assunto: "02_reuso_adaptacao_plataforma_distribuicao"
ordem: 2
itens_origem: ["## Microtópico 2 — Compartilhe lógica e adapte o que depende da plataforma", "## Microtópico 3 — Entenda o papel do framework e da distribuição"]
---

## Microtópico 2 — Compartilhe lógica e adapte o que depende da plataforma
Código de domínio, validação e uma camada HTTP podem ser reutilizados quando não dependem de `window`, DOM, CSS ou bibliotecas específicas do navegador. Componentes web não se tornam componentes nativos por serem escritos em React; `div`, estilos CSS e APIs de browser precisam de alternativa ou adaptação.

Quando uma diferença é pequena, `Platform` permite escolher um valor ou implementação para iOS e Android. Quando a interface ou integração é substancialmente diferente, arquivos como `Componente.ios.tsx` e `Componente.android.tsx` podem separar as implementações mantendo uma API comum. Não crie bifurcações sem necessidade: compartilhe a parte que realmente tem comportamento igual e prove a compatibilidade em cada destino.

Acessibilidade, teclado, permissões e recursos nativos precisam ser avaliados no aparelho ou simulador apropriado. VoiceOver e TalkBack têm diferenças de plataforma, e um teste visual em navegador não garante que rótulos, foco ou gestos funcionem como esperado em um app nativo.

## Microtópico 3 — Entenda o papel do framework e da distribuição
Além da tela, um aplicativo móvel precisa de navegação, acesso a APIs nativas, build para iOS/Android e preparação para distribuição. O React Native recomenda começar com um framework como Expo para a maioria dos novos apps; usar React Native sem um framework continua possível quando há uma necessidade ou restrição específica. Expo é uma escolha do ecossistema, não um requisito para compreender o modelo de componentes.

Escolha ferramentas conforme o projeto e verifique quais recursos exigem módulos nativos, configuração de plataforma, permissões ou builds específicos. A lógica compartilhada pode reduzir duplicação, mas não elimina a necessidade de testar interação, aparência e integrações em iOS e Android.

