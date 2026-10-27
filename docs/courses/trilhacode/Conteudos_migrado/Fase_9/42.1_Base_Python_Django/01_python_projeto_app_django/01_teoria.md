---
arquivo_id: "f9-42-1-01-python-projeto-app-django-01-teoria"
parent_key: "42.1"
tipo_arquivo: "theory"
assunto: "01_python_projeto_app_django"
ordem: 1
itens_origem: ["### 1. Python, projeto e app Django"]
---


### 1. Python, projeto e app Django
Python organiza código em módulos e pacotes. Um ambiente virtual isola as dependências de cada projeto; registre versões e confira a compatibilidade entre Python, Django e bibliotecas antes de iniciar um projeto.

No Django, **project** reúne configurações e aplicações para um site; um **app** agrupa uma capacidade reutilizável. `settings.py` configura apps, middleware, banco e políticas; `urls.py` encaminha caminhos; `manage.py` executa comandos do projeto. O app costuma concentrar modelos, views, configuração e migrations. Um app não é necessariamente um microsserviço: pode permanecer no mesmo processo e banco do projeto.

O comando `runserver` é para desenvolvimento. Para produção, siga o guia de deploy da versão escolhida e use um servidor WSGI/ASGI adequado, configurações seguras e infraestrutura operacional.

**Checagem:** `project` e `app` significam a mesma coisa? Não. O projeto configura uma instância do site e pode reunir vários apps.

