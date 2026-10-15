from core import db, hash_password, now
from settings import settings

TAXONOMIES = [
    ("pedagogical_type", "solo", "Tema solo", "Estudo isolado e focado em um assunto", "sky"),
    ("pedagogical_type", "integrado", "Tema integrado", "Conecta vários assuntos em um contexto", "violet"),
    ("pedagogical_type", "revisita", "Revisita", "Retorno a um tema já visto com nova profundidade", "amber"),
    ("pedagogical_type", "pratica", "Prática guiada", "Aplicação prática conduzida", "emerald"),
    ("pedagogical_type", "projeto", "Projeto", "Entrega integradora", "rose"),
    ("requirement", "obrigatorio", "Obrigatório", "Parte essencial da trilha", "emerald"),
    ("requirement", "repertorio", "Repertório", "Amplia visão e vocabulário técnico", "cyan"),
    ("requirement", "opcional", "Opcional", "Aprofundamento livre", "slate"),
    ("depth", "alta", "Profundidade alta", "Domínio detalhado esperado", "rose"),
    ("depth", "media", "Profundidade média", "Entendimento funcional", "amber"),
    ("depth", "repertorio", "Repertório", "Noção geral, saber que existe", "sky"),
    ("relation_type", "prerequisite", "Pré-requisito", "Deve ser estudado antes", "amber"),
    ("relation_type", "complement", "Complementar", "Enriquece o estudo deste item", "cyan"),
    ("relation_type", "revisit", "Revisita de", "Retoma um tema anterior", "violet"),
    ("relation_type", "related", "Relacionado", "Conexão temática", "slate"),
]


def f(name, label, type_, **extra):
    return {"name": name, "label": label, "type": type_, **extra}


GRADING = f("grading", "Correção", "select", options=["manual", "auto", "none"])
CRITERIA = f("criteria", "Critérios da rubrica (um por linha)", "list")
RESUBMIT = f("allow_resubmit", "Permitir nova tentativa após reprovação", "boolean")
MAX_SCORE = f("max_score", "Nota máxima (opcional)", "number")
SUBMITTABLE = {"exercise_objective", "exercise_open", "practical_challenge"}
BLOCK_TYPES = [
    ("theory_text", "Texto teórico", "teoria", "BookOpen", [f("body", "Conteúdo", "markdown")]),
    ("summary", "Resumo curto", "teoria", "AlignLeft", [f("body", "Resumo", "textarea")]),
    ("checklist", "Checklist", "pratica", "ListChecks", [f("items", "Itens", "list")]),
    ("exercise_objective", "Exercício objetivo", "avaliacao", "CircleDot", [
        f("format", "Formato", "select", options=["multiple_choice", "true_false", "ordering", "fill_code"]),
        f("prompt", "Enunciado", "markdown"), f("options", "Alternativas / itens", "list"),
        f("answer", "Resposta esperada", "text"), f("explanation", "Explicação", "markdown"), GRADING, CRITERIA, RESUBMIT,
        MAX_SCORE]),
    ("exercise_open", "Exercício aberto", "avaliacao", "PenLine", [
        f("prompt", "Enunciado", "markdown"), f("rubric", "Orientações de correção", "markdown"), GRADING, CRITERIA,
        RESUBMIT, MAX_SCORE]),
    ("practical_challenge", "Desafio prático", "pratica", "Swords", [
        f("prompt", "Descrição", "markdown"), f("language", "Linguagem", "text"),
        f("starter_code", "Código inicial", "code"), f("acceptance", "Critérios de aceite", "list"), GRADING, CRITERIA,
        RESUBMIT, MAX_SCORE]),
    ("quiz", "Quiz", "avaliacao", "HelpCircle", [
        f("question", "Pergunta", "text"), f("options", "Alternativas", "list"),
        f("correct_index", "Índice correto (0, 1, 2...)", "number"), f("explanation", "Explicação", "markdown")]),
    ("flashcard", "Flashcard", "teoria", "Layers", [f("front", "Frente", "textarea"), f("back", "Verso", "textarea")]),
    ("code_snippet", "Snippet de código", "recurso", "Code2", [
        f("language", "Linguagem", "text"), f("code", "Código", "code"), f("caption", "Legenda", "text")]),
    ("video_embed", "Vídeo", "recurso", "PlayCircle", [f("url", "URL do vídeo", "url"), f("caption", "Legenda", "text")]),
    ("external_link", "Link externo", "recurso", "ExternalLink", [
        f("url", "URL", "url"), f("label", "Texto do link", "text"), f("description", "Descrição", "textarea")]),
    ("instructor_note", "Observação do instrutor", "orientacao", "MessageSquareQuote", [f("body", "Observação", "markdown")]),
    ("review", "Revisão", "teoria", "RotateCcw", [
        f("body", "Pontos de revisão", "markdown"), f("review_after_days", "Revisar após (dias)", "number")]),
    ("supplementary", "Material complementar", "recurso", "Paperclip", [
        f("body", "Descrição", "markdown"), f("url", "Link", "url")]),
    ("reference", "Referência", "recurso", "Quote", [f("citation", "Citação", "text"), f("url", "URL", "url")]),
]

PLACEHOLDER = "> Conteúdo placeholder — este tópico existe para demonstrar a estrutura. Edite no painel administrativo."

SEED_TREE = [
    ("phase", "Fundamentos da computação", "Base conceitual para tudo que vem depois.", [
        ("module", "Lógica e algoritmos", "Pensamento computacional e estruturas de controle.", [
            ("topic", "Variáveis e tipos", "solo", "obrigatorio", "alta", True),
            ("topic", "Condicionais e laços", "solo", "obrigatorio", "alta", True),
            ("topic", "Complexidade de algoritmos", "solo", "repertorio", "repertorio", False),
        ]),
        ("module", "Ferramentas do desenvolvedor", "Terminal, Git e ambiente.", [
            ("submodule", "Versionamento com Git", "Fluxo diário com Git.", [
                ("topic", "Commits e branches", "pratica", "obrigatorio", "media", True),
                ("topic", "Merge e rebase", "integrado", "obrigatorio", "media", False),
            ]),
        ]),
    ]),
    ("phase", "Construção para a web", "Do HTML ao backend.", [
        ("module", "Frontend essencial", "Estrutura, estilo e interatividade.", [
            ("topic", "HTML semântico", "solo", "obrigatorio", "media", True),
            ("topic", "JavaScript no navegador", "integrado", "obrigatorio", "alta", True),
        ]),
        ("module", "APIs e backend", "Comunicação cliente-servidor.", [
            ("topic", "HTTP e REST", "solo", "obrigatorio", "alta", False),
            ("topic", "Revisita: laços em código real", "revisita", "repertorio", "media", False),
        ]),
    ]),
    ("phase", "Arquitetura e qualidade", "Organização de sistemas maiores.", []),
]


async def _seed_user(email, password, name, role):
    if not email or not password:
        return
    existing = await db.users.find_one({"email": email})
    if existing is not None:
        return
    await db.users.insert_one({"email": email, "name": name, "role": role, "password_hash": hash_password(password),
                               "is_demo": not settings.is_production,
                               "profile": {"bio": "", "goals": "", "preferences": {}}, "created_at": now()})


async def _insert_node(track_id, parent_id, kind, title, order, **extra):
    doc = {"track_id": track_id, "parent_id": parent_id, "kind": kind, "title": title, "slug": title.lower(),
           "is_demo": True,
           "summary": extra.pop("summary", ""), "description": "", "notes": "", "guidance": "",
           "pedagogical_type": extra.pop("ptype", ""), "requirement": extra.pop("req", ""),
           "depth": extra.pop("depth", ""), "status": "published", "estimated_minutes": extra.pop("minutes", 0),
           "tag_ids": [], "release": {}, "meta": {}, "order": order, "created_at": now(), "updated_at": now()}
    res = await db.nodes.insert_one(doc)
    return str(res.inserted_id)


async def _seed_topic(track_id, parent_id, item, order, titles):
    _, title, ptype, req, depth, rich = item
    nid = await _insert_node(track_id, parent_id, "topic", title, order, ptype=ptype, req=req, depth=depth,
                             minutes=25, summary=f"Placeholder sobre {title.lower()}.")
    titles[title] = nid
    blocks = [("theory_text", "Introdução", {"body": f"## {title}\n\n{PLACEHOLDER}"})]
    if rich:
        blocks += [
            ("checklist", "Antes de seguir", {"items": ["Li a introdução", "Anotei dúvidas", "Revisei o resumo"]}),
            ("code_snippet", "Exemplo", {"language": "javascript", "code": "// exemplo placeholder\nconst x = 42;",
                                         "caption": "Snippet demonstrativo"}),
            ("quiz", "Verificação rápida", {"question": "Este bloco é um placeholder?", "options": ["Sim", "Não"],
                                            "correct_index": 0, "explanation": "Sim — serve para demonstrar quizzes."}),
        ]
    for i, (btype, btitle, data) in enumerate(blocks):
        await db.content_blocks.insert_one({"node_id": nid, "track_id": track_id, "type": btype, "title": btitle,
                                            "is_demo": True,
                                            "data": data, "status": "published", "order": i, "schema_version": 1,
                                            "created_at": now(), "updated_at": now()})


async def _seed_children(track_id, parent_id, children, titles):
    for i, item in enumerate(children):
        if item[0] == "topic":
            await _seed_topic(track_id, parent_id, item, i, titles)
        else:
            kind, title, summary, sub = item
            nid = await _insert_node(track_id, parent_id, kind, title, i, summary=summary)
            await _seed_children(track_id, nid, sub, titles)


async def _seed_track():
    if await db.tracks.find_one({"slug": "trilha-code"}):
        return
    res = await db.tracks.insert_one({
        "title": "Trilha Code", "slug": "trilha-code",
        "is_demo": True,
        "subtitle": "Ultra cronograma de estudos em desenvolvimento de software",
        "description": "Trilha principal da plataforma. Conteúdo demonstrativo — edite livremente no painel.",
        "cover_url": "", "status": "published", "visibility": "public", "audience": ["iniciante", "intermediário"],
        "difficulty": "progressiva", "tag_ids": [], "hierarchy": ["phase", "module", "submodule", "topic"],
        "level_labels": {"phase": "Fase", "module": "Módulo", "submodule": "Submódulo", "topic": "Tópico"},
        "settings": {"enforce_prerequisites": True, "unlock_strategy": "free", "visual_style": "default"},
        "meta": {}, "order": 0, "version": 1, "derived_from": None, "created_at": now(), "updated_at": now(),
        "published_at": now()})
    track_id = str(res.inserted_id)
    titles = {}
    for i, (kind, title, summary, children) in enumerate(SEED_TREE):
        nid = await _insert_node(track_id, None, kind, title, i, summary=summary)
        await _seed_children(track_id, nid, children, titles)
    rels = [("Condicionais e laços", "Variáveis e tipos", "prerequisite"),
            ("JavaScript no navegador", "Condicionais e laços", "prerequisite"),
            ("HTTP e REST", "JavaScript no navegador", "prerequisite"),
            ("Merge e rebase", "Commits e branches", "prerequisite"),
            ("Revisita: laços em código real", "Condicionais e laços", "revisit"),
            ("Complexidade de algoritmos", "Condicionais e laços", "complement")]
    for src, tgt, rtype in rels:
        await db.relations.insert_one({"track_id": track_id, "node_id": titles[src], "target_id": titles[tgt],
                                       "type": rtype, "enforced": rtype == "prerequisite", "note": "", "created_at": now()})


async def run_seed():
    if settings.is_production:
        if not await db.users.find_one({"role": "admin"}):
            await _seed_user(settings.admin_email, settings.admin_password, "Administrador", "admin")
    else:
        await _seed_user(settings.admin_email, settings.admin_password, "Administrador", "admin")
        await _seed_user(settings.editor_email, settings.editor_password, "Editora Demo", "editor")
        await _seed_user(settings.student_email, settings.student_password, "Aluno Demo", "student")
    for i, (group, key, label, desc, color) in enumerate(TAXONOMIES):
        await db.taxonomies.update_one({"group": group, "key": key}, {"$setOnInsert": {
            "label": label, "description": desc, "color": color, "order": i, "created_at": now()}}, upsert=True)
    for i, (key, label, cat, icon, fields) in enumerate(BLOCK_TYPES):
        await db.block_types.update_one({"key": key}, {"$setOnInsert": {
            "label": label, "category": cat, "icon": icon, "fields": fields, "description": "", "enabled": True,
            "capabilities": ["submission"] if key in SUBMITTABLE else [],
            "order": i, "created_at": now()}}, upsert=True)
    for name, color in [("fundamentos", "sky"), ("web", "emerald"), ("ferramentas", "amber")]:
        await db.tags.update_one({"slug": name}, {"$setOnInsert": {"name": name, "color": color, "created_at": now()}},
                                 upsert=True)
    if not settings.is_production:
        await _seed_track()
