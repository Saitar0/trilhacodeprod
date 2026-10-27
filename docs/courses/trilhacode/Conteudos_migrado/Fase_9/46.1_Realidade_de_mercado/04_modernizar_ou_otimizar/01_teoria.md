---
arquivo_id: "f9-46-1-04-modernizar-ou-otimizar-01-teoria"
parent_key: "46.1"
tipo_arquivo: "theory"
assunto: "04_modernizar_ou_otimizar"
ordem: 4
itens_origem: ["### 4. Decidir quando modernizar e quando otimizar"]
---


### 4. Decidir quando modernizar e quando otimizar
Em sistemas existentes, entenda primeiro valor, contratos, dados, restrições e comportamento observado. Uma reescrita de uma vez pode descartar comportamento implícito e introduzir riscos; uma migração gradual pode encaminhar capacidades selecionadas ao sistema novo enquanto o restante permanece no legado. No padrão Strangler, uma fachada ou roteador encaminha cada fatia. A migração exige definir quem é dono dos dados, como evitar duas fontes de verdade, como observar divergências e como reverter o tráfego.

Débito técnico é uma escolha ou condição que aumenta o custo futuro de mudança. Registre exemplos concretos e seu efeito: incidentes, demora para entregar, erros recorrentes, dependência sem suporte ou dificuldade para testar. Código antigo, por si só, não prova que há dívida prioritária. Formule a hipótese de melhoria e uma medida que poderia confirmá-la.

“Alta volumetria” precisa ser traduzida em requisitos: taxa de requisições ou mensagens, concorrência, latência esperada, taxa de erro, crescimento de dados e custo aceitável. Compare medidas com o objetivo do produto e localize o gargalo antes de escolher cache, particionamento, fila ou serviço separado. As quatro sinais de monitoramento apresentadas pelo Google SRE — latência, tráfego, erros e saturação — ajudam a organizar observações, mas não substituem requisitos e dados do sistema que está sendo avaliado.

