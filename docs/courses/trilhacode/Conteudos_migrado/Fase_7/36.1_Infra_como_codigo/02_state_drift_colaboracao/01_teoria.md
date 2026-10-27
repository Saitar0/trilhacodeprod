---
arquivo_id: "f7-36-1-02-state-drift-colaboracao-01-teoria-md"
parent_key: "36.1"
tipo_arquivo: "theory"
assunto: "02_state_drift_colaboracao"
ordem: 2
itens_origem: ["### Microtópico 3 — State, drift e colaboração"]
---

### Microtópico 3 — State, drift e colaboração

O **state** guarda o vínculo entre recursos da configuração e objetos reais, junto com atributos usados no próximo plano. Pode conter informação sensível mesmo que ela não apareça claramente no HCL. O backend local grava state em disco; é conveniente para laboratório individual descartável, mas é fácil perder, compartilhar incorretamente ou usar em paralelo sem coordenação adequada.

Um backend remoto pode centralizar state e, dependendo do backend, oferecer controle de acesso, criptografia, versionamento/recuperação e **state locking**. Locking evita que dois runs atualizem o mesmo state ao mesmo tempo, mas nem todo backend oferece lock e ele não substitui revisão do plano. Confirme as capacidades e instruções atuais do backend escolhido. Proteja o acesso como dado crítico; não publique state em Git, artefato aberto, ticket ou log. Evite `state push`/edição manual; operações de reparo exigem backup e entendimento de lineage/serial.

**Drift** é diferença entre configuração/state e a realidade alterada fora do Terraform. Plan/refresh pode sinalizar diferença e propor correção, mas não significa que toda alteração manual deve ser revertida automaticamente. Descubra por que houve mudança, atualize configuração/state segundo o processo do time e gere novo plano. Workspaces/estados separados ajudam a separar alvos, mas não são, sozinhos, uma fronteira completa de segurança ou conta AWS.

