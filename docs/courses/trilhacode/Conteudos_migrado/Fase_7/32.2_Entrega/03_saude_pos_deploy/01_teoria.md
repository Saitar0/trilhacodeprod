---
arquivo_id: "f7-32-2-03-saude-pos-deploy-01-teoria-md"
parent_key: "32.2"
tipo_arquivo: "theory"
assunto: "03_saude_pos_deploy"
ordem: 3
itens_origem: ["### Microtópico 3 — Verifique a saúde depois de publicar"]
---

### Microtópico 3 — Verifique a saúde depois de publicar

Deploy concluído significa que a ferramenta terminou a operação; ainda é preciso confirmar que a aplicação iniciou e atende às condições esperadas. Um **health check** pode verificar disponibilidade básica e dependências críticas. Um **smoke check** percorre uma capacidade mínima importante, por exemplo abrir uma rota e consultar um endpoint essencial. Eles precisam ter timeout, critério de sucesso claro e falha visível no pipeline.

Não use apenas uma resposta HTTP 200 genérica se ela não valida a função necessária. Tampouco transforme um teste extenso e instável em gate de deploy sem entender o sinal que ele fornece. Registre URL/rota, timeout, tentativas, versão testada e resultado. Se o check falha, interrompa a promoção e decida se a versão deve ser corrigida ou revertida.

Uma promoção controlada pode seguir: construir e testar → guardar artefato → implantar em staging → executar health/smoke checks → revisar evidências → promover o mesmo artefato. Em produção, limites de tráfego, rollout gradual, janela e observabilidade dependem da plataforma e do risco. A unidade demonstra o fluxo em staging; não exige experimentar em produção.

