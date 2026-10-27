---
arquivo_id: "f7-32-1-01-workflow-reprodutibilidade-quality-gates-01-teoria-md"
parent_key: "32.1"
tipo_arquivo: "theory"
assunto: "01_workflow_reprodutibilidade_quality_gates"
ordem: 1
itens_origem: ["### Microtópico 1 — Workflow, evento, job e step", "### Microtópico 2 — Reprodutibilidade e quality gates"]
---

### Microtópico 1 — Workflow, evento, job e step

GitHub Actions executa automações declaradas em arquivos YAML dentro de `.github/workflows`. Um **evento** inicia o workflow, por exemplo `pull_request` ou `push`; um **job** agrupa trabalho em um runner; e cada **step** executa uma ação ou comando. Jobs podem rodar em paralelo ou declarar `needs` para depender de outro job. A escolha do evento define quando e em qual contexto a automação roda.

Para validação de código de pull request, `pull_request` costuma ser a opção apropriada: o workflow recebe o contexto de validação do PR e o token tem permissões limitadas conforme configuração e origem do PR. `pull_request_target` executa no contexto confiável do repositório base e pode ter acesso a permissões e segredos; não faça checkout e execução do código não confiável do PR nesse contexto. Separar validação de código de tarefas privilegiadas reduz a chance de um PR executar comandos com credenciais do projeto.

Use nomes estáveis e específicos para workflows e jobs. O nome do job pode ser referenciado na configuração de checks obrigatórios; alterá-lo pode exigir atualizar essa configuração.

### Microtópico 2 — Reprodutibilidade e quality gates

Um check confiável deve produzir resultado comparável para o mesmo commit e configuração. Para Node.js, escolha uma versão compatível com o projeto, use o lockfile e instale com `npm ci`, que falha quando o lockfile e o manifesto não estão sincronizados. Execute os scripts que o próprio projeto declara para lint, build e testes. Se o repositório usa outro gerenciador, siga o lockfile correspondente (`pnpm-lock.yaml`, `yarn.lock` etc.) e o comando de instalação imutável daquela ferramenta.

Cache de dependências pode reduzir tempo, mas não deve ser necessário para que o workflow funcione corretamente. A chave deve refletir o arquivo de dependências relevante; a instalação limpa ainda precisa ser válida sem cache. Não use o cache como prova de que dependências estão atualizadas ou de que os testes são determinísticos.

Um job verde só informa que aquele job terminou com sucesso. Para transformá-lo em **quality gate**, configure a regra de proteção da branch para exigir o check correto antes do merge. Se a organização usa fila de merge, o workflow também pode precisar do evento `merge_group`. O check obrigatório precisa ser estável, ter nome inequívoco e executar em todos os contextos exigidos pela política do repositório.

