---
arquivo_id: "f5-19-2-02-evidencia-antes-de-otimizar-01-teoria"
parent_key: "19.2"
tipo_arquivo: "theory"
assunto: "02_evidencia_antes_de_otimizar"
ordem: 2
itens_origem: ["Microtópico 3 — Exija evidência antes de otimizar"]
---

## Microtópico 3 — Exija evidência antes de otimizar
Quando houver problema de desempenho, reproduza-o com dados representativos e compare a mesma operação. Colete SQL emitido, parâmetros sem expor dados sensíveis, quantidade de consultas, linhas e campos retornados, latência e plano de execução do banco. No PostgreSQL, EXPLAIN mostra estimativas do plano; EXPLAIN ANALYZE executa a consulta e inclui medições reais, portanto deve ser usado com atenção em comandos que alteram dados.

Compare hipóteses verificáveis: projeção menor, índice adequado, estratégia de relação, paginação, query builder ou SQL explícito. Registre ambiente, conjunto de dados e limites da medição. Uma melhoria observada em um banco e volume não é prova universal de que a solução será mais rápida em qualquer cenário.

**Exemplo:** se uma consulta ORM está lenta, primeiro verifique se o gargalo é N+1, volume excessivo, plano inadequado ou contenção. Só então compare uma reescrita; confira que ela continua retornando os mesmos resultados e respeita as invariantes.

**Erro comum:** usar somente o tempo de uma execução local como benchmark. Cache, concorrência, estado do banco e volume alteram o resultado.

**Checagem:** que evidência sustenta a troca? Um caso reproduzível, uma métrica comparável e confirmação de correção funcional.

