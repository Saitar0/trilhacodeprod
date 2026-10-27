---
arquivo_id: "f5-19-1-02-consultas-relacoes-custo-p02-pratica"
parent_key: "19.1"
tipo_arquivo: "practice"
assunto: "02_consultas_relacoes_custo"
ordem: 2
itens_origem: ["P2"]
---

### Atividade 2 — Diagnóstico de N+1 e projeção
**Objetivo:** detectar custo de leitura e escolher uma estratégia relacional fundamentada em evidências.

**Passos:**
1. Implemente uma leitura de uma lista de registros e seus dados relacionados, usando ao menos 20 registros de exemplo.
2. Registre quantidade e formato das consultas emitidas pelo ORM.
3. Identifique se as consultas crescem com a quantidade de registros.
4. Ajuste a leitura para evitar consultas repetidas e selecione apenas campos necessários.
5. Compare o resultado, número de consultas e volume retornado antes/depois; registre limitações da estratégia escolhida.

**Dica:** não assuma que a opção de carregar relações funciona igual em todos os ORMs. Confira documentação da versão e SQL efetivamente emitido.

