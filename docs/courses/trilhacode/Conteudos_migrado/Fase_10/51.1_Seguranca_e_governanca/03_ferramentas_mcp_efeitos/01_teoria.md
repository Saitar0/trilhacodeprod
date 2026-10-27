---
arquivo_id: "f10-51-1-t03"
parent_key: "51.1"
tipo_arquivo: "theory"
assunto: "03_ferramentas_mcp_efeitos"
ordem: 3
itens_origem: ["### 3. Limitar ferramentas, MCP e efeitos"]
---


### 3. Limitar ferramentas, MCP e efeitos
Cada ferramenta deve fazer uma operação de domínio estreita, com autenticação, autorização, validação, limites e identidade auditável no servidor. Use privilégios mínimos também nas credenciais do serviço downstream. Não exponha funções genéricas como executar código/SQL ou buscar qualquer URL sem sandbox, allowlist e necessidade comprovada. Para ações de alto impacto, peça aprovação humana vinculada à ação exata, mostre os dados relevantes, use idempotência e ofereça caminho de reversão quando possível.

Model Context Protocol (MCP) define uma forma padronizada de comunicação entre hosts, clientes e servidores que oferecem contexto ou ferramentas. O protocolo não atesta a identidade, segurança ou confiabilidade de um servidor. Revise origem, comando de inicialização, rede, dados, ferramentas, autenticação, escopos, dependências e atualizações de cada servidor. Em clientes ou proxies remotos, avalie riscos como confused deputy, encaminhamento indevido de tokens, SSRF e acesso a recursos locais. Autorize apenas capacidades necessárias e registre consentimento e responsável pela integração.

Guardrails podem filtrar conteúdo, impor formato ou interromper classes conhecidas de ação, mas têm falsos positivos, falsos negativos e caminhos de bypass. Teste-os como uma camada; nunca os use no lugar de autorização determinística, validação de negócio, limites operacionais ou revisão humana exigida pelo risco.

