---
arquivo_id: "f8-39-3-04-demonstrar-reverter-encerrar-md"
parent_key: "39.3"
tipo_arquivo: "project_milestone"
ordem: 4
itens_origem: ["M4"]
titulo_marco: "Entrega 4 — Demonstrar, reverter, documentar e encerrar"
---


### Entrega 4 — Demonstrar, reverter, documentar e encerrar

Faça uma demonstração curta em staging/sandbox que comece do estado registrado, gere o cenário do tipo, mostre o teste e observe a métrica/log/painel. Provoque apenas uma falha controlada, limitada e reversível que valide uma parte importante do sistema — ou use um tabletop se a falha tiver risco não aceitável. Combine antes o limite de carga, condição de parada, pessoa responsável pela recuperação e como confirmar a recuperação.

Demonstre rollback de forma compatível com o tipo de alteração. Reverter binário não reverte automaticamente migration destrutiva, transações concluídas, eventos emitidos ou estado externo; verifique compatibilidade e escreva o procedimento de recuperação antes do ensaio. Após a mudança, compare comportamento com o SLI ou teste de aceite e confirme saúde do serviço.

Finalize README e revisão de entrega: passos para preparar, testar, construir, implantar, observar, reverter e destruir; arquitetura e dependências; decisões; limitações; custo estimado/observado; riscos; evidências. Atualize a cobertura do tipo apenas após aprovação do aceite.

**Evidências:** gravação/capturas ou roteiro reproduzível; execução de teste; histórico de pipeline/deploy; métrica antes/durante/depois; evidência do rollback/recuperação; README; confirmação de encerramento dos recursos temporários; linha da tabela de cobertura preenchida após aceite.


**Feedback:** se a falha não for segura, não execute em cloud; use um tabletop com dados sintéticos e identifique a limitação. Registre como pendente qualquer prova que dependa de ambiente ainda indisponível, sem marcar a cobertura como concluída.

