---
arquivo_id: "f6-30-1-01-medicao-baseline-memoizacao-01-teoria-md"
parent_key: "30.1"
tipo_arquivo: "theory"
assunto: "01_medicao_baseline_memoizacao"
ordem: 1
itens_origem: ["## Microtópico 1 — Meça antes de escolher a técnica", "## Microtópico 2 — Use memoização só para trabalho repetido que importa"]
---

## Microtópico 1 — Meça antes de escolher a técnica
Otimização começa por uma experiência observável e uma medida. Uma página pode parecer lenta porque transfere JavaScript demais, bloqueia a thread principal, repete cálculos, monta milhares de elementos ou espera um serviço remoto. Cada causa pede uma intervenção diferente. `useMemo` não reduz o tamanho do bundle; virtualização não acelera o endpoint; dividir código não torna automaticamente uma interação já carregada mais rápida.

Defina o cenário antes de medir: mesma tela, dados, ação, navegador, tamanho de viewport, rede e condições do dispositivo. Registre o ambiente e faça várias execuções comparáveis. Escolha uma métrica que represente o gargalo — por exemplo, tempo de carregamento, tamanho transferido, duração da interação ou custo de renderização — e compare a mediana ou a faixa observada, não uma única execução favorável. Se o usuário final está em dispositivos modestos, avalie sob limitação de CPU ou rede realista.

Use as ferramentas adequadas à pergunta. React Profiler ajuda a investigar renders e duração de commits em uma árvore. O painel Performance do navegador revela tarefas longas, carregamento de recursos e trabalho após uma interação. Uma build de produção é mais representativa para bundle e execução final do que o servidor de desenvolvimento. Dados de laboratório ajudam a comparar mudanças controladas; dados de campo mostram a experiência agregada de usuários reais e variam por dispositivo e rede.

Antes de otimizar, confirme também o comportamento funcional e acessível. Uma queda no tempo pode esconder conteúdo que não aparece, foco perdido ou uma tela que só funciona com cache quente.

## Microtópico 2 — Use memoização só para trabalho repetido que importa
`React.memo` pode permitir que um componente reutilize o resultado anterior quando suas props não mudam; `useMemo` pode reutilizar o resultado de um cálculo; `useCallback` pode preservar a identidade de uma função entre renders. São otimizações, não requisitos de correção. O efeito depende de entradas estáveis e do custo que se quer evitar. Props criadas como novos objetos ou funções em toda renderização podem impedir o benefício esperado.

Meça a interação e localize o componente ou cálculo que realmente consome tempo. Depois aplique a menor mudança e compare. Declare todas as dependências reativas corretas; uma dependência omitida pode exibir dados antigos. Evite memoizar valores triviais sem motivo, pois isso adiciona código e complexidade de leitura. Se a aplicação usa React Compiler, ele pode automatizar memoizações em componentes compilados; confira se o compilador está ativo antes de adicionar otimizações manuais por hábito.

Se a aplicação deixa de funcionar sem `useMemo`, o problema provavelmente está em tratar o cache como fonte de verdade. O resultado precisa continuar correto quando o React recalcular o valor.

