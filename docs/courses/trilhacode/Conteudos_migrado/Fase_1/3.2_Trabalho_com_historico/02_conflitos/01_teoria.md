---
arquivo_id: "f1-3-2-02-conflitos-01-teoria"
parent_key: "3.2"
tipo_arquivo: "theory"
assunto: "02_conflitos"
ordem: 2
itens_origem: ["Conflitos"]
---

### Conflitos
Um conflito ocorre quando Git não consegue combinar automaticamente partes alteradas, por exemplo quando duas branches mudam a mesma região de um arquivo de maneiras incompatíveis. Git marca a região em conflito no arquivo. Leia o contexto, escolha ou combine as mudanças corretas, remova os marcadores e revise o resultado. Depois marque o arquivo como resolvido (`git add`) e conclua ou continue a operação. Se não sabe o que preservar, converse com quem escreveu a mudança antes de escolher.

É possível abortar operações em andamento (`git merge --abort` ou `git rebase --abort`) para voltar ao estado anterior à tentativa, quando aplicável. Confira `git status` para saber qual operação está ativa. Antes de iniciar uma integração, conclua ou preserve as mudanças locais: `git merge --abort` tenta reconstruir o estado anterior, mas mudanças não commitadas podem dificultar essa recuperação. Não apague marcadores sem validar o conteúdo.

