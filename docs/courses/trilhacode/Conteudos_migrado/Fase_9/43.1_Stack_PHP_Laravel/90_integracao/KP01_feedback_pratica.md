---
arquivo_id: "f9-43-1-90-integracao-kp01-feedback-pratica"
parent_key: "43.1"
tipo_arquivo: "answer_key_pratica"
assuntos: ["01_php_composer_versoes", "02_ciclo_requisicao_laravel"]
ordem: 1
itens_origem: ["P01"]
---


**Feedback de referência:** a rota aponta caminho e handler; middleware filtra a requisição; controller coordena; Eloquent lê o modelo; policy decide ação sobre o pedido; resposta retorna dados. O `composer.json` declara restrições, enquanto `composer.lock` revela versões resolvidas do projeto.

**Erro comum:** assumir que qualquer usuário autenticado pode acessar qualquer `Order` encontrado pelo binding.

