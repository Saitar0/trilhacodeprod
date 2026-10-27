---
arquivo_id: "f4-12-1-01-hipoteses-planos-explain-medicao-01-teoria"
parent_key: "12.1"
tipo_arquivo: "theory"
assunto: "01_hipoteses_planos_explain_medicao"
ordem: 1
itens_origem: ["1. Comece por uma consulta e uma hipótese", "2. Leia o plano com EXPLAIN", "5. Compare evidências e comunique limites"]
---

## Teoria

### 1. Comece por uma consulta e uma hipótese
Otimize uma consulta observada e relevante, não uma coluna abstrata. Registre a consulta, os filtros, o tamanho e a distribuição dos dados, a latência percebida e o comportamento esperado. Uma boa hipótese é verificável: “o filtro por categoria lê muitas linhas; um índice adequado pode reduzir o trabalho nesta consulta”.

Compare a mesma consulta antes e depois, com os mesmos dados e condições de execução. Registre linhas estimadas e observadas, tipo de acesso, tempo e configuração relevante. Uma tabela pequena pode ser mais rápida com leitura sequencial, mesmo que exista índice. Não crie índices em toda coluna por hábito.

**Erro comum:** declarar sucesso porque um índice existe, sem confirmar se o plano o usa nem se a consulta melhorou.

### 2. Leia o plano com EXPLAIN
EXPLAIN apresenta o plano estimado pelo otimizador: nós de leitura, filtros, junções, ordenações e agregações, além de estimativas de custo e linhas. O custo é uma unidade interna para comparar planos, não milissegundos. Um Seq Scan percorre a tabela; Index Scan usa uma estrutura de índice para localizar linhas; Bitmap Scan combina posições de índice e acesso à tabela. Nenhum nó é ruim por si só: avalie-o no contexto da consulta e dos dados.

A estimativa de linhas importa. Grande diferença entre linhas estimadas e reais pode sugerir estatísticas desatualizadas, distribuição desigual ou uma condição difícil de estimar. O plano é uma árvore: observe os nós de baixo para cima para entender de onde vêm as linhas e como elas são transformadas.

EXPLAIN ANALYZE executa a consulta e informa observações reais de execução, incluindo tempos e linhas. Use em SELECT de estudo com dados representativos. Não execute EXPLAIN ANALYZE em UPDATE, DELETE ou outra operação com efeitos sem um ambiente controlado e uma estratégia explícita para seus efeitos.

**Erro comum:** ler o custo estimado como tempo real ou interpretar Seq Scan como prova automática de falta de índice.

### 5. Compare evidências e comunique limites
Uma comparação útil declara o que foi medido, em que ambiente e com quais dados. Registre consulta, índice, plano, linhas estimadas/reais e observações de tempo; repita a medição e evite comparações quando uma execução aproveitou cache que a outra não teve. Explique que caches, estatísticas, concorrência, armazenamento e volume alteram os resultados.

O plano ajuda a entender o trabalho do banco, mas o usuário percebe também transmissão e renderização do resultado. Retornar milhares de colunas ou linhas pode custar mesmo que a busca encontre registros rapidamente. Limite a projeção e o conjunto de resultados conforme a necessidade.

A conclusão deve ser proporcional à evidência: “neste conjunto e ambiente, o plano passou a usar o índice e as execuções repetidas ficaram menores” é mais defensável do que afirmar que o índice sempre acelera consultas.

**Checklist de investigação:**
- A consulta é relevante e representa uma necessidade real?
- O conjunto de dados representa o volume e a distribuição esperados?
- Comparei a mesma consulta antes e depois?
- Entendi estimativas, linhas observadas e nós do plano?
- O índice resolve o padrão de filtro/ordenação e vale o custo de escrita?
- O mecanismo de busca corresponde ao tipo de correspondência pedido?
- Registrei limitações e evitei generalizar uma única medição?

