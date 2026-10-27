---
arquivo_id: "f6-31-3-02-versoes-padroes-legado-01-teoria-md"
parent_key: "31.3"
tipo_arquivo: "theory"
assunto: "02_versoes_padroes_legado"
ordem: 2
itens_origem: ["## Microtópico 2 — Reconheça versões, padrões atuais e legado"]
---

## Microtópico 2 — Reconheça versões, padrões atuais e legado
Em Vue, `ref()` e `reactive()` criam estado reativo na Composition API; templates acompanham mudanças e atualizam a interface. Em Angular atual, componentes e templates se relacionam com estado e serviços por mecanismos próprios do framework, incluindo injeção de dependências. Ao ler um código, identifique o padrão e a versão em vez de traduzir mentalmente cada API para React.

Vue 2 chegou ao fim de vida em **31 de dezembro de 2023**. Ele permanece em aplicações existentes e pode aparecer em manutenção ou migração, mas não deve ser apresentado como a base padrão para projetos novos. Vue 3 é a versão atual. Angular moderno recomenda standalone para código novo, embora bases anteriores usem `NgModule`. Consulte documentação da versão concreta antes de aplicar uma receita a um repositório legado.

Compare ecossistemas pelo problema: convenções da equipe, dependências, manutenção, acessibilidade e requisitos do produto. Este panorama serve para reconhecer modelos e ler documentação; não pretende eleger um framework universalmente superior nem substituir um curso de implementação completo.

