---
arquivo_id: "f6-31-1-90-integracao-p03-pratica-md"
parent_key: "31.1"
tipo_arquivo: "practice"
assuntos: ["02_fronteira_e_renderizacao", "03_route_handlers_endpoints"]
ordem: 3
itens_origem: ["P03"]
---

### Atividade 3 — Compare Route Handler e estratégia de renderização
**Objetivo:** publicar uma rota HTTP segura e explicar seu comportamento de produção.

**Passos:**
1. Crie `app/api/items/route.ts` com leitura de coleção de teste e, se fizer sentido, uma operação de escrita com validação de entrada.
2. Verifique método, parâmetros, formato da resposta e status de sucesso, entrada inválida, não autenticado e não autorizado.
3. Para a página que usa esses dados, decida se o conteúdo pode ser pré-gerado, se depende da requisição ou se combina shell e conteúdo dinâmico.
4. Documente a configuração de cache e revalidação para a versão utilizada; inclua identidade do usuário na decisão de isolamento e evite cache compartilhado de dados privados.
5. Gere e execute o build no runtime de teste previsto e confirme que páginas, handlers, variáveis de servidor e rotas funcionam conforme a configuração declarada.

**Dica:** não use o servidor de desenvolvimento como única evidência do modo de produção; o comportamento de cache e build pode ser diferente.

**Entrega:** Route Handler documentado, tabela de respostas e decisão de renderização/cache com evidência de build.

**Critérios de conclusão:** entrada validada; endpoint faz autenticação e autorização; cache não mistura usuários; plataforma atende ao runtime escolhido.

