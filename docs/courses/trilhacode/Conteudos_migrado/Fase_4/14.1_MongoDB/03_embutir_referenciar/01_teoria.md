---
arquivo_id: "f4-14-1-03-embutir-referenciar-01-teoria"
parent_key: "14.1"
tipo_arquivo: "theory"
assunto: "03_embutir_referenciar"
ordem: 3
itens_origem: ["3. Escolha entre embutir e referenciar"]
---

### 3. Escolha entre embutir e referenciar
Embuta dados relacionados quando são lidos juntos, têm tamanho limitado e seu ciclo de vida acompanha o documento pai. Um endereço de entrega copiado para um pedido pode preservar o endereço usado naquele momento; especificações pequenas e próprias de um produto podem ficar dentro do produto.

Use referências quando o dado relacionado é compartilhado por muitos documentos, cresce sem limite, precisa de consultas próprias ou tem ciclo de vida independente. Uma lista infinita de avaliações dentro de um único produto tende a crescer continuamente; avaliações em coleção separada permitem consultar e paginar esse conjunto de forma independente.

Embedding pode reduzir consultas e manter campos relacionados no mesmo documento, mas duplicação pode exigir atualização coordenada. Referenciar reduz algumas duplicações, mas exige consulta adicional ou aggregation para combinar dados. Não aplique regras como “sempre embutir até X” sem considerar volume, frequência de leitura/escrita, tamanho e atualização.

**Erro comum:** embutir uma relação que cresce sem limite ou referenciar cada pequeno atributo e obrigar a aplicação a remontar o agregado em toda leitura.

