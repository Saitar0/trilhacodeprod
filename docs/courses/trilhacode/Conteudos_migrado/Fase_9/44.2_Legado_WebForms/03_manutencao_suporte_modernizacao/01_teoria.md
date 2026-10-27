---
arquivo_id: "f9-44-2-03-manutencao-suporte-modernizacao-01-teoria"
parent_key: "44.2"
tipo_arquivo: "theory"
assunto: "03_manutencao_suporte_modernizacao"
ordem: 3
itens_origem: ["### 3. Manutenção, suporte e modernização"]
---


### 3. Manutenção, suporte e modernização
WebForms não é simplesmente uma versão antiga de ASP.NET Core. Ele usa ASP.NET/.NET Framework e seu modelo de página; ASP.NET Core moderno tem pipeline, hosting e composição diferentes. Um sistema WebForms pode permanecer em operação se o runtime, Windows, dependências e controles estiverem suportados e protegidos. O suporte do .NET Framework acompanha a política da versão/Windows hospedeiro; verifique a matriz completa antes de alegar que todo WebForms está sem suporte ou que qualquer host está coberto.

Modernização pode começar com inventário e separação de regra de negócio do code-behind. Uma equipe pode mover partes de forma incremental, por exemplo criando uma aplicação ASP.NET Core ao lado da aplicação Framework, roteando novos endpoints para o sistema novo e mantendo as páginas restantes no legado. Isso exige proxy/roteamento, autenticação compartilhada, compatibilidade de dados, observabilidade, reversão e plano de retirar o legado; coexistência não é gratuita. Não é necessário migrar tudo para concluir esta unidade.

Para cada candidato, documente: target .NET Framework e Windows; dependências/controles de terceiros; página e evento envolvidos; fonte de estado; regras de negócio acopladas; dados compartilhados; restrições de teste/deploy; risco e métrica que justificaria modernizar. Comece com uma fatia delimitada e mantenha um retorno verificável.

**Checagem:** o número da versão do .NET Framework sozinho prova que o sistema está dentro de suporte? Não; sistema operacional, nível de atualização, dependências e política aplicável também contam.

