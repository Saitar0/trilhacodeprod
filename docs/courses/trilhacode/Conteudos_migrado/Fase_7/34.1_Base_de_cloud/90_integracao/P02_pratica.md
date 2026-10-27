---
arquivo_id: "f7-34-1-90-integracao-p02-pratica-md"
parent_key: "34.1"
tipo_arquivo: "practice"
assuntos: ["01_conta_iam_responsabilidade", "02_vpc_subnets_rotas_security_groups"]
ordem: 2
itens_origem: ["P02"]
---

### Atividade 2 — Defina acesso e responsabilidades

**Desafio:** dê à aplicação acesso mínimo ao storage e ao banco e identifique as responsabilidades de operação.

**Passos:**
1. Crie um mapa principal → identidade → ações → recursos; diferencie pessoa administradora, aplicação e serviço AWS.
2. Descreva uma role de aplicação com trust policy adequada e permissões limitadas a um bucket/prefixo e às operações estritamente necessárias.
3. Registre como a aplicação acessa RDS e quais grupos de segurança permitem a conexão. Nenhuma credencial estática vai para o repositório ou código cliente.
4. Para EC2, S3 e RDS, liste duas tarefas da AWS e duas tarefas da pessoa cliente, escolhidas conforme o modelo compartilhado.
5. Sem uma conta de laboratório, produza policy conceitual e matriz de responsabilidade; não provisionar é um resultado válido.

**Evidências:** matriz de identidades/policies; caminho de conexão ao banco; lista compartilhada de responsabilidades; captura sanitizada ou diagrama, se recurso foi criado.

**Verificação:** valide que acesso ao bucket é privado por padrão, cada identidade tem apenas ações requeridas e nenhuma rota pública ao banco foi introduzida.

**Aceite:** confiança e autorização são distintas; role substitui chave estática para o workload quando compatível; responsabilidades por serviço e rede são precisas.

