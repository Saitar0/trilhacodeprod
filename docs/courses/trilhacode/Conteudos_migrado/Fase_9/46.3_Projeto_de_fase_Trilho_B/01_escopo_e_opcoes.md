---
arquivo_id: "f9-46-3-01-escopo-e-opcoes"
parent_key: "46.3"
tipo_arquivo: "project_scope"
ordem: 0
itens_origem: ["Regras de escolha e escopo", "Tipos disponíveis na Fase 9"]
---


## Regras de escolha e escopo
Consulte a cobertura de tipos no [Guia de Projetos e Rotação](../../../Guia_Projetos_e_Rotacao_de_Tipos.md). Ofereça três ideias de tipos diferentes conforme as disponibilidades restantes e as regras do guia. Escolha um tipo ainda não concluído para obter crédito de cobertura; tipos repetidos permanecem opcionais e não contam novamente. Se T1–T5 já estiverem concluídos, faça aprofundamento livre sem declarar novo tipo coberto. Registre as opções mostradas, o tipo escolhido e o estado da cobertura antes/depois.

A versão da Fase 9 é autocontida: inclua uma base mínima com 2–4 tabelas PostgreSQL, migrations e API simples autenticada, além de aplicação, RabbitMQ, consumidor e Compose local. Implemente apenas uma fatia vertical que demonstre o problema difícil do tipo. Não é necessário publicar em nuvem nem entregar um produto completo. Use dados sintéticos, configuração de exemplo e segredos fora do repositório.

A mensagem precisa de identidade estável e contrato com versão e significado. Classifique erros transitórios e permanentes, limite tentativas, defina backoff, DLQ, retenção e procedimento de redrive. O consumidor deve tolerar redelivery e fazer o efeito idempotente. Publisher confirm, ack do consumidor e transação do banco cobrem fronteiras distintas; não descreva o fluxo como “exactly once” sem delimitar e provar o efeito dentro da fronteira escolhida. A fila só é justificável se o trabalho puder ser assíncrono; registre no ADR por que uma chamada síncrona ou processamento no mesmo serviço não atende tão bem ao caso.

## Tipos disponíveis na Fase 9
A implementação comum de fila e resiliência não substitui a demonstração específica abaixo. Escolha a linha correspondente ao tipo selecionado:

| Tipo | Regra técnica central a demonstrar | Evidência mínima da fatia |
|---|---|---|
| **T1 — Transacional: venda de ingressos** | Concorrência e repetição não vendem além do estoque nem repetem o pagamento simulado. | Dois pedidos concorrentes para o último ingresso; apenas um é confirmado. Redelivery com a mesma chave não duplica cobrança/baixa. |
| **T2 — SaaS multiempresa: agendamento** | Toda leitura, escrita e tarefa assíncrona preserva o limite do tenant e a autorização por papel. | Dois tenants com dados semelhantes; prova automatizada de que usuário e worker não acessam nem notificam o tenant alheio, inclusive na redelivery. |
| **T3 — Tempo real e colaboração** | A atualização chega a clientes conectados em instâncias diferentes, com comportamento de duplicação/ordem definido pelo requisito. | Dois clientes em duas instâncias recebem a atualização; o cenário de duplicata é idempotente e qualquer garantia de ordem fica explícita e testada. |
| **T4 — Conteúdo, feed e busca** | Uma projeção de leitura assíncrona converge após evento repetido ou falha. | Conteúdo alterado atualiza a projeção; evento duplicado não duplica resultado; demonstrar recuperação ou reconciliação após falha. |
| **T5 — Dados e processamento assíncrono** | Importação reprocessável não duplica registros nem contagens e permite identificar progresso/falha. | Reimportar o mesmo lote mantém resultado único; falha parcial pode ser retomada e os itens problemáticos são localizáveis. |

Se o guia mudar ou houver dúvida sobre cobertura, use a regra canônica do guia; não invente disponibilidade a partir desta tabela resumida.

