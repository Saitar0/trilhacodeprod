---
arquivo_id: "f4-11-1-90-integracao-p02-pratica"
parent_key: "11.1"
tipo_arquivo: "practice"
assuntos: ["02_filtros_logica_booleana", "03_null_logica_trivalente"]
ordem: 2
itens_origem: ["P2"]
---

### Atividade 2 — Interprete NULL e lógica booleana
Considere estes registros:
- (1, status='pago', total=80)
- (2, status=NULL, total=150)
- (3, status='aberto', total=200)
- (4, status='pago', total=150)

Determine quais ids retornam em cada consulta:
A. `WHERE status = 'pago' AND total >= 100)
B. `WHERE status IS NULL OR total >= 200)
C. `WHERE status = NULL)

**Tarefas**
1. Mostre o resultado de cada filtro.
2. Explique por que a consulta C não encontra o registro 2.
3. Reescreva C corretamente.

**Dica:** WHERE mantém somente linhas cuja condição inteira é verdadeira; desconhecido não é verdadeiro.

