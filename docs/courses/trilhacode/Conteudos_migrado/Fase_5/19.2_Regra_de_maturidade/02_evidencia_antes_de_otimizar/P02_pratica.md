---
arquivo_id: "f5-19-2-02-evidencia-antes-de-otimizar-p02-pratica"
parent_key: "19.2"
tipo_arquivo: "practice"
assunto: "02_evidencia_antes_de_otimizar"
ordem: 2
itens_origem: ["P2"]
---

### Atividade 2 — Diagnóstico antes da otimização
**Objetivo:** usar evidências para escolher se e como mudar uma leitura existente.

**Passos:**
1. Rode uma consulta do projeto com conjunto de dados conhecido e registre ambiente e condições.
2. Inspecione SQL emitido, parâmetros sem valores sensíveis, número de consultas e volume de dados retornado.
3. Se o banco for PostgreSQL, examine EXPLAIN; use EXPLAIN ANALYZE somente sabendo que a instrução será executada.
4. Formule uma hipótese concreta e implemente uma alternativa pequena, como reduzir projeção, corrigir N+1 ou ajustar a consulta.
5. Compare correção funcional e medições nas mesmas condições; anote o que a comparação não permite concluir.

**Dica:** não use dados de produção ou comandos mutáveis em EXPLAIN ANALYZE sem ambiente e procedimento apropriados.

