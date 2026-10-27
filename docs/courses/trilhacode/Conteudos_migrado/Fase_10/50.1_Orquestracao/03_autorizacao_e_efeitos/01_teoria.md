---
arquivo_id: "f10-50-1-t03"
parent_key: "50.1"
tipo_arquivo: "theory"
assunto: "03_autorizacao_e_efeitos"
ordem: 3
itens_origem: ["### 3. Aplicar autorização e controlar efeitos"]
---


### 3. Aplicar autorização e controlar efeitos
Autorize cada execução com identidade, papel e contexto validados pelo servidor; confira novamente o acesso ao recurso específico. Use menor privilégio no serviço downstream, idealmente escopos distintos para leitura e escrita. Não confie em um argumento de tenant ou proprietário só porque ele veio em JSON válido.

Para ações com efeitos — enviar mensagem, alterar registro, cobrar, excluir — determine o risco e os controles necessários. Se precisar de confirmação humana, mostre o efeito concreto e os dados relevantes antes de confirmar; não aceite uma aprovação genérica que possa ser reutilizada para outra ação. Use idempotência contra repetição, limite tentativas e registre ator, decisão e resultado conforme política de auditoria. Um modelo pode solicitar ação fora do escopo; o backend deve recusá-la sem executar.

