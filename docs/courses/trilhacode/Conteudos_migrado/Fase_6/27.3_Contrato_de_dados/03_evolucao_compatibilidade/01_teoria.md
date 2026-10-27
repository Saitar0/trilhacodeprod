---
arquivo_id: "f6-27-3-03-evolucao-compatibilidade-01-teoria-md"
parent_key: "27.3"
tipo_arquivo: "theory"
assunto: "03_evolucao_compatibilidade"
ordem: 3
itens_origem: ["### 4. Evoluir contratos sem surpreender consumidores"]
---

### 4. Evoluir contratos sem surpreender consumidores
Uma mudança aditiva — como incluir campo opcional que clientes antigos ignoram — tende a ser mais compatível do que remover ou alterar o tipo/significado de um campo usado. Ainda assim, clientes que rejeitam propriedades desconhecidas ou geradores específicos podem se comportar de modo diferente. Teste consumidores e servidor com exemplos versionados.

Para mudança incompatível, planeje migração: adicionar novo campo/rota, migrar consumidores, observar uso e só então remover o antigo quando a política permitir. Defina comportamento para cliente antigo, versão suportada, período de transição e aviso de descontinuação. Testes de contrato com exemplos válidos e inválidos ajudam a detectar divergência antes de chegar à UI.

