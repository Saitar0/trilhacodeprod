---
arquivo_id: "f8-37-3-90-integracao-p01-pratica-md"
parent_key: "37.3"
tipo_arquivo: "practice"
assuntos: ["01_modelos_de_execucao_cloud_run", "02_pubsub_entrega_idempotencia", "03_gke_autopilot_standard_provedores"]
ordem: 1
itens_origem: ["P01"]
---

### Atividade 1 — Mapeamento por cenário
Para cada cenário, escolha uma opção inicial no GCP e registre uma possível referência AWS. Justifique a escolha e descreva **dois limites da comparação**.

1. Uma API HTTP sem estado que pode escalar conforme as requisições.
2. Um evento precisa ser publicado e processado por dois consumidores independentes.
3. Uma aplicação já usa manifests e recursos Kubernetes e depende de controle detalhado dos nós.

**Entrega:** tabela com cenário, opção GCP, comparação AWS aproximada, dois limites e uma pergunta que precisa ser respondida antes de produção.

**Critérios de aceite:** as escolhas correspondem ao tipo de workload; referências AWS são chamadas de aproximações; cada linha aponta dois limites concretos (por exemplo, contrato de execução, entrega, identidade, rede, operação ou cobrança).

**Feedback esperado:** se a resposta disser apenas “Cloud Run = Fargate” ou “Pub/Sub = SQS”, revise: identifique o fluxo completo e os comportamentos ainda não comparados.

