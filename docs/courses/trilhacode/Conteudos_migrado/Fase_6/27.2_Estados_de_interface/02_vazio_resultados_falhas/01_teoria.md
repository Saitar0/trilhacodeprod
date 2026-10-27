---
arquivo_id: "f6-27-2-02-vazio-resultados-falhas-01-teoria-md"
parent_key: "27.2"
tipo_arquivo: "theory"
assunto: "02_vazio_resultados_falhas"
ordem: 2
itens_origem: ["## Microtópico 2 — Diferencie vazio, ausência de resultados e falha"]
---

## Microtópico 2 — Diferencie vazio, ausência de resultados e falha
Uma resposta bem-sucedida com `items: []` significa que a consulta terminou e não encontrou itens. Uma busca por “React” sem correspondências também pode ser válida, mas a ação útil talvez seja limpar ou alterar o filtro. Já uma coleção vazia porque o usuário ainda não criou seu primeiro projeto pede uma chamada para criar o primeiro item. Esses cenários compartilham a ausência de linhas, mas têm causas e próximas ações diferentes.

Erro não é vazio. Se a rede falhou, mostrar “Nenhum resultado” mascara o problema e leva a uma decisão errada. Mensagens de interface devem indicar o que ocorreu em linguagem compreensível e, quando possível, o que a pessoa pode fazer: tentar novamente, revisar filtros ou conferir conexão. Não exponha stack traces, tokens, SQL, endereços internos ou detalhes sensíveis. Códigos como `404` só representam “sem itens” quando o contrato daquele endpoint define esse significado; não assuma isso para toda API.

| Contexto | Mensagem possível | Próxima ação |
| --- | --- | --- |
| Primeiro acesso sem itens | “Você ainda não tem projetos.” | Criar projeto |
| Filtro sem correspondências | “Nenhum projeto corresponde a este filtro.” | Limpar ou editar filtro |
| Consulta falhou sem dados | “Não foi possível carregar os projetos.” | Tentar novamente ou verificar conexão |
| Atualização falhou com dados anteriores | “Não foi possível atualizar. Exibindo os dados carregados anteriormente.” | Tentar atualizar novamente |

