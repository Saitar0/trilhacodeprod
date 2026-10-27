---
arquivo_id: "f9-41-2-04-extracao-incremental-reversao-01-teoria"
parent_key: "41.2"
tipo_arquivo: "theory"
assunto: "04_extracao_incremental_reversao"
ordem: 4
itens_origem: ["### 4. Extração incremental, reversão e decisão"]
---


### 4. Extração incremental, reversão e decisão
Para modernizar um sistema em uso, prefira uma fatia limitada que permita coexistência e retorno:
1. registre situação atual, métrica, dependências e critérios de sucesso;
2. crie uma interface/adaptador para a capacidade, ainda atendida pelo monólito;
3. mova uma operação delimitada e roteie o tráfego gradualmente para a nova implementação;
4. compare resultados, erros, latência, custo e carga operacional;
5. mantenha um caminho de reversão; retire a implementação antiga só após evidência de estabilidade e propriedade dos dados.

Uma camada proxy ou roteamento vira dependência crítica e também precisa de disponibilidade e observabilidade. Durante a coexistência, evite escrita dupla sem reconciliação e defina qual implementação é a fonte da verdade para cada dado. Uma reversão precisa considerar mudanças de esquema e eventos já emitidos; voltar o código não desfaz efeitos externos.

Registre a decisão em um ADR curto: contexto, opções (incluindo manter), evidências, benefício esperado, custos, riscos, dono, métricas, prazo de revisão e condição de parar/reverter. As métricas podem incluir lead time/deploy, falhas e rollback, latência/capacidade, dependências entre módulos, incidentes, esforço de plantão e custo total. Métricas sem hipótese associada não justificam a migração.

