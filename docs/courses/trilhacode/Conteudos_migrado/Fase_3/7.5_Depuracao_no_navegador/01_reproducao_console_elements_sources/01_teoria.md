---
arquivo_id: "f3-7-5-01-reproducao-console-elements-sources-01-teoria"
parent_key: "7.5"
tipo_arquivo: "theory"
assunto: "01_reproducao_console_elements_sources"
ordem: 1
itens_origem: ["1. Reproduzir e formular uma hipótese", "2. Console e Elements: mensagens, DOM e estado visível", "3. Sources: breakpoint, escopo e pilha de chamadas"]
---

## Teoria

### 1. Reproduzir e formular uma hipótese
Comece reproduzindo o problema com passos consistentes e anotando o resultado esperado e o observado. Formule uma hipótese verificável, como “o handler recebe uma string vazia” ou “a API respondeu com status 404”. Mude uma coisa por vez e repita o mesmo cenário para confirmar se a correção resolveu o sintoma.

**Evidência** é algo observável; **hipótese** é uma explicação possível para essa evidência. Uma mensagem ajuda a localizar a investigação, mas não prova sozinha a causa raiz.

**Erro comum:** fazer várias alterações antes de reproduzir de novo. Sem repetir o cenário, fica difícil saber qual mudança corrigiu o comportamento.

### 2. Console e Elements: mensagens, DOM e estado visível
O **Console** mostra logs, avisos e erros e permite avaliar expressões no contexto disponível. Leia o tipo da mensagem, o arquivo e a linha indicados. Um stack trace lista chamadas relacionadas ao erro; procure o primeiro frame do seu código e reconstrua como o fluxo chegou até ele.

**Elements** permite inspecionar o DOM atual e os estilos calculados. Compare o elemento real com o que o seletor espera: um seletor sem correspondência retorna `null`; tentar registrar um evento nesse valor produz um erro. Confirme IDs, classes, hierarquia e mudanças da interação.

**Erro comum:** editar o DOM pelo painel Elements e achar que corrigiu o código-fonte. A edição serve para investigar o estado atual; recarregar a página descarta mudanças temporárias.

### 3. Sources: breakpoint, escopo e pilha de chamadas
**Sources** é o painel de depuração de JavaScript. Um breakpoint pausa a execução na linha marcada. Durante a pausa, inspecione variáveis locais e valores em Scope ou Console, veja a linha atual e a pilha de chamadas (Call Stack). Use **Step over** para executar uma chamada sem entrar nela, **Step into** para acompanhar uma função relevante e **Step out** para terminar a função atual e voltar ao chamador.

Compare o valor que entra numa linha com o valor esperado. Para um handler de formulário, siga o evento desde a ação da pessoa até a leitura do campo e a atualização da página. Sourcemaps, quando disponíveis, relacionam código gerado ao fonte original; sem eles, arquivos compactados podem dificultar a leitura.

**Erro comum:** avançar linha a linha sem uma pergunta de depuração. Escolha antes qual valor ou transição sua hipótese prevê; no breakpoint, compare previsão e evidência.

