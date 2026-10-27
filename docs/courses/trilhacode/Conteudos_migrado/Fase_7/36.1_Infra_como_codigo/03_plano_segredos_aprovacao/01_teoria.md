---
arquivo_id: "f7-36-1-03-plano-segredos-aprovacao-01-teoria-md"
parent_key: "36.1"
tipo_arquivo: "theory"
assunto: "03_plano_segredos_aprovacao"
ordem: 3
itens_origem: ["### Microtópico 4 — Plano, segredo e aprovação de mudança"]
---

### Microtópico 4 — Plano, segredo e aprovação de mudança

Trate state e **plan salvo** como dados sensíveis: arquivos de plano podem conter valores e configuração do backend. O atributo `sensitive = true` oculta determinados valores na saída normal de CLI/UI; ele não os remove do state ou do plano. Não versionar `.tfstate`, arquivos de plano, credenciais, arquivos `.tfvars` com segredo ou `.terraform/` por padrão. Use `.gitignore` adequado, secrets store ou identidade temporária (por exemplo OIDC no pipeline), permissões mínimas e armazenamento de state com controles apropriados.

Uma sequência segura para laboratório é preparar backend/identidade, inicializar e validar, criar plano e revisar mudanças e custos, então aplicar somente o plano esperado no sandbox. Se salvar um plano para aprovação, restrinja o arquivo, canal e duração de retenção; os bytes aprovados devem corresponder ao que será aplicado, e qualquer mudança de configuração/estado exige uma nova revisão. Plano aprovado não é autorização para ignorar blast radius ou segurança dos dados.

Após apply, registre outputs não sensíveis e confirme recursos criados. Para encerrar laboratório, inspecione um plano de destroy, entenda dependências e dados persistentes e só então destrua recursos permitidos. Volumes, snapshots, buckets e backups podem sobreviver ou conter dados mesmo depois de apagar outros recursos; verifique o resultado e custos remanescentes.

