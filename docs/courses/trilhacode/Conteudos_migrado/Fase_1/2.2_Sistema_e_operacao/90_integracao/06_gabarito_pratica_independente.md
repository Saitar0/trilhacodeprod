---
arquivo_id: "f1-2-2-90-integracao-06-gabarito-pratica-independente"
parent_key: "2.2"
tipo_arquivo: "answer_key_pratica"
ordem: 2
itens_origem: ["P2"]
---

**Gabarito comentado:** o processo está no grupo `app-readers`; em `uploads`, esse grupo tem `r-x`, portanto pode ler a listagem e atravessar o diretório, mas não tem `w` para criar a entrada. Isso é compatível com `EACCES` ao gravar, dadas as premissas do exercício. Ainda é preciso confirmar que `/srv/app/uploads` é o destino correto e que a aplicação deve gravar nele. Se confirmado, a mudança deve conceder somente escrita necessária à identidade ou ao grupo apropriado, apenas nesse diretório, seguindo a política da equipe. Não se deve aplicar `777`, alterar recursivamente toda a árvore nem usar `sudo` como tentativa inicial.

