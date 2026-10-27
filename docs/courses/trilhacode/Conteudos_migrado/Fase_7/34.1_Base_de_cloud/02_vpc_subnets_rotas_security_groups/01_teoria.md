---
arquivo_id: "f7-34-1-02-vpc-subnets-rotas-security-groups-01-teoria-md"
parent_key: "34.1"
tipo_arquivo: "theory"
assunto: "02_vpc_subnets_rotas_security_groups"
ordem: 2
itens_origem: ["### Microtópico 2 — VPC, subnets, rotas e security groups"]
---

### Microtópico 2 — VPC, subnets, rotas e security groups

Uma VPC é uma rede virtual isolada logicamente numa região. **Subnets** ocupam blocos de endereços dentro de uma zona e se associam a route tables. Uma subnet é considerada pública quando a tabela de rotas associada aponta para um Internet Gateway; isso, por si só, não torna cada recurso acessível pela internet. Um recurso também precisa de endereçamento/rota aplicável, listener/serviço configurado e regras de rede que permitam o tráfego. Subnet privada não possui rota direta de entrada pela internet; uma rota por NAT Gateway pode permitir conexões iniciadas de dentro para fora, com custo adicional, sem abrir entrada direta.

Um **security group** é um firewall stateful associado a interfaces de rede: regras de entrada/saída permitem tráfego específico e respostas a conexões permitidas são tratadas pelo estado da conexão. Prefira referenciar o security group da aplicação no grupo do banco, limitando a origem à aplicação e a porta realmente necessária. Não abra SSH, banco ou painel administrativo a `0.0.0.0/0` por conveniência. Network ACLs e controles de aplicação são camadas diferentes; nenhum deles substitui autenticação e autorização.

Desenho típico de aplicação web: entrada pública recebe HTTPS num load balancer; aplicação roda em subnets privadas; banco fica em subnets privadas, sem acesso público; aplicação acessa banco por regra de origem e porta limitada. Se a arquitetura tiver apenas um servidor de laboratório, documente essa simplificação e não a trate como configuração de produção resiliente.

