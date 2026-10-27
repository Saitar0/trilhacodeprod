---
arquivo_id: "f5-19-2-03-fronteira-seguranca-contrato-p03-pratica"
parent_key: "19.2"
tipo_arquivo: "practice"
assunto: "03_fronteira_seguranca_contrato"
ordem: 3
itens_origem: ["P3"]
---

### Atividade 3 — Exceção de persistência sustentável
**Objetivo:** criar uma consulta especializada sem espalhar fragilidade pelo projeto.

**Passos:**
1. Identifique uma consulta que a API escolhida não expressa bem ou um recurso específico que o projeto realmente exige.
2. Encapsule-a no módulo de acesso a dados com parâmetros vinculados e retorno/contrato explícitos.
3. Se a escolha for ORM ou query builder em vez de SQL, registre por que essa abstração é suficiente.
4. Adicione verificações para resultado típico, ausência de resultados e regra de integridade relevante.
5. Documente premissas, decisão, custo de manutenção e como perceber uma regressão.

**Dica:** não crie uma exceção apenas para cumprir a atividade; se não houver caso real, use um exemplo controlado e marque-o como demonstrativo.

