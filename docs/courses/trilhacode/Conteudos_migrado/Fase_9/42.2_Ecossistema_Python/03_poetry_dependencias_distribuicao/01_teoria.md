---
arquivo_id: "f9-42-2-03-poetry-dependencias-distribuicao-01-teoria"
parent_key: "42.2"
tipo_arquivo: "theory"
assunto: "03_poetry_dependencias_distribuicao"
ordem: 3
itens_origem: ["### 3. Poetry: dependências e distribuição"]
---


### 3. Poetry: dependências e distribuição
Poetry usa `pyproject.toml` para declarar metadados, restrições de Python e dependências; `poetry.lock` registra versões resolvidas para instalações consistentes do aplicativo. `poetry install` instala o conjunto travado quando o lockfile existe. Poetry não é o interpretador Python e não instala automaticamente o runtime necessário ao projeto.

Para **aplicações**, versionar o lockfile costuma melhorar a repetibilidade de desenvolvimento, CI e deploy. Para **bibliotecas**, consumidores resolvem dependências próprias conforme as restrições publicadas; o lockfile do autor não controla a instalação feita pelo projeto consumidor. Biblioteca ainda pode manter lock para repetir o próprio ambiente de desenvolvimento/testes.

Grupos de dependências ajudam a distinguir execução, desenvolvimento e documentação, mas o pipeline deve instalar o grupo adequado. Mudanças devem revisar tanto `pyproject.toml` quanto lockfile e testar atualização de maneira deliberada.

Comparação aproximada: `pyproject.toml` e Poetry cobrem parte dos papéis de manifesto/gerenciador e lockfile que npm ou pnpm têm em Node. Formato, resolução, grupos e distribuição não são idênticos.

**Checagem:** Poetry instala o Python declarado no projeto? Não; a ferramenta precisa encontrar um interpretador compatível no ambiente.

