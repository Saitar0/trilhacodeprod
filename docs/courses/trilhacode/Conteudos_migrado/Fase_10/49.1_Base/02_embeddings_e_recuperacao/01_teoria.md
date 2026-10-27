---
arquivo_id: "f10-49-1-t02"
parent_key: "49.1"
tipo_arquivo: "theory"
assunto: "02_embeddings_e_recuperacao"
ordem: 2
itens_origem: ["### 2. Representar e recuperar conteúdo"]
---


### 2. Representar e recuperar conteúdo
Embedding converte texto em um vetor numérico cuja distância/proximidade pode ajudar a localizar textos relacionados. Similaridade é um sinal de relevância, não prova de verdade, equivalência ou autorização. A busca semântica pode encontrar correspondência mesmo quando palavras não coincidem; busca lexical pode ser melhor para identificadores, nomes e termos exatos. Uma combinação lexical e vetorial pode ajudar, mas precisa ser medida. Reordenação de resultados (reranking) é uma opção a avaliar se a busca inicial trouxer candidatos úteis em posições ruins.

Na consulta, converta a pergunta segundo o mesmo espaço/modelo usado no índice, recupere candidatos, aplique filtros de metadados e limite número/tamanho dos trechos enviados ao modelo. Um filtro de acesso deve vir de identidade e política confiáveis no servidor, não de um tenant ou papel fornecido livremente pelo cliente. Aplique o controle antes de expor conteúdo ao modelo e valide acesso ao resultado/citação também na resposta; se possível, use defesa em profundidade nas camadas de busca e aplicação.

