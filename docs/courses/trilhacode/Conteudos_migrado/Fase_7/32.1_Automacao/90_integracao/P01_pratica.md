---
arquivo_id: "f7-32-1-90-integracao-p01-pratica-md"
parent_key: "32.1"
tipo_arquivo: "practice"
assuntos: ["01_workflow_reprodutibilidade_quality_gates", "02_seguranca_actions_falhas"]
ordem: 1
itens_origem: ["P01"]
---

### Atividade 1 — Monte o workflow mínimo reproduzível

**Desafio:** crie um workflow de CI para um repositório Node.js que valide cada pull request.

**Passos:**
1. Inspecione `package.json`, lockfile e documentação para identificar o gerenciador, runtime compatível e scripts reais de lint, build e teste.
2. Crie `.github/workflows/ci.yml` com gatilho de PR, `contents: read`, instalação limpa pelo lockfile e passos separados para os três checks.
3. Escolha a versão da Action conforme política do projeto: tag de release ou SHA completo verificado com comentário legível.
4. Garanta que um teste ausente ou um comando inválido produza falha visível; não use `continue-on-error` nos checks requeridos.
5. Registre como executar localmente os mesmos comandos e quais limitações ainda dependem da plataforma.

**Evidências:** workflow; scripts do projeto usados; diff; saída dos comandos locais; execução do workflow no PR ou validação de sintaxe disponível no repositório.

**Verificação:** confira que o lockfile correto é usado, que todos os checks têm nomes legíveis e que o job falha quando um comando retorna erro.

**Aceite:** instalação e scripts correspondem ao projeto; permissões são explícitas e mínimas; os três checks aparecem no workflow e não há credenciais no arquivo.

