---
arquivo_id: "f9-43-2-02-phalcon-versao-distribuicao-p02-pratica"
parent_key: "43.2"
tipo_arquivo: "practice"
assunto: "02_phalcon_versao_distribuicao"
ordem: 2
itens_origem: ["P02"]
---


### Atividade 2 — Identifique versão e risco de implantação Phalcon
**Contexto:** um projeto PHP declara Phalcon como dependência, mas um guia antigo manda instalar um módulo `phalcon.so`. O deploy atual usa imagem PHP e `composer install`; não há confirmação da major do projeto.

**Instruções:** faça uma lista dos arquivos e evidências que verificaria para distinguir Phalcon 5 de 6. Para cada caso, indique o caminho de distribuição esperado, um risco de incompatibilidade e qual versão do runtime PHP deve ser validada. Compare com um deployment Laravel/Slim baseado em dependências Composer.

**Entrega:** checklist de diagnóstico com evidência necessária, hipótese por versão e recomendação antes de mudar produção. Não instale nem altere dependências.

**Dica gradual:** comece por `composer.lock`/`composer.json`, depois configuração PHP e imagem de deploy. Leia a documentação da major encontrada; não deduza a versão pelo nome do framework no README.

