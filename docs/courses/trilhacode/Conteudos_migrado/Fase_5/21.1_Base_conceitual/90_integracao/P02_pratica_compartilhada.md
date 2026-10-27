---
arquivo_id: "f5-21-1-90-integracao-p02-pratica-compartilhada"
parent_key: "21.1"
tipo_arquivo: "practice"
assuntos: ["03_di_ponto_de_composicao", "04_refatoracao_comportamento_evidencia"]
ordem: 2
itens_origem: ["P2"]
---

### Atividade 2 — Extração de uma regra testável
**Objetivo:** separar uma regra de negócio de um detalhe externo e verificar que o contrato continua igual.

**Passos:**
1. Escolha uma operação que misture regra de negócio e acesso a HTTP, banco, relógio ou serviço externo.
2. Registre o comportamento atual com um teste, exemplo executável ou contrato observável.
3. Extraia a regra para função/módulo/caso de uso e forneça explicitamente apenas o colaborador externo necessário.
4. Na inicialização da aplicação, conecte a dependência concreta; no teste, use a implementação real mais simples ou um dublê de fidelidade adequada.
5. Compare o teste e a estrutura antes/depois: resultado, dependências necessárias, setup e partes do sistema que mudaram.

**Dica:** não substitua todas as dependências por mocks automaticamente. Uma dependência real rápida pode tornar o teste mais fiel; reserve dublês para fronteiras que de fato precisam ser controladas.

