---
arquivo_id: "f6-28-2-90-integracao-p02-pratica-md"
parent_key: "28.2"
tipo_arquivo: "practice"
assuntos: ["02_identidade_de_consultas", "03_frescor_ciclo_de_cache"]
ordem: 2
itens_origem: ["P02"]
---

### Atividade 2 — Construa chaves e política de frescor
**Objetivo:** impedir colisões entre resultados e decidir como cada consulta envelhece.

**Passos:**
1. Modele consultas para detalhe de pedido, lista paginada por status e perfil da conta autenticada.
2. Proponha chaves serializáveis que incluam identificadores e parâmetros capazes de alterar cada resposta.
3. Identifique quais parâmetros são sensíveis e não devem aparecer na chave; use identificadores não secretos para distinguir escopos quando necessário.
4. Para cada consulta, defina o que significa dado fresco para o produto e qual custo haveria se a tela mostrasse dado antigo.
5. Registre quando a consulta pode revalidar, quando dados inativos podem ser coletados e como verificaria uma mudança de status, reconexão ou retorno à tela.

**Dica:** não copie um mesmo prazo de frescor para todos os recursos. Use a necessidade de atualização e o comportamento observado para justificá-lo.

**Entrega:** catálogo de query keys e tabela de políticas de frescor e revalidação.

**Critérios de conclusão:** parâmetros variáveis estão representados; as chaves não incluem segredos; frescor e coleta estão documentados como decisões distintas.

