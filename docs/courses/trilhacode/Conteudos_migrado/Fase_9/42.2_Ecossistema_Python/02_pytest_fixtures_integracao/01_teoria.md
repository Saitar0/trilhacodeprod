---
arquivo_id: "f9-42-2-02-pytest-fixtures-integracao-01-teoria"
parent_key: "42.2"
tipo_arquivo: "theory"
assunto: "02_pytest_fixtures_integracao"
ordem: 2
itens_origem: ["### 2. pytest: testes, fixtures e níveis de integração"]
---


### 2. pytest: testes, fixtures e níveis de integração
pytest descobre e executa testes Python e fornece assertions, parametrização e **fixtures**. Uma fixture prepara dependências ou estado e pode limpar recursos ao final. Escopo de fixture (função, classe, módulo ou sessão) determina quanto estado é compartilhado; quanto maior o escopo, maior a necessidade de evitar acoplamento entre testes.

Use testes unitários para lógica isolada e rápidos; testes de integração para validar colaboração real com banco, broker ou API quando essa fronteira for o risco. Mockar um broker não confirma que configuração, rede e serialização funcionam com um broker real. Para integração, use serviço isolado, credenciais de teste e limpeza reproduzível; evite depender de produção.

Comparação aproximada: pytest ocupa o papel de runner/ferramentas de teste como Jest ou Vitest. Fixtures lembram setup compartilhado, mas têm regras de descoberta, dependência e escopo próprias.

**Checagem:** uma fixture de sessão que cria dados compartilhados torna os testes mais isolados? Nem sempre; dados mutáveis compartilhados podem causar dependência pela ordem dos testes.

