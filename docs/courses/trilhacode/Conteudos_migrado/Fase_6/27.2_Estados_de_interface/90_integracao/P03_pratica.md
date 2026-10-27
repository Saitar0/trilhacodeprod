---
arquivo_id: "f6-27-2-90-integracao-p03-pratica-md"
parent_key: "27.2"
tipo_arquivo: "practice"
assuntos: ["01_estado_operacao_comunicacao_acessivel", "03_retry_seguro"]
ordem: 3
itens_origem: ["P03"]
---

### Atividade 3 — Defina retry e acessibilidade para estados de falha
**Objetivo:** apresentar recuperação segura, acessível e reproduzível.

**Passos:**
1. Escolha uma leitura `GET` e uma escrita que altera dados. Documente se cada uma pode ser repetida automaticamente e qual contrato sustenta a decisão.
2. Para a leitura, configure uma política limitada de tentativas e intervalo progressivo; inclua uma opção manual após a falha final.
3. Para a escrita, impeça duplicidade enquanto estiver pendente e documente como a aplicação verifica o resultado ou usa uma chave de idempotência fornecida pelo servidor.
4. Anuncie de forma concisa a mudança de estado da listagem sem mover o foco; torne ações operáveis por teclado e confira o comportamento com leitor de tela.
5. Simule resposta lenta, falha temporária, falha persistente e recuperação. Registre o número de tentativas, a mensagem exibida e a ação disponível em cada caso.

**Dica:** a implementação da chave de idempotência depende do suporte do servidor; enviar um cabeçalho desconhecido não cria a garantia por si só.

**Entrega:** política de retry documentada, estados acessíveis e registro dos quatro cenários simulados.

**Critérios de conclusão:** tentativas automáticas têm limite; escrita insegura não é repetida cegamente; anúncio é compreensível sem excesso; os cenários podem ser reproduzidos por outra pessoa.

