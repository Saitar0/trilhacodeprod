import type { PublicTypedActivity } from "./types";

const versionRef = "question-source-sha256:" + "a".repeat(64);

export const typedActivityFixtures: PublicTypedActivity[] = [
  {
    activity_ref: "f1-fundamentos-multipla-escolha",
    version_ref: versionRef,
    title: "Escolha uma alternativa",
    order: 0,
    type: "multiple_choice",
    prompt: "Qual opção representa o exemplo apresentado?",
    options: [
      { option_id: "opt-a", text: "Primeira alternativa demonstrativa" },
      { option_id: "opt-b", text: "Segunda alternativa demonstrativa" },
    ],
  },
  {
    activity_ref: "f1-fundamentos-resposta-curta",
    version_ref: versionRef,
    title: "Resposta curta",
    order: 1,
    type: "short_answer",
    prompt: "Escreva uma observação curta sobre o exemplo.",
    instructions: "Use suas próprias palavras.",
  },
  {
    activity_ref: "f1-fundamentos-discursiva",
    version_ref: versionRef,
    title: "Resposta discursiva",
    order: 2,
    type: "discursive",
    prompt: "Descreva como você investigaria um problema.",
    instructions: "Organize a resposta em parágrafos.",
  },
  {
    activity_ref: "f1-fundamentos-associacao",
    version_ref: versionRef,
    title: "Associe os conceitos",
    order: 3,
    type: "matching",
    prompt: "Relacione cada conceito demonstrativo à descrição correspondente.",
    left_items: [
      { ref: "left-one", text: "Conceito A" },
      { ref: "left-two", text: "Conceito B" },
    ],
    right_items: [
      { ref: "right-one", text: "Descrição um" },
      { ref: "right-two", text: "Descrição dois" },
    ],
  },
  {
    activity_ref: "f1-fundamentos-ordenacao",
    version_ref: versionRef,
    title: "Organize as etapas",
    order: 4,
    type: "ordering",
    prompt: "Organize os itens demonstrativos na sequência que considerar adequada.",
    items: [
      { ref: "step-one", text: "Etapa demonstrativa A" },
      { ref: "step-two", text: "Etapa demonstrativa B" },
      { ref: "step-three", text: "Etapa demonstrativa C" },
    ],
  },
  {
    activity_ref: "f1-fundamentos-revisao",
    version_ref: versionRef,
    title: "Revisão formativa",
    order: 5,
    type: "review",
    prompt: "Que ideia deste tópico você gostaria de revisar?",
  },
];