---
arquivo_id: "f3-7-5-90-integracao-p03-pratica-integrada-interacao-requisicao"
parent_key: "7.5"
tipo_arquivo: "practice"
assuntos: ["01_reproducao_console_elements_sources", "02_network_requisicoes"]
ordem: 3
itens_origem: ["P3"]
---

### 3. Integrada — corrija interação e requisição com evidência
Use a página e o módulo da prática guiada como base. Acrescente uma chamada a um endpoint de demonstração existente ou a uma rota fixture que possa responder 404 de forma previsível. Mantenha dois defeitos controlados: o seletor incorreto do input e o caminho incorreto da requisição. Corrija um de cada vez.

**Procedimento:** abra Console, Elements, Sources e Network; reproduza e registre a primeira evidência; pause no handler e inspecione o valor; corrija apenas o seletor e repita; então selecione a requisição na Network, confira método, URL, status e resposta, corrija o caminho e repita.

**Entregáveis:** tabela com sintoma, evidência, hipótese, causa confirmada, correção e resultado; captura opcional sem credenciais/dados pessoais; passos para reproduzir em outra máquina.

**Dicas:** abra Network antes de recarregar; use breakpoint perto da leitura do campo; compare o caminho solicitado com a rota real; faça uma mudança por vez. Se o endpoint não estiver disponível, registre a limitação e use uma fixture local com resposta previsível.

