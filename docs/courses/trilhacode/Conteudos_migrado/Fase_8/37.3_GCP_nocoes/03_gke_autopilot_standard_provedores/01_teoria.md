---
arquivo_id: "f8-37-3-03-gke-autopilot-standard-provedores-01-teoria-md"
parent_key: "37.3"
tipo_arquivo: "theory"
assunto: "03_gke_autopilot_standard_provedores"
ordem: 3
itens_origem: ["### Microtópico 3 — Escolher GKE e comparar provedores pelo cenário"]
---

### Microtópico 3 — Escolher GKE e comparar provedores pelo cenário

O **Google Kubernetes Engine (GKE)** é Kubernetes gerenciado. O modo de operação muda o equilíbrio entre controle e trabalho operacional:

- **Autopilot:** GKE gerencia mais aspectos da infraestrutura, incluindo nós, escala e configurações recomendadas. Há restrições e convenções que podem não servir a workloads que exigem controle específico.
- **Standard:** a equipe controla mais configurações da infraestrutura, como node pools, e assume mais decisões de operação. Essa flexibilidade também traz responsabilidades.

GKE é comparável a EKS porque ambos oferecem Kubernetes gerenciado, mas uma carga não se torna portável sem revisão. Verifique versões e recursos Kubernetes usados, rede, identidade, storage, classes de nós, políticas de segurança, observabilidade, upgrade e integrações específicas de cada provedor.

Uma comparação útil parte dos requisitos e segue esta lista: **execução e escala; entrega e falhas; identidade e permissões; rede e armazenamento; operação e observabilidade; quotas e disponibilidade regional; custo para o padrão de uso**. Registre o que é equivalente no comportamento necessário e o que exigiria adaptação. Para esta unidade de repertório, não é preciso criar projeto GCP, ativar cobrança ou cadastrar cartão.

