---
arquivo_id: "f4-9-2-90-integracao-kp01-gabarito-pratica"
parent_key: "9.2"
tipo_arquivo: "answer_key_pratica"
assuntos: ["01_regras_dominio_entidades_chaves", "02_cardinalidade_opcionalidade"]
ordem: 1
itens_origem: ["P1"]
---

**Solução de referência:** Estudante, Curso e Matrícula. Matrícula liga um estudante a um curso e guarda data_matricula. Cursos como lista violam a organização em valores individuais e dificultam integridade e consultas. Se não pode haver reinscrição, estudante_id + curso_id é único. Cada Matrícula referencia exatamente um Estudante e um Curso; cada Estudante e cada Curso podem participar de zero a muitas Matrículas.

