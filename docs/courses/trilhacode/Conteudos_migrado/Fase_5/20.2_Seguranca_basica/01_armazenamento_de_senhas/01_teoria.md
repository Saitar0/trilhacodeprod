---
arquivo_id: "f5-20-2-01-armazenamento-de-senhas-01-teoria"
parent_key: "20.2"
tipo_arquivo: "theory"
assunto: "01_armazenamento_de_senhas"
ordem: 1
itens_origem: ["Microtópico 1 — Armazenamento de senhas"]
---

## Microtópico 1 — Armazenamento de senhas
Senha não deve ser armazenada em texto puro nem protegida por criptografia reversível. Para verificar uma senha depois, use uma função adaptativa de hash para senhas, apropriada para tornar cada tentativa de adivinhação cara. A recomendação atual da OWASP para novos sistemas é Argon2id, com parâmetros calibrados ao ambiente; a configuração mínima indicada na referência é 19 MiB de memória, duas iterações e paralelismo 1. Bibliotecas costumam gerar e guardar salt único junto com o hash codificado; não invente formato ou comparação por conta própria.

SHA-256 sem função adaptativa não é adequado para senhas: é rápido e permite testar muitas combinações. A comparação e a verificação de parâmetros devem ser feitas por biblioteca mantida. Calibre o custo no hardware e carga esperados, verificando que o login continua utilizável sem reduzir a proteção abaixo das recomendações atuais. Uma eventual migração de parâmetros pode ocorrer no próximo login válido, conforme o formato e a biblioteca usados.

Política de senha, recuperação de conta e MFA são decisões de autenticação aprofundadas na unidade anterior; aqui o foco é guardar e verificar credenciais de modo resistente a vazamentos do banco.

**Exemplo:** no cadastro, a biblioteca gera hash com salt e parâmetros atuais; no login, a mesma biblioteca verifica a senha candidata contra o hash armazenado sem recuperar a senha original.

**Erro comum:** aplicar SHA-256 a todas as senhas, inclusive usando um salt fixo para o sistema, ou acreditar que criptografar senhas permite verificá-las com mais segurança.

**Checagem:** se o banco vazar, a aplicação consegue recuperar as senhas originais? Não; deve guardar apenas um hash adaptativo validável pela biblioteca.

