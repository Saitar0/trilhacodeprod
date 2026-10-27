---
arquivo_id: "f5-22-1-01-modulos-grafo-e-composicao-03-gabarito-quiz"
parent_key: "22.1"
tipo_arquivo: "answer_key"
assunto: "01_modulos_grafo_e_composicao"
ordem: 1
itens_origem: ["Q1", "Q2", "Q4"]
---

**Resposta:** controller declara/adapta endpoints HTTP; provider é uma dependência que o container pode fornecer, como serviço, repositório ou factory.

**Resposta:** OrdersModule registra e exporta OrdersService; BillingModule importa OrdersModule. Evite registrar uma cópia do mesmo provider no módulo consumidor.

**Resposta:** verificar se a dependência circular aponta para responsabilidades ou fronteiras mal definidas e se uma dependência comum pode ser extraída ou redirecionada. forwardRef é um recurso do framework para ciclos inevitáveis, não o primeiro conserto.

