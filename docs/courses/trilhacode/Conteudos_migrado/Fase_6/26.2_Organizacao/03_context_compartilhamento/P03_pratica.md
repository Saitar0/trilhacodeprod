---
arquivo_id: "f6-26-2-03-context-compartilhamento-p03-pratica-md"
parent_key: "26.2"
tipo_arquivo: "practice"
assunto: "03_context_compartilhamento"
ordem: 3
itens_origem: ["P03"]
---

### Atividade 3 — Decida entre props, composição e Context

**Desafio:** avalie três cenários: um aviso usado só dentro de uma tela; um tema lido em muitos componentes profundos; e uma prop de título encaminhada por quatro wrappers que não a utilizam.

**Passos:**
1. Para cada cenário, identifique produtores e consumidores e quantos níveis atravessa.
2. Escolha props, estado elevado, children/slots ou Context.
3. Selecione um Context para implementar com createContext, provider e useContext.
4. Separe Contexts quando valores têm consumidores ou frequências de mudança claramente distintas; explique o custo de fazê-lo.
5. Descreva como verificaria se a organização melhorou clareza sem criar complexidade desnecessária.

**Dica:** não mova o aviso de uma tela para uma store global. Para o título atravessando wrappers, composição pode remover a necessidade de encaminhá-lo.

