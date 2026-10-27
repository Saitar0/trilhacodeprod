---
arquivo_id: "f9-43-2-02-phalcon-versao-distribuicao-01-teoria"
parent_key: "43.2"
tipo_arquivo: "theory"
assunto: "02_phalcon_versao_distribuicao"
ordem: 2
itens_origem: ["### 2. Phalcon: versão e forma de distribuição"]
---


### 2. Phalcon: versão e forma de distribuição
O nome Phalcon cobre versões cuja instalação e implementação diferem. Isso muda o que se deve verificar num repositório ou numa proposta de adoção:

| Linha | Distribuição descrita na documentação | Implicação para avaliação |
|---|---|---|
| Phalcon 5 | Extensão PHP; a versão 5.18 documenta instalação/ativação do módulo compatível com a versão e build do PHP | Verifique `php.ini`, extensões, arquitetura e suporte do ambiente de deploy; não basta executar `composer install` |
| Phalcon 6 | Pacote PHP instalado pelo Composer; a documentação 6.0 descreve implementação em PHP sem compilar/ativar extensão Phalcon | Leia o `composer.json`/lockfile e requisitos PHP da major; dependências do projeto ainda precisam ser compatíveis |

As duas linhas expõem componentes web e de persistência/ORM, mas APIs, instalação e manutenção devem ser avaliadas na major efetivamente usada. Em documentação consultada em 15/10/2026, Phalcon 6 indica PHP 8.1 ou superior; esse mínimo não garante suporte de segurança do próprio runtime. Confira também a matriz oficial vigente de PHP e a disponibilidade da versão para o ambiente de produção.

**Checagem:** pode-se usar instrução de instalação de extensão da versão 5 sem confirmar a major? Não. Na versão 6 documentada, Phalcon é dependência Composer; a instalação difere.

