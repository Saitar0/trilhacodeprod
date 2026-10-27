---
arquivo_id: "f6-25-2-90-integracao-kp01-solucao-md"
parent_key: "25.2"
tipo_arquivo: "answer_key_pratica"
assuntos: ["01_estado_snapshot_formulario_controlado", "03_colecoes_imutaveis_identidade"]
ordem: 1
itens_origem: ["P01"]
---

**Solução de referência:** o componente guarda tasks e title. O submit normaliza e valida title, pede atualização funcional com array acrescido do objeto novo e limpa o campo se adicionou. Cada botão de concluir chama função com ID e map cria cópia do item; remover filtra pelo ID. Renderização usa task.id como key e mostra texto vazio quando não há itens.

