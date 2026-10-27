---
arquivo_id: "f7-32-1-02-seguranca-actions-falhas-p03-pratica-md"
parent_key: "32.1"
tipo_arquivo: "practice"
assunto: "02_seguranca_actions_falhas"
ordem: 3
itens_origem: ["P03"]
---

### Atividade 3 — Faça uma revisão de segurança e manutenção

**Desafio:** revise o workflow como uma dependência executável e documente riscos e ações.

**Passos:**
1. Liste eventos, jobs, `GITHUB_TOKEN` permissions, secrets acessíveis e Actions chamadas.
2. Identifique se algum evento privilegiado executa código de PR, especialmente combinação de `pull_request_target`, checkout e comandos de instalação/build.
3. Confira origem, release e SHA das Actions conforme política do projeto; não trate versão citada no material como substituto da revisão atual.
4. Verifique se o cache usa a chave de dependências adequada e se a instalação continua correta sem cache.
5. Se Sonar ou outra análise estiver configurada, descreva o sinal que o gate verifica, limiar, falso positivo e responsável por manutenção. Se não for necessária, registre a decisão de não incluir.
6. Corrija problemas encontrados no workflow de exercício e registre cada decisão com impacto e evidência.

**Evidências:** inventário de eventos/permissões/dependências; revisão do diff; achados e correções; justificativa de análise estática e de cache.

**Verificação:** um colega consegue identificar qual código executa em cada evento, quais credenciais ficam disponíveis e como uma Action será atualizada.

**Aceite:** nenhuma credencial está hard-coded ou impressa; permissões seguem menor privilégio; código não confiável não é executado em contexto privilegiado; versões e limites estão documentados.

