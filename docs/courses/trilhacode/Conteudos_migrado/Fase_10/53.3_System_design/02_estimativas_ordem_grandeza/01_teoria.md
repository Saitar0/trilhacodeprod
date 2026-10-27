---
arquivo_id: "f10-53-3-t02"
parent_key: "53.3"
tipo_arquivo: "theory"
assunto: "02_estimativas_ordem_grandeza"
ordem: 2
itens_origem: ["### 2. Estimar ordens de grandeza"]
---


### 2. Estimar ordens de grandeza
Faça contas simples e escreva unidades em cada etapa. Exemplo ilustrativo: com 100 mil usuários ativos por dia e 10 ações por usuário, há 1 milhão de ações/dia. Dividindo por 86.400 segundos, a média é cerca de 12 ações/s. Se o pico for hipoteticamente 5 vezes a média, planeje para cerca de 60 ações/s. O fator de pico é uma hipótese a validar, não uma propriedade universal.

Para armazenamento, multiplique registros criados por dia pelo tamanho médio e pelos dias de retenção; depois declare se a conta inclui índices, réplicas ou overhead. Para tráfego, multiplique taxa pela dimensão média do payload. Uma estimativa serve para identificar gargalos e fazer perguntas melhores. Mostre arredondamentos, premissas e faixa plausível; não apresente resultado de guardanapo como capacidade comprovada.

