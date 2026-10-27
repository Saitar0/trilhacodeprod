---
arquivo_id: "f6-30-1-02-carregamento-e-virtualizacao-p03-pratica-md"
parent_key: "30.1"
tipo_arquivo: "practice"
assunto: "02_carregamento_e_virtualizacao"
ordem: 3
itens_origem: ["P03"]
---

### Atividade 3 — Escolha entre divisão de código e virtualização
**Objetivo:** reduzir uma medida de carregamento ou renderização sem criar uma regressão de interação.

**Passos:**
1. Selecione uma rota que carrega um módulo pesado ou uma lista grande; meça bundle/tempo inicial ou custo de renderização.
2. Para uma rota ou recurso pouco usado, experimente `lazy` com um fallback de carregamento; para uma lista muito longa, experimente virtualização com dados controlados.
3. Compare a métrica apropriada: código inicial e chunk da rota para divisão; número de linhas no DOM e tempo de atualização/rolagem para virtualização.
4. Verifique o primeiro acesso ao recurso adiado, rolagem, redimensionamento, teclado, foco e leitura dos itens virtualizados.
5. Registre o que a técnica não resolveu — por exemplo, tamanho total publicado, consulta lenta ou busca excessiva — e decida se a complexidade compensa.

**Dica:** não use um benchmark de DOM como evidência de menor tráfego de rede. Identifique se os dados e o código são baixados e quando.

**Entrega:** comparação de uma técnica com baseline, verificação de acessibilidade e recomendação de manter ou remover.

**Critérios de conclusão:** a métrica é pertinente à técnica; estados de espera e navegação continuam utilizáveis; limites e custos estão documentados.

