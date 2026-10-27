---
arquivo_id: "f10-49-1-t04"
parent_key: "49.1"
tipo_arquivo: "theory"
assunto: "04_avaliacao_recuperacao_resposta"
ordem: 4
itens_origem: ["### 4. Avaliar recuperação e resposta em separado"]
---


### 4. Avaliar recuperação e resposta em separado
Monte perguntas com conjunto de documentos/trechos relevantes conhecido. **Recall@k** mede quantos dos itens relevantes conhecidos aparecem entre os k primeiros; **precision@k** mede qual fração desses k resultados é relevante. Essas métricas avaliam recuperação e dependem de uma referência bem rotulada. Para geração, avalie se a resposta responde à pergunta, se cada afirmação importante está apoiada nos trechos, se as citações apontam para fontes corretas e se o sistema se abstém em casos sem suporte. Faça revisão humana em amostra; um avaliador automático também pode errar.

Inclua casos cobertos, sem resposta, ambíguos, conflitantes, com identificador exato e com tentativa de prompt injection dentro do documento. Registre a versão do corpus, modelo de embedding, regra de chunking, filtros, k, prompt e modelo gerador. Compare uma mudança por vez, como chunking, busca híbrida ou reranking, para identificar o que alterou resultados. Um benchmark pequeno mostra evidências para aquele conjunto, não garantia para todo uso real.

