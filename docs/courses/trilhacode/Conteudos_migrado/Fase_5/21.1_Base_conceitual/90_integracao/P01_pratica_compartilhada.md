---
arquivo_id: "f5-21-1-90-integracao-p01-pratica-compartilhada"
parent_key: "21.1"
tipo_arquivo: "practice"
assuntos: ["01_coesao_responsabilidades", "02_acoplamento_custo_mudanca"]
ordem: 1
itens_origem: ["P1"]
---

## Atividades práticas

### Atividade 1 — Mapa de responsabilidades e mudanças
**Objetivo:** localizar um problema concreto de coesão/acoplamento antes de desenhar uma refatoração.

**Passos:**
1. Escolha um trecho real do projeto que combine entrada/saída, regra ou integração externa.
2. Escreva qual comportamento ele oferece e liste razões diferentes que poderiam fazê-lo mudar.
3. Desenhe módulos/funções envolvidos e setas de dependência, indicando quais detalhes atravessam cada fronteira.
4. Escolha duas mudanças plausíveis, como alterar formato HTTP e substituir serviço externo, e marque os pontos que precisariam mudar.
5. Proponha uma separação mínima e escreva que problema ela pretende reduzir.

**Dica:** comece por mudanças reais ou próximas do domínio do projeto. Não divida por substantivo ou verbo apenas para aumentar o número de classes.

