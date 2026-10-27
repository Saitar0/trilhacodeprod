---
arquivo_id: "f6-30-2-03-tradeoffs-regressoes-01-teoria-md"
parent_key: "30.2"
tipo_arquivo: "theory"
assunto: "03_tradeoffs_regressoes"
ordem: 3
itens_origem: ["## Microtópico 3 — Avalie benefícios junto aos custos e às regressões"]
---

## Microtópico 3 — Avalie benefícios junto aos custos e às regressões
Uma otimização tem custo: código mais difícil de entender, dependências, estados de carregamento, medições imprecisas ou casos adicionais de acessibilidade. Decida com base no ganho percebido e no comportamento completo, não só numa métrica isolada. Carregar um módulo sob demanda pode reduzir transferência inicial, mas atrasar a abertura do recurso. Virtualizar uma lista pode reduzir elementos no DOM, mas afetar foco, busca e navegação com leitor de tela. Memoização pode reduzir recálculo, mas exigir dependências e identidades estáveis.

Defina critérios antes de executar a mudança: qual métrica precisa melhorar, qual regressão seria inaceitável e quanto ganho mínimo tornaria a complexidade razoável para o produto? Os valores dependem da tarefa e do público; não copie um limite sem entender o que ele representa. Verifique também correção, acessibilidade, confiabilidade e resultados de testes.

Se o gargalo desaparece, o problema funcional continua, ou uma otimização adiciona efeitos colaterais sem ganho repetível, reverta ou não a adote. Manter a solução simples é uma decisão técnica válida quando a evidência não sustenta a complexidade extra.

