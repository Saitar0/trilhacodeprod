---
arquivo_id: "f9-40-3-01-modelar-problema-antes-escolha-01-teoria"
parent_key: "40.3"
tipo_arquivo: "theory"
assunto: "01_modelar_problema_antes_escolha"
ordem: 1
itens_origem: ["parágrafo introdutório de ## Teoria", "### 1. Modele o problema antes de escolher"]
---


Esta unidade consolida conceitos e experimentos de 33.1, 35.1, 37.3, 40.1 e 40.2. Nenhum produto é vencedor universal: descreva primeiro o comportamento necessário e só então escolha uma tecnologia. Características dependem do modo, configuração, versão, região e cliente; consulte a documentação oficial antes de uma decisão real.

### 1. Modele o problema antes de escolher
- **Fila de trabalho:** cada tarefa deve ser distribuída para processamento por um worker disponível; normalmente importa controlar concorrência, ack, retentativa e fila de falhas. RabbitMQ e SQS se encaixam naturalmente nesse modelo.
- **Log de eventos:** eventos ficam retidos e cada grupo de consumidores acompanha seu próprio progresso; replay e leitura independente são requisitos centrais. Kafka foi desenhado para esse modelo.
- **Publicação/assinatura gerenciada:** produtores publicam sem conhecer assinantes, e o serviço gerencia a distribuição; Pub/Sub oferece esse modelo como serviço gerenciado. Recursos de retenção e replay dependem da configuração e da assinatura.
- **Sobreposição não é equivalência:** RabbitMQ pode rotear para várias filas; Kafka pode distribuir eventos a muitos grupos; SQS pode integrar-se a padrões de fan-out; Pub/Sub separa tópico e assinatura. Compare o fluxo concreto, não apenas o rótulo.

Pergunta de checagem: o novo consumidor precisa receber só mensagens futuras, tarefas ainda não processadas ou todo o histórico retido? A resposta muda a arquitetura.

