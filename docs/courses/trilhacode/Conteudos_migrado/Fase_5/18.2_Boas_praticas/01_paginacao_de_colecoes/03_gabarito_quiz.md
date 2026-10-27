---
arquivo_id: "f5-18-2-01-paginacao-de-colecoes-03-gabarito-quiz"
parent_key: "18.2"
tipo_arquivo: "answer_key"
assunto: "01_paginacao_de_colecoes"
ordem: 1
itens_origem: ["Q1", "Q2", "Q3"]
---

**Resposta:** para limitar trabalho, memória, latência e tamanho do payload mesmo quando o cliente pede um volume excessivo.  
   **Feedback:** o servidor define tamanho padrão e máximo; não deve confiar que todo consumidor enviará um limite seguro.

**Resposta:** um critério de desempate único, como o ID, usado junto com a data.  
   **Feedback:** uma ordem não determinística pode fazer itens empatados reaparecerem ou serem omitidos entre páginas.

**Resposta:** não. Base64 é codificação, não segredo nem proteção contra alteração.  
   **Feedback:** o cliente não deve depender da estrutura interna do cursor; ele não deve funcionar como autorização.

