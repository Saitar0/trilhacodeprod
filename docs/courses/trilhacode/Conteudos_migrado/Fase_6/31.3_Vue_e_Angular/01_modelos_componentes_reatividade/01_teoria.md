---
arquivo_id: "f6-31-3-01-modelos-componentes-reatividade-01-teoria-md"
parent_key: "31.3"
tipo_arquivo: "theory"
assunto: "01_modelos_componentes_reatividade"
ordem: 1
itens_origem: ["## Microtópico 1 — Compare como os frameworks descrevem a interface"]
---

## Microtópico 1 — Compare como os frameworks descrevem a interface
Vue 3 usa componentes, templates e um sistema de reatividade. Em componentes de arquivo único, template, lógica e estilo podem ficar juntos. Há duas formas oficiais de organizar a lógica: **Options API**, que agrupa opções como dados e métodos, e **Composition API**, que usa funções como `ref()` e hooks de ciclo de vida. `<script setup>` é uma forma comum de escrever componentes com Composition API. Options API continua suportada; Composition API facilita agrupar lógica por funcionalidade quando um componente cresce.

Angular organiza aplicações com componentes e templates em TypeScript e inclui mecanismos integrados para serviços, injeção de dependências, roteamento e ferramentas de desenvolvimento. Componentes standalone importam diretamente as dependências do template e são recomendados pela equipe Angular para código novo; `NgModule` continua importante para compreender projetos existentes.

Os dois frameworks resolvem desafios parecidos — composição, estado, eventos, formulários, acessibilidade e chamadas a serviços — com convenções diferentes. O modelo React ajuda a entender componentização e fluxo de dados, mas não ensina automaticamente a sintaxe de templates do Vue ou o sistema de DI do Angular.

