---
arquivo_id: "f8-37-1-01-ecs-eks-modelos-responsabilidades-01-teoria-md"
parent_key: "37.1"
tipo_arquivo: "theory"
assunto: "01_ecs_eks_modelos_responsabilidades"
ordem: 1
itens_origem: ["## Teoria (bloco integral; fonte sem subtítulos de microtópico)"]
---


## Teoria
Amazon ECS é orquestrador gerenciado de containers integrado à AWS. Define task definition, cluster, task e service; capacidade pode usar EC2, Fargate e outras opções suportadas. O time ainda desenha rede, IAM, health checks, implantação, autoscaling, observabilidade e custos.

Amazon EKS oferece Kubernetes gerenciado. AWS gerencia o control plane e integração; a operação de nodes/capacidade, add-ons, políticas Kubernetes e upgrades depende do modo escolhido. ECS tende a seguir modelo AWS e requer menos conceitos Kubernetes. EKS oferece compatibilidade com APIs e ecossistema Kubernetes, mas a flexibilidade pode trazer complexidade de cluster, rede, permissões e custos. “Gerenciado” descreve uma divisão de responsabilidades, não ausência de operação.

Escolha olhando requisitos e competência da equipe: portabilidade/ecossistema, integração AWS, governança, workload, custo fixo/variável, disponibilidade de habilidades e esforço de atualização. A comparação deve usar o mesmo workload e contabilizar cluster/control plane, compute, rede, logs e suporte. Fargate reduz gestão de nós, mas preço e limitações precisam ser comparados por uso e modalidade vigentes.

