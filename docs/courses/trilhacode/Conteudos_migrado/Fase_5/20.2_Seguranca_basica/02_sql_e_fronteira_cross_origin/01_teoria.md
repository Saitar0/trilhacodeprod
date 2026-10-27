---
arquivo_id: "f5-20-2-02-sql-e-fronteira-cross-origin-01-teoria"
parent_key: "20.2"
tipo_arquivo: "theory"
assunto: "02_sql_e_fronteira_cross_origin"
ordem: 2
itens_origem: ["Microtópico 2 — SQL seguro e limites de ORM", "Microtópico 3 — CORS e fronteira do navegador"]
---

## Microtópico 2 — SQL seguro e limites de ORM
Injection ocorre quando entrada não confiável altera a estrutura do comando. Use consultas parametrizadas ou prepared statements: o SQL define a estrutura e os parâmetros fornecem valores separados. Isso continua valendo em SQL bruto chamado por ORM; uma API de ORM não é proteção automática se código concatenar entrada em uma consulta dinâmica.

Parâmetros representam valores, não identificadores SQL como nome de tabela, coluna ou ASC/DESC. Quando um identificador precisa variar, escolha entre opções fixas controladas por allowlist; sempre que possível, redesenhe a consulta para remover a necessidade de construir SQL dinâmico. Validação de formato não transforma concatenação em uma defesa confiável. Use também a conta de banco com somente os privilégios necessários.

**Exemplo:** uma busca por e-mail vincula o e-mail como valor. Um parâmetro de ordenação vindo da tela é convertido por mapa para uma coluna conhecida, como data de criação ou nome, em vez de ser concatenado literalmente.

**Erro comum:** confiar que caracteres removidos ou escapados tornam qualquer string segura para inserir no SQL.

**Checagem:** quais partes da consulta aceitam parâmetros e quais exigem mapeamento por allowlist? Valores são vinculados; identificadores dinâmicos devem ser fixos ou validados contra opções permitidas.

## Microtópico 3 — CORS e fronteira do navegador
CORS é um mecanismo de navegador que permite ao servidor declarar quais origens de script podem ler determinadas respostas cross-origin. Não autentica usuário, não autoriza recursos e não é firewall para chamadas feitas por outros clientes. Algumas requisições simples ainda podem ser enviadas mesmo que o navegador depois impeça o script de ler a resposta. Portanto, CORS não substitui controles de servidor nem defesa contra CSRF.

Permita apenas origens necessárias para os recursos que precisam de leitura cross-origin. Se a API exige credenciais do navegador, retorne uma origem explicitamente permitida e habilite credenciais conforme o protocolo; wildcard não pode ser usado como origem em respostas credenciadas. Não reflita qualquer valor de Origin recebido sem validação. Para recursos públicos sem credenciais, wildcard pode ser adequado se essa exposição for intencional.

**Exemplo:** uma API permite leitura com cookie apenas do domínio aprovado da interface. Uma ferramenta de linha de comando pode continuar chamando o endpoint: CORS não é mecanismo de autenticação ou bloqueio de rede.

**Erro comum:** liberar qualquer origem porque “a API já exige login”, ou supor que CORS impeça um atacante de enviar toda requisição.

**Checagem:** o que o navegador faz quando uma origem não está autorizada? Impede a leitura da resposta pelo script; a API ainda precisa validar identidade, permissão e proteção contra requisições forjadas.

