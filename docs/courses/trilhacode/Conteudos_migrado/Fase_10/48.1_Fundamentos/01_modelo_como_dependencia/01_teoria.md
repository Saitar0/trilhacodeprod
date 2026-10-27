---
arquivo_id: "f10-48-1-t01"
parent_key: "48.1"
tipo_arquivo: "theory"
assunto: "01_modelo_como_dependencia"
ordem: 1
itens_origem: ["### 1. O modelo como dependência externa"]
---


### 1. O modelo como dependência externa
Um modelo generativo recebe uma solicitação e produz uma saída cuja forma e conteúdo podem variar. A aplicação não deve depender da ideia de que toda resposta será correta ou terá o formato esperado. O provedor é uma dependência externa: pode limitar requisições, responder lentamente, falhar, alterar versões disponíveis ou cobrar de acordo com a unidade tarifada. Comece pelo problema do produto e pela saída necessária; escolha a integração depois.

Separe o nome do modelo, o provedor e o serviço de nuvem. OpenAI e Anthropic oferecem APIs para seus modelos; Microsoft Foundry/Azure disponibiliza modelos e deployments conforme região, configuração e acesso; Vertex AI oferece modelos e controles integrados à plataforma Google Cloud. Catálogo, compatibilidade, limites, disponibilidade regional, privacidade, ciclo de vida e preço mudam. Nomes semelhantes ou um endpoint compatível não garantem comportamento ou recursos idênticos. Não memorize catálogos: confirme documentação e condições oficiais antes de implementar ou operar.

