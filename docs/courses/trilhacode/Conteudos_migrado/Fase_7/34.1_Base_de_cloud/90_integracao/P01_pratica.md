---
arquivo_id: "f7-34-1-90-integracao-p01-pratica-md"
parent_key: "34.1"
tipo_arquivo: "practice"
assuntos: ["02_vpc_subnets_rotas_security_groups", "03_dns_tls_caminho_requisicao"]
ordem: 1
itens_origem: ["P01"]
---

### Atividade 1 — Desenhe a rede e rastreie uma requisição

**Desafio:** proponha uma arquitetura mínima para uma aplicação web em AWS e explique o caminho de uma requisição.

**Passos:**
1. Desenhe VPC, blocos CIDR, duas zonas, subnets públicas/privadas, rotas, Internet Gateway e NAT apenas se necessário.
2. Coloque load balancer e aplicação nos locais apropriados; coloque RDS privado e indique se a aplicação realmente precisa de saída pela internet.
3. Trace DNS → TLS → load balancer → aplicação → banco; marque onde TLS termina e que conexão interna é protegida.
4. Defina regras de security group por origem, destino, protocolo/porta e razão. Não use portas administrativas abertas globalmente.
5. Explique o que aconteceria se cada rota ou regra essencial fosse removida e quais componentes seriam públicos.

**Evidências:** diagrama legível; tabela de rotas e regras; narrativa do fluxo; simplificações e limites de resiliência.

**Verificação:** confira que uma subnet pública tem rota apropriada, que o banco não recebe acesso direto da internet e que DNS/TLS não foram confundidos com autorização.

**Aceite:** fluxo de ponta a ponta está completo; cada regra tem origem/porta justificadas; superfície pública e limites do laboratório são explícitos.

