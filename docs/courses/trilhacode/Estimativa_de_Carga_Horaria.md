---
title: "Estimativa de carga horária"
aliases:
  - Carga horária do curso
tags:
  - trilhas
  - estrutura-curricular
tipo: guia
status: planejamento
---

# Estimativa de carga horária

> [!abstract] Escopo
> Estimativa inicial do tempo de estudo de uma pessoa iniciante que acompanha a trilha e conclui atividades e projetos no escopo mínimo definido. Não representa duração de aulas gravadas nem tempo de produção dos conteúdos. A pasta `trilhacodeprod` foi excluída da análise.

## Método

- A hora é de estudo ativo: leitura/estudo, exercício, tentativa e erro, depuração, correção e revisão necessários para atingir o critério de conclusão.
- As faixas consideram uma pessoa iniciante, sem experiência prévia em programação, mas com familiaridade básica com computador e internet, conforme o público da trilha.
- Unidade obrigatória de profundidade média: **1–2 h**; alta: **2–4 h**; repertório: **30–60 min**. Revisita: **30–60 min**. Prática guiada média: **1,5–2,5 h**; prática guiada alta: **2,5–4,5 h**.
- Projetos recebem estimativa própria pelo escopo incremental mínimo e evidências exigidas. As estimativas pressupõem reaproveitar o trabalho anterior, não refazer fases já concluídas.
- A referência de planejamento é o ponto médio arredondado para 15 minutos por unidade. Na plataforma, ela é exibida como tempo aproximado de estudo ativo, não como duração de vídeo; o intervalo continua sendo a estimativa editorial para planejamento.
- Não inclui pausas, estudo opcional fora do escopo, recuperação de tipos do Trilho B além do percurso recomendado, atrasos de infraestrutura individual, nem desenvolvimento das aulas pelo autor.
- As faixas são estimativas iniciais, não promessa de duração nem prazo universal. Medir a Fase 1 e ajustar com dados de estudantes antes de divulgar um total rígido.

## Total da trilha

**313–560 horas**; referência central de planejamento: **436 horas** para as 131 unidades e projetos incrementais/Trilho B previstos, com uma escolha de projeto B em cada fase disponível e T6 na Fase 10.

Equivalências de calendário (sem contar pausas):

| Dedicação semanal | Pela referência central |
|---:|---:|
| 5 h/semana | cerca de 87 semanas |
| 10 h/semana | cerca de 44 semanas |
| 15 h/semana | cerca de 29 semanas |
| 20 h/semana | cerca de 22 semanas |

## Faixa por fase

| Fase | Unidades | Estimativa | Referência central |
|---|---:|---:|---:|
| [Fase 1](Fase_1_Base_Tecnica.md) | 10 | 16,5–30 h | 23 h |
| [Fase 2](Fase_2_Base_da_Web_HTML_CSS.md) | 7 | 12,5–24,5 h | 18 h |
| [Fase 3](Fase_3_Base_da_Web_JS_TS_Node.md) | 14 | 33–59,5 h | 46 h |
| [Fase 4](Fase_4_Dados_e_Bancos.md) | 17 | 39–72 h | 56 h |
| [Fase 5](Fase_5_Backend_e_Arquitetura.md) | 20 | 45–79 h | 62 h |
| [Fase 6](Fase_6_Frontend_Moderno.md) | 20 | 39–71 h | 55 h |
| [Fase 7](Fase_7_Infra_Deploy_e_Cloud.md) | 7 | 13–26 h | 20 h |
| [Fase 8](Fase_8_Infra_Operacao.md) | 8 | 23–39,5 h | 31 h |
| [Fase 9](Fase_9_Escala_Mensageria_e_Mercado.md) | 16 | 31,5–53 h | 42 h |
| [Fase 10](Fase_10_IA_Aplicada_e_Posicionamento.md) | 12 | 60,5–105,5 h | 83 h |

## Faixas dos projetos

O cálculo inclui os marcos incrementais do Trilho A e uma entrega do Trilho B
em cada fase prevista. A faixa pressupõe evolução do mesmo projeto principal e
execução da fatia mínima do projeto B.

| Unidade | Trilha | Estimativa |
|---:|---|---:|
| 3.5 | A — ambiente e repositório | 4–6 h |
| 8.5 | A — interface estática | 6–10 h |
| 8.6 | B — protótipo web | 8–12 h |
| 16.2 | A — evolução com dados | 6–10 h |
| 16.3 | B — modelo de dados | 8–14 h |
| 24.3 | A — evolução de backend | 8–12 h |
| 24.4 | B — API por tipo | 12–18 h |
| 31.4 | A — integração frontend | 8–12 h |
| 31.5 | B — interface React | 8–14 h |
| 39.2 | A — operação e observabilidade | 10–16 h |
| 39.3 | B — implantação | 8–14 h |
| 46.2 | A — mensageria e resiliência | 12–18 h |
| 46.3 | B — processamento assíncrono | 10–16 h |
| 52.1 | A — projeto final com IA | 30–50 h |
| 52.2 | B — projeto de IA (T6) | 20–35 h |

O percurso base não inclui projetos extras de recuperação. Se algum tipo T1–T5
ficar pendente, a versão de recuperação da Fase 9 acrescenta tempo conforme o
escopo e a tecnologia já disponíveis para a pessoa.

## Estimativa por unidade

A referência em minutos está no campo editorial `estimativa_minutos` de cada unidade em `Conteudos/Fase_N`. No JSON de importação, esse valor é mapeado para `estimated_minutes`, exibido ao estudante como minutos aproximados de estudo. A faixa e o ponto de referência ficam também no submódulo canônico da fase.

| Fase | Unidade | Faixa | Referência |
|---:|---:|---:|---:|
| 1 | 1.1 | 1–2 h | 1,5 h |
| 1 | 1.2 | 1–2 h | 1,5 h |
| 1 | 2.1 | 2,5–4,5 h | 3,5 h |
| 1 | 2.2 | 1–2 h | 1,5 h |
| 1 | 2.3 | 1–2 h | 1,5 h |
| 1 | 3.1 | 2–4 h | 3 h |
| 1 | 3.2 | 1–2 h | 1,5 h |
| 1 | 3.3 | 2,5–4,5 h | 3,5 h |
| 1 | 3.4 | 30–60 min | 45 min |
| 1 | 3.5 | 4–6 h | 5 h |
| 2 | 4.1 | 2–4 h | 3 h |
| 2 | 4.2 | 2–4 h | 3 h |
| 2 | 4.3 | 1–2 h | 1,5 h |
| 2 | 5.1 | 2–4 h | 3 h |
| 2 | 5.2 | 2,5–4,5 h | 3,5 h |
| 2 | 5.3 | 2–4 h | 3 h |
| 2 | 5.4 | 1–2 h | 1,5 h |
| 3 | 6.1 | 2–4 h | 3 h |
| 3 | 6.2 | 2–4 h | 3 h |
| 3 | 6.3 | 2–4 h | 3 h |
| 3 | 6.4 | 1–2 h | 1,5 h |
| 3 | 7.1 | 2–4 h | 3 h |
| 3 | 7.2 | 1–2 h | 1,5 h |
| 3 | 7.3 | 2–4 h | 3 h |
| 3 | 7.4 | 30–60 min | 45 min |
| 3 | 7.5 | 1,5–2,5 h | 2 h |
| 3 | 8.1 | 2–4 h | 3 h |
| 3 | 8.2 | 2–4 h | 3 h |
| 3 | 8.3 | 1–2 h | 1,5 h |
| 3 | 8.5 | 6–10 h | 8 h |
| 3 | 8.6 | 8–12 h | 10 h |
| 4 | 9.1 | 2–4 h | 3 h |
| 4 | 9.2 | 2–4 h | 3 h |
| 4 | 9.3 | 2–4 h | 3 h |
| 4 | 10.1 | 2–4 h | 3 h |
| 4 | 10.2 | 2,5–4,5 h | 3,5 h |
| 4 | 11.3 | 1,5–2,5 h | 2 h |
| 4 | 11.1 | 2,5–4,5 h | 3,5 h |
| 4 | 11.2 | 2,5–4,5 h | 3,5 h |
| 4 | 12.1 | 1–2 h | 1,5 h |
| 4 | 12.2 | 2–4 h | 3 h |
| 4 | 12.3 | 2–4 h | 3 h |
| 4 | 13.1 | 30–60 min | 45 min |
| 4 | 14.1 | 1–2 h | 1,5 h |
| 4 | 15.1 | 1–2 h | 1,5 h |
| 4 | 16.1 | 30–60 min | 45 min |
| 4 | 16.2 | 6–10 h | 8 h |
| 4 | 16.3 | 8–14 h | 11 h |
| 5 | 17.1 | 2–4 h | 3 h |
| 5 | 17.2 | 1,5–2,5 h | 2 h |
| 5 | 18.1 | 2–4 h | 3 h |
| 5 | 18.2 | 1–2 h | 1,5 h |
| 5 | 18.3 | 1–2 h | 1,5 h |
| 5 | 19.1 | 1–2 h | 1,5 h |
| 5 | 19.2 | 1–2 h | 1,5 h |
| 5 | 20.1 | 2–4 h | 3 h |
| 5 | 20.2 | 2–4 h | 3 h |
| 5 | 20.3 | 1–2 h | 1,5 h |
| 5 | 21.1 | 1–2 h | 1,5 h |
| 5 | 22.1 | 1–2 h | 1,5 h |
| 5 | 22.2 | 1–2 h | 1,5 h |
| 5 | 23.1 | 1–2 h | 1,5 h |
| 5 | 23.2 | 1–2 h | 1,5 h |
| 5 | 23.3 | 1–2 h | 1,5 h |
| 5 | 24.1 | 2–4 h | 3 h |
| 5 | 24.2 | 2,5–4,5 h | 3,5 h |
| 5 | 24.3 | 8–12 h | 10 h |
| 5 | 24.4 | 12–18 h | 15 h |
| 6 | 25.1 | 2–4 h | 3 h |
| 6 | 25.2 | 2–4 h | 3 h |
| 6 | 26.1 | 2–4 h | 3 h |
| 6 | 26.2 | 1–2 h | 1,5 h |
| 6 | 27.1 | 2–4 h | 3 h |
| 6 | 27.2 | 2,5–4,5 h | 3,5 h |
| 6 | 27.3 | 1–2 h | 1,5 h |
| 6 | 27.4 | 1–2 h | 1,5 h |
| 6 | 28.1 | 1–2 h | 1,5 h |
| 6 | 28.2 | 1–2 h | 1,5 h |
| 6 | 28.3 | 1–2 h | 1,5 h |
| 6 | 29.1 | 1–2 h | 1,5 h |
| 6 | 29.2 | 1,5–2,5 h | 2 h |
| 6 | 30.1 | 1–2 h | 1,5 h |
| 6 | 30.2 | 1–2 h | 1,5 h |
| 6 | 31.1 | 1–2 h | 1,5 h |
| 6 | 31.2 | 30–60 min | 45 min |
| 6 | 31.3 | 30–60 min | 45 min |
| 6 | 31.4 | 8–12 h | 10 h |
| 6 | 31.5 | 8–14 h | 11 h |
| 7 | 32.1 | 2–4 h | 3 h |
| 7 | 32.2 | 2–4 h | 3 h |
| 7 | 33.1 | 1–2 h | 1,5 h |
| 7 | 34.1 | 2–4 h | 3 h |
| 7 | 35.1 | 2–4 h | 3 h |
| 7 | 36.1 | 2–4 h | 3 h |
| 7 | 36.2 | 2–4 h | 3 h |
| 8 | 37.1 | 30–60 min | 45 min |
| 8 | 37.2 | 30–60 min | 45 min |
| 8 | 37.3 | 30–60 min | 45 min |
| 8 | 38.1 | 1–2 h | 1,5 h |
| 8 | 38.2 | 1,5–2,5 h | 2 h |
| 8 | 39.1 | 1–2 h | 1,5 h |
| 8 | 39.2 | 10–16 h | 13 h |
| 8 | 39.3 | 8–14 h | 11 h |
| 9 | 40.1 | 1–2 h | 1,5 h |
| 9 | 40.2 | 30–60 min | 45 min |
| 9 | 40.3 | 1–2 h | 1,5 h |
| 9 | 41.1 | 1–2 h | 1,5 h |
| 9 | 41.2 | 1–2 h | 1,5 h |
| 9 | 42.1 | 30–60 min | 45 min |
| 9 | 42.2 | 30–60 min | 45 min |
| 9 | 42.3 | 30–60 min | 45 min |
| 9 | 43.1 | 30–60 min | 45 min |
| 9 | 43.2 | 30–60 min | 45 min |
| 9 | 44.1 | 30–60 min | 45 min |
| 9 | 44.2 | 30–60 min | 45 min |
| 9 | 45.1 | 30–60 min | 45 min |
| 9 | 46.1 | 1–2 h | 1,5 h |
| 9 | 46.2 | 12–18 h | 15 h |
| 9 | 46.3 | 10–16 h | 13 h |
| 10 | 47.1 | 1,5–2,5 h | 2 h |
| 10 | 48.1 | 1–2 h | 1,5 h |
| 10 | 48.2 | 1–2 h | 1,5 h |
| 10 | 49.1 | 1–2 h | 1,5 h |
| 10 | 50.1 | 1–2 h | 1,5 h |
| 10 | 51.1 | 1–2 h | 1,5 h |
| 10 | 52.1 | 30–50 h | 40 h |
| 10 | 52.2 | 20–35 h | 27,5 h |
| 10 | 53.1 | 1–2 h | 1,5 h |
| 10 | 53.2 | 1–2 h | 1,5 h |
| 10 | 53.3 | 1–2 h | 1,5 h |
| 10 | 53.4 | 1–2 h | 1,5 h |

## Critérios de calibração após a produção

- Registrar o tempo real apenas para estudo que alcança o critério; separar abandono, interrupções e problema técnico externo.
- Após a primeira turma, comparar a mediana e a dispersão por unidade com a faixa estimada; ajustar quando a mediana ficar fora da faixa ou quando a dispersão mostrar que a tarefa está ambígua.
- Projetos devem manter sua faixa por escopo (e não uma média única para todos os tipos); estudantes que fazem projetos de recuperação acrescentam horas além do percurso base.

