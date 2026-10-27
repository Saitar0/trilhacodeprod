---
arquivo_id: "f8-37-2-01-pods-deployments-services-probes-01-teoria-md"
parent_key: "37.2"
tipo_arquivo: "theory"
assunto: "01_pods_deployments_services_probes"
ordem: 1
itens_origem: ["## Teoria (bloco integral; fonte sem subtítulos de microtópico)"]
---


## Teoria
Um **Pod** é a menor unidade implantável do Kubernetes e pode conter um ou mais containers que compartilham rede e volumes. Pod é efêmero: pode ser substituído, ganhar outro IP ou terminar. Por isso, normalmente não se cria Pod isolado para manter aplicação.

Um **Deployment** descreve estado desejado de uma aplicação sem estado e mantém réplicas via ReplicaSet; alteração de template pode iniciar rollout e, se apropriado, rollback. Liveness probe verifica se deve reiniciar processo; readiness indica se deve receber tráfego. Probes mal calibradas podem causar reinícios/indisponibilidade. Um **Service** seleciona Pods por labels e oferece endereço estável e descoberta de serviço, mesmo quando Pods mudam. Tipos (ClusterIP, NodePort, LoadBalancer) definem alcance diferente; Ingress/Gateway acrescenta roteamento HTTP conforme controlador instalado.

Manifestos declarativos descrevem objeto desejado; `kubectl apply` pede ao control plane convergir, não executa comandos em sequência como script. ConfigMap guarda configuração não secreta; Secret representa dado sensível, mas seu uso ainda depende de RBAC, criptografia e gestão do cluster. Kubernetes automatiza scheduling e reconciliação, não resolve sozinho desenho da aplicação, backup ou segurança.

