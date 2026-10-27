---
arquivo_id: "f9-43-2-03-comparacao-trabalho-completo-01-teoria"
parent_key: "43.2"
tipo_arquivo: "theory"
assunto: "03_comparacao_trabalho_completo"
ordem: 3
itens_origem: ["### 3. Compare com Laravel pelo trabalho completo"]
---


### 3. Compare com Laravel pelo trabalho completo
Laravel oferece mais convenções e componentes integrados para rotas, middleware, validação, ORM, migrations, autenticação/autorização e filas. Slim oferece uma superfície menor e interoperabilidade padronizada para compor partes. Phalcon oferece seu conjunto de componentes, mas implantação depende da versão; comparações antigas podem refletir a versão com extensão, enquanto a linha 6 mudou sua distribuição.

A decisão deve comparar uma mesma tarefa de ponta a ponta: rota → validação → autorização → persistência → resposta → logs e deploy. Considere:
- convenções e componentes já fornecidos;
- bibliotecas que a equipe precisará escolher e manter;
- compatibilidade PSR e dependências existentes;
- requisitos de PHP, extensões, build, servidor e hospedagem;
- curva de aprendizado, documentação, comunidade e manutenção;
- custo medido em workload equivalente, incluindo configuração e operação.

Não conclua desempenho por nome ou linguagem de implementação. Benchmark sem as mesmas regras, banco, payload, runtime, cache e configuração não representa comparação útil. Para um sistema existente, descubra a versão pelo `composer.lock`, `composer.json`, configuração PHP e processo de deploy antes de propor atualização.

**Checagem:** “Phalcon é mais rápido” é justificativa suficiente? Não. Defina workload e medição representativos e inclua custo de dependências, instalação e operação.

