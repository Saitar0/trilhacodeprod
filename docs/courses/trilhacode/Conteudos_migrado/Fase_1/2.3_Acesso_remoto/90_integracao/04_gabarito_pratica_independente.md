---
arquivo_id: "f1-2-3-90-integracao-04-gabarito-pratica-independente"
parent_key: "2.3"
tipo_arquivo: "answer_key_pratica"
ordem: 2
itens_origem: ["P2"]
---

**Referência para autocorreção:** uma sequência razoável identifica a URL remota (`git remote -v` ou `git remote get-url origin`); confere localmente quais pares de chave existem sem abrir nem copiar a privada; verifica se a chave pública correspondente foi cadastrada na conta correta; confere qual chave o cliente oferece, seguindo os comandos oficiais do sistema; executa `ssh -T git@github.com`; e compara qualquer impressão digital de host com a publicada pelo GitHub. A saída de `ssh-add -l` pode ajudar a inspecionar chaves carregadas, mas lista vazia, isoladamente, não prova que não exista uma chave padrão utilizável. Se o teste autenticar, o GitHub pode informar que não oferece acesso shell; essa mensagem é compatível com o teste bem-sucedido. Se persistir a falha, registre sistema, cliente e mensagem sem incluir segredos.

