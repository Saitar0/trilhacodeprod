---
arquivo_id: "f4-10-2-90-integracao-kp02-gabarito-pratica"
parent_key: "10.2"
tipo_arquivo: "answer_key_pratica"
assuntos: ["01_servicos_rede_portas", "02_dados_volumes_configuracao_segura"]
ordem: 2
itens_origem: ["P2"]
---

**Solução de referência:** declare serviço `documentdb) com imagem de MongoDB escolhida e volume em `/data/db), depois associe `profiles: ["document"]`. Sem ativar o perfil, o conjunto padrão não inicia o serviço; com `docker compose --profile document up), o serviço fica disponível na rede do projeto pelo nome `documentdb) e porta interna 27017. Se uma porta for necessária a um cliente no host, publique-a apenas na interface local. Para material introdutório, deixe explícito que exemplo sem autenticação é local e descartável; não o exponha na rede. `down) conserva o volume; `down --volumes) pode apagar os dados.

