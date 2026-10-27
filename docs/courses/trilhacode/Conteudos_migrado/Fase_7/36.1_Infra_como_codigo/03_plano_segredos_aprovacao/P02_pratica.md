---
arquivo_id: "f7-36-1-03-plano-segredos-aprovacao-p02-pratica-md"
parent_key: "36.1"
tipo_arquivo: "practice"
assunto: "03_plano_segredos_aprovacao"
ordem: 2
itens_origem: ["P02"]
---

### Atividade 2 — Leia e aprove um plano de mudança

**Desafio:** produza uma mudança controlada e decida se um plano está pronto para aplicação.

**Passos:**
1. Gere plano inicial e classifique cada ação como create, update in-place, replace ou destroy.
2. Altere uma tag e gere um novo plano; explique por que a alteração não deve recriar o recurso.
3. Em arquivo separado ou revisão conceitual, remova o recurso e inspecione o plano de destroy sem aplicá-lo; identifique recurso e dados que seriam afetados.
4. Introduza mudança externa controlada no sandbox ou descreva cenário de drift; compare realidade, configuração e plano sem “aceitar” mudança às cegas.
5. Se utilizar arquivo de plano salvo, trate-o como sensível e explique como garante que o plano revisado é exatamente o aplicado.

**Evidências:** planos; tabela ação → motivo → risco → decisão; confirmação explícita de não aplicação do destroy; registro da revisão.

**Verificação:** replacement/destroy nunca são confundidos com atualização simples; mudança de estado/configuração invalida aprovação anterior; drift tem causa investigada.

**Aceite:** cada ação tem interpretação; mudança simples e destrutiva são comparadas; decisão corresponde ao sandbox e ao plano revisado; nenhum plano/state sensível foi publicado.

