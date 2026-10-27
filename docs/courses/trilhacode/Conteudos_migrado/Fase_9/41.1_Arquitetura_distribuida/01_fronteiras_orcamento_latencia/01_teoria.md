---
arquivo_id: "f9-41-1-01-fronteiras-orcamento-latencia-01-teoria"
parent_key: "41.1"
tipo_arquivo: "theory"
assunto: "01_fronteiras_orcamento_latencia"
ordem: 1
itens_origem: ["### 1. Fronteiras de serviço e orçamento de latência"]
---


### 1. Fronteiras de serviço e orçamento de latência
Uma chamada síncrona aguarda a resposta remota para continuar. Isso simplifica o fluxo quando o usuário precisa do resultado imediato, mas acopla latência e disponibilidade: se A chama B e B chama C, atrasos e falhas atravessam a cadeia. Antes de separar um componente, pergunte se deploy, escala, dados ou propriedade da equipe precisam mesmo ser independentes; um módulo dentro da mesma aplicação pode ser mais simples.

Defina um **deadline** para a operação completa e distribua esse orçamento entre chamadas. Exemplo: se a API deve responder em até 2 s e precisa chamar dois serviços em sequência, não configure 2 s para cada chamada. Reserve tempo para processamento, rede e resposta ao cliente. O timeout encerra a espera local; não prova que o serviço remoto deixou de executar. Uma chamada que expirou pode ter sido concluída do outro lado.

Comunicação assíncrona permite aceitar uma solicitação e continuar o trabalho depois, desacoplando disponibilidade imediata e absorvendo picos. Em troca, a resposta pode ser “recebido/em processamento”, o estado converge depois e a equipe precisa tratar duplicatas, ordenação, mensagens presas, rastreamento e recuperação.

**Checagem:** após timeout de uma cobrança, que evidência permite saber se ela ocorreu? Sem uma consulta por identificador idempotente ou estado durável do processo, o cliente não deve presumir que falhou.

