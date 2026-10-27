---
arquivo_id: "f5-20-3-01-autorizacao-acao-objeto-01-teoria"
parent_key: "20.3"
tipo_arquivo: "theory"
assunto: "01_autorizacao_acao_objeto"
ordem: 1
itens_origem: ["Microtópico 1 — Decida acesso para ação e recurso"]
---

## Microtópico 1 — Decida acesso para ação e recurso
Autenticação confirma a identidade; autorização decide se aquela identidade pode executar determinada ação naquele recurso, naquele contexto. A autorização precisa considerar regras do domínio: proprietário, organização/tenant, papel, estado atual do recurso e ação solicitada. Estar autenticado ou conhecer um identificador não comprova permissão.

Adote negação por padrão: só permita ações cobertas por uma regra explícita. Faça a verificação no servidor em toda requisição e perto da operação protegida. Uma checagem na interface, em uma tela anterior ou apenas no endpoint de listagem não protege uma leitura ou alteração direta posterior. Identificadores aleatórios podem dificultar descoberta, mas não substituem autorização.

**Exemplo:** ao ler, editar ou excluir um pedido, verifique que o usuário atual pertence ao tenant correto e tem permissão para aquela ação sobre aquele pedido. A regra pode permitir a um administrador uma ação adicional, sem presumir que todo usuário autenticado seja administrador.

**Erro comum:** comparar somente o ID do usuário com o ID do caminho. Relações reais podem envolver organização, equipe, compartilhamento, papel e estado do objeto; cada regra precisa corresponder ao domínio.

**Checagem:** se a pessoa trocar o ID na requisição, qual regra do servidor impede acesso ou alteração de um recurso alheio?

