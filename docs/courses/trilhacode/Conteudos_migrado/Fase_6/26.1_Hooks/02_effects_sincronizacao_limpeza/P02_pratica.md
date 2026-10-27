---
arquivo_id: "f6-26-1-02-effects-sincronizacao-limpeza-p02-pratica-md"
parent_key: "26.1"
tipo_arquivo: "practice"
assunto: "02_effects_sincronizacao_limpeza"
ordem: 2
itens_origem: ["P02"]
---

### Atividade 2 — Sincronize uma assinatura com limpeza

**Desafio:** um componente se inscreve em atualizações de uma sala e precisa trocar de assinatura quando roomId muda.

**Passos:**
1. Defina o que o setup cria e qual função libera a inscrição.
2. Escreva um Effect que lê roomId e registra a assinatura correta.
3. Retorne a limpeza que remove a assinatura correspondente ao valor usado no setup.
4. Descreva a sequência ao montar, trocar roomId e desmontar.
5. Simule em desenvolvimento setup → cleanup → setup e verifique que não ficam listeners duplicados.

**Dica:** a limpeza deve fechar sobre a assinatura criada naquele ciclo; não remova um listener diferente por engano.

