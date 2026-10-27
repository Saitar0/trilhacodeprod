---
arquivo_id: "f6-28-2-04-mutacoes-conflitos-reconciliacao-01-teoria-md"
parent_key: "28.2"
tipo_arquivo: "theory"
assunto: "04_mutacoes_conflitos_reconciliacao"
ordem: 4
itens_origem: ["## Microtópico 4 — Reconcilie mutações, falhas e identidade do usuário"]
---

## Microtópico 4 — Reconcilie mutações, falhas e identidade do usuário
Depois de uma mutação bem-sucedida, escolha uma estratégia para manter as leituras coerentes:

1. **Invalidar e buscar novamente:** simples e robusto quando a resposta do servidor é a autoridade e o custo de uma nova leitura é aceitável.
2. **Atualizar o cache com a resposta da mutação:** evita uma busca quando a API devolve o registro atualizado completo e a chave do cache é conhecida.
3. **Atualizar otimisticamente:** mostra o resultado antes da confirmação do servidor. Exige guardar o valor anterior ou uma ação de rollback, tratar falha e considerar atualizações simultâneas ou buscas que poderiam sobrescrever a previsão.

Prefira a estratégia mais simples que atenda à experiência. Uma atualização otimista não é apenas “mudar o cache antes”: é preciso prever como desfazer a mudança e reconciliar o estado final. Se o rollback de uma lista inteira puder apagar uma alteração concorrente mais nova, limite o escopo da atualização, use identificadores e considere invalidar e buscar novamente ao final.

Se a mutação falhar, comunique o resultado sem apagar o rascunho da pessoa quando for seguro preservá-lo. O erro do cliente não prova sempre que o servidor não aplicou a ação; uma queda durante a resposta pode deixar o resultado incerto. Operações de escrita precisam de contrato de repetição e resolução de ambiguidade apropriados.

Ao encerrar sessão ou trocar de conta, trate dados em cache ligados à identidade anterior. Remova ou isole esses dados conforme o modelo de sessão para que outra pessoa usando o mesmo navegador não veja conteúdo anterior. A proteção real continua no servidor: ocultar um botão ou limpar a interface não substitui autenticação e autorização por recurso.

