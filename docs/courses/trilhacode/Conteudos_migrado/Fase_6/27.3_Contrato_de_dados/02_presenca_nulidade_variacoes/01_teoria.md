---
arquivo_id: "f6-27-3-02-presenca-nulidade-variacoes-01-teoria-md"
parent_key: "27.3"
tipo_arquivo: "theory"
assunto: "02_presenca_nulidade_variacoes"
ordem: 2
itens_origem: ["### 3. Modelar presença, nulidade e variações de resposta"]
---

### 3. Modelar presença, nulidade e variações de resposta
Campo opcional e campo anulável expressam situações diferentes. `nickname?: string` permite que a propriedade esteja ausente; `nickname: string | null` exige a propriedade, mas admite valor nulo. A API e o cliente precisam concordar com o caso de cada campo. Não converta ausência em string vazia ou zero sem uma regra de produto.

Sucesso e erro também têm estruturas diferentes. Uma resposta HTTP de sucesso pode carregar um objeto de dados; falha pode incluir código estável, mensagem segura e detalhes de validação. O cliente deve considerar status HTTP e validar o corpo correspondente. Tipar só o caminho feliz deixa erros de rede, autenticação e contrato sem tratamento.

