# Beta 2 — decisão Git proposta

## Conclusão

Recomenda-se `e801cee8f765f87b6e42ccf867a9a70f0325b389` como **base técnica de trabalho para a próxima consolidação**, não como prova da versão operacional implantada nem como aprovação final da base canônica do produto. O commit contém a Beta 1, descende da C16 e é o ponto limpo obrigatório desta prova.

A decisão operacional de canonicalização continua dependente do responsável pelo projeto e de referências remotas atualizadas por processo autorizado. A Beta 2 não integrou branches.

## Evidências locais consultadas

| Referência | HEAD observado | Relação com `e801cee` | Observação |
|---|---|---|---|
| `codex/beta2-curriculum-import-proof` | `e801cee` | Base exata | Worktree isolada desta fase |
| `codex/beta1-platform-course-readiness-audit` | `e801cee` | Igual | Contém inventário da Beta 1 |
| `codex/fase2-1a-12c16-editorial-writer-containment` | `6c227fa` | Ancestral direto | Protótipo e documentação editorial |
| `codex/compose-ci-validation` | `27a9896` | Ancestral; 81 commits atrás | Branch do checkout original, que também tem alterações locais |
| `main` | `65857f5` | Ancestral; 103 commits atrás | Ref local, não atualizada nesta fase |
| `origin/main` (cache local) | `22dca64` | Ancestral; 56 commits atrás | Sem fetch; pode estar desatualizada |
| `origin/staging` (cache local) | `fff8521` | Divergente: 57 commits atrás e 3 exclusivos | Não usada como base |
| `migracao-estrutura` | `147dc68` | Divergente: 57 commits atrás e 12 exclusivos | Trabalho curricular separado e dirty |

Os números de commits são comparações do grafo local observado, não uma afirmação sobre o servidor remoto atual.

## Trabalho preservado

O checkout original está em `codex/compose-ci-validation` e contém alterações locais em importação, leitores, trilhas, permissões, testes, frontend, documentação de curso e arquivos novos. Ele permaneceu intocado. As worktrees de autenticação, frontend/acessibilidade, atividade, CI e gerações editoriais também não foram modificadas.

A worktree `fase1-migracao` permanece em `migracao-estrutura` (`147dc68`). Seu `trilha-code-bulk-import.json` está modificado e há contratos, relatórios e código de conversão não rastreados. O conteúdo segmentado `Conteudos_migrado` consultado estava rastreado e sem mudanças locais detectadas; isso não torna o bundle ou os contratos locais aprovados.

## Recomendação de integração futura

1. Solicitar ao responsável pelo projeto que ratifique um SHA de plataforma após atualizar as referências remotas por procedimento autorizado.
2. Obter confirmação do proprietário da worktree migratória e consolidar seus arquivos locais em mudanças revisáveis, sem copiar seu estado dirty diretamente.
3. Reconciliar contratos e regressões sobre uma base limpa antes de qualquer merge.
4. Manter a implementação editorial C8–C16 experimental até haver autorização separada e eliminação dos bypasses.

Nenhuma referência foi atualizada, e nenhum merge, cherry-pick, reset, rebase ou push foi executado.
