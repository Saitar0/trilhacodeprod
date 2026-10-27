---
arquivo_id: "f9-41-2-03-descoberta-teste-fronteira-01-teoria"
parent_key: "41.2"
tipo_arquivo: "theory"
assunto: "03_descoberta_teste_fronteira"
ordem: 3
itens_origem: ["### 3. Descubra e teste a fronteira"]
---


### 3. Descubra e teste a fronteira
Comece pelas capacidades e regras de negócio, não por camadas técnicas (frontend, API, banco) nem por substantivos do código. Uma fronteira candidata deve ter linguagem e regras coerentes, dados que possam ser controlados por ela, poucas dependências síncronas e mudanças que façam sentido juntas. Mapeie chamadas, tabelas compartilhadas, transações, equipes e frequência de mudanças; dados de produção podem mostrar acoplamentos que o diagrama não revela.

Perguntas de teste:
1. A capacidade pode ser implantada sem coordenar uma mudança simultânea em outros módulos?
2. Tem dados que pode possuir e modificar por uma interface estável?
3. Pode continuar correta durante falha ou atraso dos vizinhos?
4. A equipe consegue observar, proteger, escalar e recuperar o serviço?
5. Qual resultado melhora, e qual métrica mostrará isso?

Se as respostas forem fracas, fortaleça primeiro módulos e interfaces dentro do processo atual. Criar um serviço por tabela, entidade ou camada tende a multiplicar chamadas sem criar limites de negócio úteis.

