---
arquivo_id: "f6-28-2-04-mutacoes-conflitos-reconciliacao-p03-pratica-md"
parent_key: "28.2"
tipo_arquivo: "practice"
assunto: "04_mutacoes_conflitos_reconciliacao"
ordem: 3
itens_origem: ["P03"]
---

### Atividade 3 — Implemente uma mutação com reconciliação
**Objetivo:** manter detalhe e lista coerentes após edição e falha.

**Passos:**
1. Implemente uma edição de item com rascunho de formulário local e uma resposta previsível de sucesso ou erro.
2. Escolha entre invalidar as consultas relacionadas e atualizar o cache com a resposta do servidor; documente o motivo.
3. Se implementar atualização otimista, salve informação suficiente para desfazer a previsão, impeça que uma busca antiga sobrescreva a alteração e descreva como tratar mutações concorrentes.
4. Simule sucesso, erro de validação, falha de rede após envio e duas atualizações próximas; observe mensagem, rascunho, detalhe e lista em cada caso.
5. Faça logout e entrada com outra conta de teste; confirme que dados privados da sessão anterior não aparecem e que a API continua verificando autorização.

**Dica:** se a atualização otimista não for necessária para a experiência, invalidar e aceitar o estado confirmado pelo servidor é uma solução válida e mais simples.

**Entrega:** fluxo de edição, estratégia de cache documentada e registro dos cenários de sucesso, falha e troca de sessão.

**Critérios de conclusão:** lista e detalhe convergem ao mesmo estado; falha não elimina entrada útil; rollback não descarta atualização concorrente conhecida; dados de outra sessão não ficam visíveis.

