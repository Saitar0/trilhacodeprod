---
arquivo_id: "f9-42-1-90-integracao-kp01-feedback-pratica"
parent_key: "42.1"
tipo_arquivo: "answer_key_pratica"
assuntos: ["02_ciclo_url_modelo", "03_drf_serializacao_views_acesso"]
ordem: 1
itens_origem: ["P01"]
---


**Feedback de referência:** router resolve o caminho; viewset executa `list`; queryset escolhe registros; serializer prepara a representação; DRF constrói a resposta. Uma analogia razoável é router/controller/ORM/schema, mas convenções e ciclo exato variam por framework.

**Erro comum:** atribuir ao serializer o trabalho de escolher quais linhas o usuário pode consultar.

