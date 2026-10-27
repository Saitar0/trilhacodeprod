---
arquivo_id: "f7-36-1-01-configuracao-providers-modulos-p01-pratica-md"
parent_key: "36.1"
tipo_arquivo: "practice"
assunto: "01_configuracao_providers_modulos"
ordem: 1
itens_origem: ["P01"]
---

### Atividade 1 — Crie uma configuração pequena e rastreável

**Desafio:** declare um recurso AWS de laboratório com entradas explícitas e uma interface simples de módulo.

**Passos:**
1. Defina região como variável com tipo e descrição; selecione uma identidade de sandbox sem access key versionada.
2. Declare provider AWS com origem e restrição de versão; rode `init` e mantenha `.terraform.lock.hcl` no Git.
3. Declare um bucket S3 privado com nome derivado de variável não secreta, tags e controles de acesso apropriados; exponha apenas output não sensível necessário.
4. Separe entradas por ambiente sem commitar valores sensíveis; use exemplo com valores fictícios.
5. Organize a configuração como root module e, se houver uma interface realmente reutilizável, extraia um child module com variáveis/outputs documentados.

**Evidências:** arquivos HCL; lockfile; `.gitignore`; diagrama da interface de módulo; saída de `fmt`, `validate` e `plan` sem credenciais.

**Verificação:** confira fonte/versão do provider, região, permissões, exposição pública, dados retornados em outputs e ausência de arquivos sensíveis no diff.

**Aceite:** configuração é compreensível e validável; provider lock está versionado; bucket não fica público por padrão; não há segredo no repositório; módulo tem interface justificada.

