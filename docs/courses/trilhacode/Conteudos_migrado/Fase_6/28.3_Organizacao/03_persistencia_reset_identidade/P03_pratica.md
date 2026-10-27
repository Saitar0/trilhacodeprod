---
arquivo_id: "f6-28-3-03-persistencia-reset-identidade-p03-pratica-md"
parent_key: "28.3"
tipo_arquivo: "practice"
assunto: "03_persistencia_reset_identidade"
ordem: 3
itens_origem: ["P03"]
---

### Atividade 3 — Defina limites de persistência e redefinição
**Objetivo:** especificar o que sobrevive a navegação, troca de registro, recarga e logout.

**Passos:**
1. Para uma tela de edição, escolha três valores: filtro, preferência visual e rascunho não salvo.
2. Preencha uma matriz indicando se cada valor deve sobreviver à troca de componente, rota, recarga, abertura em outra aba e logout.
3. Escolha memória, URL, armazenamento local ou servidor para cada requisito, justificando privacidade, compartilhamento e tempo de vida.
4. Implemente uma troca de registro que preserve ou redefina o formulário conforme a decisão e deixe visível quando há alterações não salvas.
5. Verifique que logout não deixa informação privada exposta e documente como limpar ou invalidar os dados persistidos.

**Dica:** persistência e compartilhamento são requisitos distintos: algo pode sobreviver à recarga sem precisar aparecer em um link.

**Entrega:** matriz de ciclo de vida, implementação de um caso de redefinição e justificativa de persistência.

**Critérios de conclusão:** cada transição tem comportamento definido; rascunhos não desaparecem inesperadamente; dados privados não persistem sem política explícita.

