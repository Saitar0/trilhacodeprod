---
arquivo_id: "f3-7-2-03-responsabilidades-coesao-01-teoria"
parent_key: "7.2"
tipo_arquivo: "theory"
assunto: "03_responsabilidades_coesao"
ordem: 3
itens_origem: ["4. Responsabilidades, coesão e dependências"]
---

### 4. Responsabilidades, coesão e dependências
Divida por responsabilidade coesa, não por uma regra automática de quantidade de linhas. Em uma lista de tarefas, por exemplo, `tarefas.js` pode transformar dados sem acessar o DOM; `interface-tarefas.js` pode registrar eventos e atualizar a página; `app.js` conecta e inicia as partes. O ponto de entrada coordena, mas não precisa conter toda a lógica.

Uma dependência aponta do consumidor para o módulo que fornece a função. Se dois módulos precisam importar um ao outro, há um ciclo; reavalie as responsabilidades e considere extrair a função compartilhada para um módulo menor. Evite também arquivos “utilitários” que acumulam funções sem relação.

**Erro comum:** criar um arquivo para cada função sem considerar o uso. Isso aumenta a navegação sem necessariamente tornar responsabilidades mais claras.

