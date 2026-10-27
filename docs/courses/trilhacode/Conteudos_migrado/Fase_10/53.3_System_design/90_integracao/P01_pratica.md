---
arquivo_id: "f10-53-3-p01"
parent_key: "53.3"
tipo_arquivo: "practice"
assuntos: ["01_requisitos_e_delimitacao", "02_estimativas_ordem_grandeza"]
ordem: 1
itens_origem: ["P01"]
---


### Atividade 1 — Requisitos e estimativa de um encurtador de URLs
**Contexto e objetivo:** praticar clarificação, estimativa dimensional e delimitação antes de desenhar componentes.

**Dados iniciais:** cenário didático com 100 mil usuários ativos/dia; cada usuário cria 2 URLs e acessa 20 URLs por dia. Considere, apenas para a conta inicial, 500 bytes de metadados por URL e retenção de 365 dias. Não foram informados fator de pico, overhead de índice nem crescimento futuro.

**Instruções:** escreva cinco perguntas de requisito; classifique pelo menos dois requisitos funcionais e dois não funcionais; calcule criações/leitura por dia, taxa média e armazenamento bruto anual de metadados. Declare o que está fora da conta e proponha uma faixa ou hipótese de pico, sem tratá-la como fato.

**Entrega:** tabela de requisitos e cálculos com unidades, hipóteses e exclusões.

**Dica gradual:** converta usuários × ações/usuário em ações/dia; divida por 86.400 para média por segundo; para armazenamento, multiplique URLs criadas/dia × 500 bytes × 365 dias.

