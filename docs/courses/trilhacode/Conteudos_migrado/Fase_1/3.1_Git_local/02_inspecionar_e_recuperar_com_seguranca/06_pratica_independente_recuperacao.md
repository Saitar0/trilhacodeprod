---
arquivo_id: "f1-3-1-02-inspecionar-e-recuperar-com-seguranca-06-pratica-independente-recuperacao"
parent_key: "3.1"
tipo_arquivo: "practice"
assunto: "02_inspecionar_e_recuperar_com_seguranca"
ordem: 2
itens_origem: ["P2"]
---

### 2. Independente — escolha como recuperar cada estado

Para cada situação, complete uma tabela com: estado atual, resultado desejado, inspeção anterior, operação apropriada e risco a comunicar.

1. Um arquivo foi preparado por engano; você quer mantê-lo editado, mas não incluí-lo no próximo commit.
2. Um arquivo rastreado tem uma edição local descartável; você quer voltar ao conteúdo registrado em `HEAD`.
3. Um segredo real foi incluído em um commit e enviado ao remoto; depois alguém adicionou o caminho ao `.gitignore`.
4. Você considera executar `git reset --hard` para “limpar” um repositório cujo estado ainda não inspecionou.

**Dicas progressivas**

- Diferencie remover do staging de descartar o conteúdo na working tree. São objetivos distintos.
- `.gitignore` afeta arquivos não rastreados; uma credencial já exposta exige revogação/rotação e tratamento cuidadoso do histórico e dos sistemas que receberam o commit.

