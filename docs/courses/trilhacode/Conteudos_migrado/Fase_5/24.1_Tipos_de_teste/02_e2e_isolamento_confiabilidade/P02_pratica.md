---
arquivo_id: "f5-24-1-02-e2e-isolamento-confiabilidade-p02-pratica"
parent_key: "24.1"
tipo_arquivo: "practice"
assunto: "02_e2e_isolamento_confiabilidade"
ordem: 2
itens_origem: ["P2"]
---

### Atividade 2 — Torne um teste repetível

**Desafio:** um teste de integração de cadastro falha de forma intermitente porque reutiliza e-mail fixo, depende de outro teste e espera dois segundos pela resposta.

**Passos:**
1. Identifique fontes de estado e não determinismo.
2. Defina como preparar e limpar o registro em cada teste.
3. Troque o e-mail fixo por dado isolado/único ou estratégia equivalente compatível com a constraint.
4. Substitua a espera fixa por espera da condição observável ou sincronização do processo.
5. Execute mentalmente o cenário isolado, repetido e em ordem diferente; anote quais recursos precisam ser encerrados.

**Dica:** tornar dado aleatório não basta se o teste não consegue encontrar ou limpar o que criou.

