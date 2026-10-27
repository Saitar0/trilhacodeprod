---
arquivo_id: "f5-20-2-03-csrf-e-segredos-p03-pratica"
parent_key: "20.2"
tipo_arquivo: "practice"
assunto: "03_csrf_e_segredos"
ordem: 3
itens_origem: ["P3"]
---

### Atividade 3 — CSRF e incidente de segredo simulado
**Objetivo:** proteger alterações autenticadas por cookie e praticar resposta a credencial exposta.

**Passos:**
1. Selecione uma rota que altera estado e recebe cookie; confirme que GET não provoca alteração.
2. Aplique a defesa CSRF recomendada pelo framework, com validação de origem/Fetch Metadata ou camada adicional pertinente.
3. Configure SameSite de acordo com o fluxo e registre por que não é a única defesa presumida.
4. Em um repositório local descartável, use um segredo fictício e simule que ele foi commitado.
5. Descreva a sequência de contenção: revogar/trocar, atualizar consumidores, revisar exposição e limpar cópias quando apropriado.

**Dica:** não use segredo verdadeiro nem faça teste em serviço compartilhado. Limpar o histórico é uma tarefa separada da revogação no emissor.

