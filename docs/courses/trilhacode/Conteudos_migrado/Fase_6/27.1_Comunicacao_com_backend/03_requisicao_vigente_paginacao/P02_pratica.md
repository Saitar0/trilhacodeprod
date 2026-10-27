---
arquivo_id: "f6-27-1-03-requisicao-vigente-paginacao-p02-pratica-md"
parent_key: "27.1"
tipo_arquivo: "practice"
assunto: "03_requisicao_vigente_paginacao"
ordem: 2
itens_origem: ["P02"]
---

### Atividade 2 — Impeça que resposta antiga substitua a atual

**Desafio:** conecte busca por filtro à tela React e simule que a primeira requisição demora mais que a segunda.

**Passos:**
1. Defina estado de resultado e parâmetro vigente (filtro/página) sem duplicar dados derivados.
2. Inicie a requisição para o parâmetro atual e passe signal de AbortController, ou implemente marcador que ignore resultado que perdeu validade.
3. Limpe/aborte a requisição anterior quando o parâmetro mudar ou a tela desmontar.
4. Não mostre erro comum para AbortError de requisição que ficou obsoleta; preserve estado de carregamento correto da nova busca.
5. Simule “abertas” lento e “concluídas” rápido; confirme que a lista final corresponde ao filtro atual.

**Dica:** abortar client-side economiza trabalho quando possível; use a checagem de validade também quando a operação subjacente não pode ser interrompida.

