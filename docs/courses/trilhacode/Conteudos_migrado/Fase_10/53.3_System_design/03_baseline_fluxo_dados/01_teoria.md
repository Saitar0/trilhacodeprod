---
arquivo_id: "f10-53-3-t03"
parent_key: "53.3"
tipo_arquivo: "theory"
assunto: "03_baseline_fluxo_dados"
ordem: 3
itens_origem: ["### 3. Desenhar um baseline e seguir os dados"]
---


### 3. Desenhar um baseline e seguir os dados
Desenhe primeiro o fluxo principal de ponta a ponta, por exemplo: cliente → API → autenticação/autorização → aplicação → banco. Acrescente cache, fila, CDN, replicação ou serviços separados apenas quando um requisito ou gargalo justificar. Marque no diagrama quem inicia cada chamada, onde os dados são persistidos, quais fronteiras são confiáveis e o que acontece em erro.

Defina responsabilidades e contratos principais: operações da API, entidades/dados e índices de consulta. Considere se a operação precisa de transação, se a leitura pode ser eventualmente consistente e se duplicatas podem ocorrer. Para cada componente extra, explique o benefício e o custo operacional que introduz. Evite desenhar tecnologia pela popularidade.

