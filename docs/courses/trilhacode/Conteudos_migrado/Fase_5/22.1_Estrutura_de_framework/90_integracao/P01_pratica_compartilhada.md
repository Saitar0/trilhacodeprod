---
arquivo_id: "f5-22-1-90-integracao-p01-pratica-compartilhada"
parent_key: "22.1"
tipo_arquivo: "practice"
assuntos: ["01_modulos_grafo_e_composicao", "02_controller_provider_e_di_runtime"]
ordem: 1
itens_origem: ["P1"]
---

## Atividades práticas

### Atividade 1 — Estruture uma rota em módulos Nest
**Objetivo:** separar adaptação HTTP e colaboração de aplicação num módulo de feature.

**Passos:**
1. Escolha uma rota simples Express do projeto, por exemplo listar ou criar um item.
2. Crie um módulo de feature com controller e provider de aplicação; registre-os nos campos apropriados do módulo.
3. Mantenha no controller apenas adaptação de entrada/saída e delegue comportamento ao provider.
4. Registre a feature no módulo raiz e invoque a rota com um caso válido e um caso de falha.
5. Desenhe o caminho da requisição até o provider e anote quais metadados do Nest conectam cada parte.

**Dica:** não transfira a rota para Nest copiando a mesma função extensa para o controller. Reaproveite o contrato HTTP, mas identifique regra e colaboração externas.

