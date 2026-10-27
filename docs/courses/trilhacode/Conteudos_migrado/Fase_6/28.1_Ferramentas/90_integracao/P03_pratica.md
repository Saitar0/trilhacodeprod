---
arquivo_id: "f6-28-1-90-integracao-p03-pratica-md"
parent_key: "28.1"
tipo_arquivo: "practice"
assuntos: ["01_criterio_de_escolha_vite_build", "03_fronteiras_store_cache"]
ordem: 3
itens_origem: ["P03"]
---

### Atividade 3 — Audite build e variáveis expostas
**Objetivo:** compreender o que o Vite entrega ao navegador e evitar colocar segredos no cliente.

**Passos:**
1. Examine os scripts de desenvolvimento e build do projeto e descreva o que cada um faz.
2. Liste as variáveis usadas pelo código do cliente e classifique cada uma como pública ou secreta, justificando a classificação.
3. Confira como o projeto escolhe a URL da API por ambiente e valide valores esperados, considerando que variáveis carregadas pelo Vite são strings.
4. Gere o build local e identifique a pasta de saída e o tipo de hospedagem necessário para servi-la.
5. Escolha uma rota interna da aplicação e descreva como verificaria o acesso direto a essa rota na hospedagem. Não publique segredos nem inclua credenciais no bundle.

**Dica:** tudo que o navegador precisa receber pode ser inspecionado por quem usa a aplicação. Não trate `.env` como cofre quando a variável é exposta ao cliente.

**Entrega:** mapa dos scripts, tabela de variáveis e nota curta sobre build e hospedagem.

**Critérios de conclusão:** scripts estão compreendidos; nenhuma credencial privada é exposta; saída e comportamento de rotas são verificáveis no ambiente de publicação previsto.

