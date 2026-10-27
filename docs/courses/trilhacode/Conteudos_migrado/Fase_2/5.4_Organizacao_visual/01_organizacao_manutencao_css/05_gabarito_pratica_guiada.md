---
arquivo_id: "f2-5-4-01-organizacao-manutencao-css-05-gabarito-pratica-guiada"
parent_key: "5.4"
tipo_arquivo: "answer_key_pratica"
assunto: "01_organizacao_manutencao_css"
ordem: 1
itens_origem: ["P1"]
---

**Solução comentada:** `div` não corresponde ao `article` nem ao `section`, então sua declaração de padding não tem efeito nesses elementos. `.card p` e `.profile p` têm mais especificidade que `.muted` e, por isso, a cor calculada nos dois parágrafos é `#555`. Para preservar esse resultado e reduzir duplicação, remova as duas regras específicas e altere `.muted` para `color: #555`; mantenha `.card { padding: 1rem; }`. Compare cor e espaçamento nos dois componentes antes e depois. A solução é deliberadamente localizada; não é necessário criar uma arquitetura de arquivos para este exemplo.

**Erros comuns:** supor que todo seletor escrito afeta algo; remover uma regra sem conferir a aparência calculada; confundir repetição de valor com prova de que dois componentes terão sempre a mesma intenção.

