---
arquivo_id: "f6-28-3-90-integracao-p02-pratica-md"
parent_key: "28.3"
tipo_arquivo: "practice"
assuntos: ["01_consumidores_dono_elevacao", "02_estado_derivado_sem_redundancia"]
ordem: 2
itens_origem: ["P02"]
---

### Atividade 2 — Refatore estado duplicado e coordene componentes
**Objetivo:** simplificar uma interface sem perder sincronização nem apagar rascunhos indevidamente.

**Passos:**
1. Crie ou selecione uma tela com dois componentes que mantêm cópias de um filtro ou painel ativo, e um valor calculado armazenado separadamente.
2. Reproduza a inconsistência, por exemplo alterar os itens sem atualizar o total ou abrir os dois painéis ao mesmo tempo.
3. Escolha um proprietário comum para o estado sincronizado; passe valor e ações aos filhos ou use Context somente se a árvore justificar essa distribuição.
4. Substitua o valor derivado por um cálculo e guarde IDs em vez de objetos selecionados quando a coleção puder mudar.
5. Teste mudança de seleção, atualização da lista, navegação e retorno à tela; confirme explicitamente quais rascunhos devem ser preservados.

**Dica:** implemente primeiro a regra de propriedade e depois decida se a forma de passagem precisa mudar.

**Entrega:** refatoração funcional e uma nota curta explicando o proprietário e o ciclo de vida dos estados alterados.

**Critérios de conclusão:** consumidores permanecem sincronizados; não há valor derivado duplicado; seleção não aponta para um objeto antigo; comportamento de rascunho é intencional.

