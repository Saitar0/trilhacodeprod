---
arquivo_id: "f10-51-1-t01"
parent_key: "51.1"
tipo_arquivo: "theory"
assunto: "01_ativos_fronteiras_confianca"
ordem: 1
itens_origem: ["### 1. Mapear ativos e fronteiras de confiança"]
---


### 1. Mapear ativos e fronteiras de confiança
LLM não é uma fronteira de segurança. Prompt injection pode vir diretamente do usuário ou indiretamente de arquivos, páginas, imagens e resultados recuperados. O modelo pode tratar conteúdo malicioso como instrução e influenciar respostas ou ferramentas. RAG, instruções de sistema, filtros e guardrails podem reduzir aspectos específicos do risco; isoladamente, não garantem prevenção.

Desenhe o fluxo e marque ativos (credenciais, dados pessoais, documentos, estado de negócio), atores, entradas não confiáveis, componentes, ferramentas, saídas, logs e fronteiras entre eles. Para cada fluxo, pergunte: quem controla a entrada? O que é enviado ao provedor? Qual identidade é usada para recuperar dados? O que o modelo pode solicitar? Quem executa a ação? Que impacto ocorre em caso de abuso? Inclua exfiltração por resposta, log, URL, ferramenta, erro de autorização, conteúdo multimodal ou integração externa.

Um registro simples de ameaça liga ativo → ator/capacidade → caminho de ataque → impacto → controle preventivo/detetivo → evidência → responsável → risco residual. Priorize pelo impacto e exposição do produto, sem fingir que uma classificação numérica substitui análise contextual.

