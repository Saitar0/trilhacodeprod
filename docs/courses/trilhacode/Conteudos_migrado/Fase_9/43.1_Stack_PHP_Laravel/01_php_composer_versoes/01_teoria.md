---
arquivo_id: "f9-43-1-01-php-composer-versoes-01-teoria"
parent_key: "43.1"
tipo_arquivo: "theory"
assunto: "01_php_composer_versoes"
ordem: 1
itens_origem: ["### 1. PHP, Composer e versões"]
---


### 1. PHP, Composer e versões
PHP executa código no servidor dentro de um runtime e de uma configuração de servidor compatível. Composer declara e resolve dependências, mantém `composer.lock` para instalações reproduzíveis de uma aplicação e configura autoload segundo o ecossistema PHP. Composer não é o runtime PHP; verifique versão instalada, extensões exigidas e restrições declaradas no `composer.json`.

Diferencie código PHP legado de uma aplicação Laravel atual. O roadmap cita PHP 7.4 como tecnologia que pode aparecer em manutenção de sistemas antigos; essa versão está fora de suporte e não deve ser a base de uma aplicação nova. Na consulta de 15/10/2026, Laravel 13 exige PHP 8.3 ou superior; PHP 8.3 está em suporte de segurança e versões mais novas podem estar disponíveis. Para produção real, confira o suporte de Laravel, PHP, extensões e dependências na data de início e fixe versões compatíveis no projeto.

