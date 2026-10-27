---
arquivo_id: "f4-14-1-04-integridade-referencial-validacao-01-teoria"
parent_key: "14.1"
tipo_arquivo: "theory"
assunto: "04_integridade_referencial_validacao"
ordem: 4
itens_origem: ["4. Combine flexibilidade com integridade e escolha de tecnologia"]
---

### 4. Combine flexibilidade com integridade e escolha de tecnologia
Validação de schema pode impor tipos e faixas de valores, por exemplo exigir que preço seja numérico e não negativo. O MongoDB rejeita inserções ou atualizações inválidas por padrão quando uma regra de validação está configurada, embora as opções possam ser ajustadas. Decida quais campos precisam de estrutura rígida e quais realmente variam.

Referências em documentos não criam automaticamente a mesma garantia de chave estrangeira típica de um SGBD relacional. Integridade entre coleções pode depender da aplicação, constraints disponíveis e operações transacionais em cenários suportados. Se relações, integridade referencial e consultas combinadas dominam o problema, um banco relacional pode representar melhor essas regras.

MongoDB oferece transações em deployments suportados, mas isso não torna irrelevante a modelagem: decida quais dados formam um agregado, quais atualizações devem ocorrer juntas e qual consistência as leituras exigem. Não escolha um banco apenas por alegações genéricas de velocidade ou escalabilidade; compare consultas, crescimento, consistência, operação e custo de duplicação.

**Erro comum:** assumir que flexibilidade significa ausência de validação ou que trocar para documentos remove decisões de integridade.

