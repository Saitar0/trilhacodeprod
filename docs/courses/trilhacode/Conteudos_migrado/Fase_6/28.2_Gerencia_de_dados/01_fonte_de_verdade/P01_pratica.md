---
arquivo_id: "f6-28-2-01-fonte-de-verdade-p01-pratica-md"
parent_key: "28.2"
tipo_arquivo: "practice"
assunto: "01_fonte_de_verdade"
ordem: 1
itens_origem: ["P01"]
---

### Atividade 1 — Mapeie a fonte de verdade e os ciclos de vida
**Objetivo:** propor um desenho de estado coerente para uma aplicação com áreas públicas e autenticadas.

**Passos:**
1. Use um cenário com sessão, modal, filtro, lista paginada da API, formulário de edição, preferência de tema, indicador de erro e contador do servidor.
2. Para cada item, anote origem, fonte autoritativa, componentes consumidores, ciclo de vida e se deve sobreviver à navegação ou recarga.
3. Escolha estado local, URL, store de cliente ou cache remoto para cada item e explique a decisão.
4. Marque quais dados devem ser removidos ou isolados ao sair da conta e quais não podem ser protegidos apenas pelo cliente.
5. Desenhe o fluxo de edição do formulário desde o rascunho local até a resposta do servidor e a atualização da tela.

**Dica:** “global” descreve alcance entre componentes; “remoto” descreve origem e autoridade. Um dado não é remoto só porque muitos componentes o leem.

**Entrega:** matriz de classificação e diagrama do fluxo de leitura e edição.

**Critérios de conclusão:** cada item tem uma fonte autoritativa; persistência está ligada a um requisito; o desenho separa autenticação no servidor de apresentação no cliente.

