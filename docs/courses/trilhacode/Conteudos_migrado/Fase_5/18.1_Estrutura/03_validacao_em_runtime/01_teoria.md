---
arquivo_id: "f5-18-1-03-validacao-em-runtime-01-teoria"
parent_key: "18.1"
tipo_arquivo: "theory"
assunto: "03_validacao_em_runtime"
ordem: 3
itens_origem: ["4. Validação e limites de confiança"]
---

### 4. Validação e limites de confiança
Tudo que chega pela rede é dado externo, mesmo que o frontend use TypeScript ou compartilhe tipos com o servidor. Tipos desaparecem em runtime e não confirmam que um JSON recebido tem campos, tipos, tamanhos ou combinações válidas. Valide parâmetros de rota, query e body no servidor antes de chamar a regra de negócio. Defina campos obrigatórios, limites de tamanho, formatos, enumerações e comportamento para campos desconhecidos.

Uma falha de validação deve retornar um contrato previsível, com código/status e detalhes úteis para corrigir os campos inválidos sem ecoar dados sensíveis. Validação de formato não substitui autorização nem regra de domínio: uma entrada pode ser bem formada e ainda não permitida ou causar conflito.

