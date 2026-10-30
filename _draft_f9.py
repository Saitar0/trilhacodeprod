from pathlib import Path
import re, yaml, hashlib, unicodedata, json

SRC=Path("docs/courses/trilhacode/Conteudos/Fase_9")
DEST="docs/courses/trilhacode/Conteudos_migrado/Fase_9"
BASE="2b906584f7e8b3d0b5e1cc84a21287d9e4ff57a6"
PAGE="docs/courses/trilhacode/Fase_9_Escala_Mensageria_e_Mercado.md"
REFS="docs/courses/trilhacode/Referencias_Fase_9.md"
GUIDE=Path("docs/courses/trilhacode/Guia_Projetos_e_Rotacao_de_Tipos.md")
mods={"40":"Mensageria na prática: RabbitMQ e Kafka","41":"Arquitetura distribuída","42":"Python e ecossistema web","43":"PHP e Laravel","44":"C# e .NET","45":"Java e Spring","46":"Realidade de mercado e projeto da fase"}
srcnames={"40.1":"40.1_RabbitMQ.md","40.2":"40.2_Kafka.md","40.3":"40.3_Comparacao.md","41.1":"41.1_Arquitetura_distribuida.md","41.2":"41.2_Regra_dura.md","42.1":"42.1_Base_Python_Django.md","42.2":"42.2_Ecossistema_Python.md","42.3":"42.3_Nocoes_FastAPI_Flask.md","43.1":"43.1_Stack_PHP_Laravel.md","43.2":"43.2_Nocoes_Slim_Phalcon.md","44.1":"44.1_Stack_CSharp_DotNet.md","44.2":"44.2_Legado_WebForms.md","45.1":"45.1_Stack_Java_Spring.md","46.1":"46.1_Realidade_de_mercado.md","46.2":"46.2_Projeto_incremental_da_fase.md","46.3":"46.3_Projeto_de_fase_Trilho_B.md"}
topics={
"40.1":[("01_exchange_binding_filas_consumers","Exchange, binding, filas e consumers"),("02_confirmacoes_ack_idempotencia","Confirmações, ack e idempotência"),("03_prefetch_trabalho_em_voo","Prefetch e trabalho em voo"),("04_dead_letter_recuperacao","Dead-letter e recuperação de mensagens")],
"40.2":[("01_log_particionado_ordem","Tópicos como log particionado e ordenação"),("02_grupos_particoes_consumidores","Grupos e distribuição de consumidores"),("03_offsets_retencao_replay","Offsets, retenção e replay")],
"40.3":[("01_modelar_problema_antes_escolha","Modelar o problema antes da escolha"),("02_entrega_falhas_duplicatas","Entrega, falhas e duplicatas"),("03_ordem_escala_replay","Ordem, escala e replay"),("04_operacao_custo_decisao","Operação, custo e decisão defensável")],
"41.1":[("01_fronteiras_orcamento_latencia","Fronteiras de serviço e orçamento de latência"),("02_timeout_retry_circuit_breaker","Timeout, retry e circuit breaker"),("03_consistencia_saga_compensacao","Consistência eventual, saga e compensação"),("04_outbox_entrega_operacao","Outbox, entrega e operação observável")],
"41.2":[("01_beneficio_fronteira","Benefício que justifica a fronteira"),("02_custo_prontidao_operacional","Custo total e prontidão operacional"),("03_descoberta_teste_fronteira","Descoberta e teste da fronteira"),("04_extracao_incremental_reversao","Extração incremental, reversão e decisão")],
"42.1":[("01_python_projeto_app_django","Python, projeto e app Django"),("02_ciclo_url_modelo","Do URL ao modelo: ciclo Django"),("03_drf_serializacao_views_acesso","DRF: serialização, views e controle de acesso")],
"42.2":[("01_celery_tarefas_fora_requisicao","Celery: tarefas fora da requisição"),("02_pytest_fixtures_integracao","pytest: testes, fixtures e níveis de integração"),("03_poetry_dependencias_distribuicao","Poetry: dependências e distribuição")],
"42.3":[("01_api_validacao_documentacao","API, validação e documentação"),("02_convencoes_composicao_custo","Convenções, composição e custo de equipe"),("03_sync_async_operacao","Síncrono, async e operação")],
"43.1":[("01_php_composer_versoes","PHP, Composer e versões"),("02_ciclo_requisicao_laravel","Ciclo de requisição no Laravel"),("03_filas_decisao_stack","Filas e decisão de stack")],
"43.2":[("01_slim_http_composicao","Slim: HTTP e composição de componentes"),("02_phalcon_versao_distribuicao","Phalcon: versão e forma de distribuição"),("03_comparacao_trabalho_completo","Comparação com Laravel pelo trabalho completo")],
"44.1":[("01_csharp_sdk_pipeline_api","C#, SDK e pipeline de API"),("02_injecao_dependencia_persistencia","Injeção de dependência e persistência"),("03_testes_suporte_producao","Testes, suporte e produção")],
"44.2":[("01_pagina_postback_ciclo_vida","Página server-side, postback e ciclo de vida"),("02_controles_viewstate_codebehind","Controles server-side, ViewState e code-behind"),("03_manutencao_suporte_modernizacao","Manutenção, suporte e modernização")],
"45.1":[("01_java_spring_caminho_requisicao","Java, Spring e o caminho de uma requisição"),("02_persistencia_jpa_consultas","Persistência: especificação, implementação e consultas"),("03_testes_integracao_kafka","Testes e integração com Kafka")],
"46.1":[("01_vaga_fonte_de_sinais","Ler uma vaga como fonte de sinais"),("02_requisitos_evidencias_honestas","Transformar requisitos em evidências honestas"),("03_projeto_portfolio_escopo","Projeto de portfólio com escopo defensável"),("04_modernizar_ou_otimizar","Decidir quando modernizar e quando otimizar")]}
Q={"40.1":[["01"],["02"],["02","04"],["03"],["04"]],"40.3":[["03"],["01","04"],["02"],["03"],["04"]],"41.1":[["02"],["02"],["02"],["03"],["04"]],"41.2":[["01"],["03"],["01"],["02"],["04"]],"46.1":[["01"],["02"],["02"],["04"],["04"]]}
P={"40.1":[["01"],["01","02","03"],["02","04"]],"40.2":[["01","02"],["03"]],"40.3":[["01","02","03","04"],["02","03","04"],["01","02","03","04"]],"41.1":[["01","02"],["01","02"],["03","04"]],"41.2":[["01","02","03","04"],["02","03"],["02","04"]],"42.1":[["02","03"],["03"]],"42.2":[["01","02","03"],["01","02","03"]],"42.3":[["01","02","03"],["02","03"]],"43.1":[["01","02"],["02","03"]],"43.2":[["01","03"],["02"]],"44.1":[["01","02"],["02","03"]],"44.2":[["01","02"],["02","03"]],"45.1":[["01","02"],["02","03"]],"46.1":[["01","02"],["02","03"],["04"]]}
FC={"40.2":[["01"],["02"],["03"]],"42.1":[["01"],["03"],["01"]],"42.2":[["01"],["02"],["03"]],"42.3":[["01"],["02"],["03"]],"43.1":[["01"],["02"],["02","03"]],"43.2":[["01"],["01"],["02"]],"44.1":[["02","03"],["02"],["02"]],"44.2":[["01"],["02"],["03"]],"45.1":[["02"],["02"],["03"]]}
levels={"40.2":"reconhecer","42.1":"implementar","43.1":"implementar","44.1":"implementar","45.1":"implementar","42.2":"repertorio","42.3":"reconhecer","43.2":"reconhecer","44.2":"repertorio"}
stacks=["42.1","43.1","44.1","45.1"]
def section(t,h):
 m=re.search(r"(?m)^## "+re.escape(h)+r"\s*$",t)
 if not m:return None
 z=t[m.end():];e=re.search(r"(?m)^## ",z);return (z[:e.start()] if e else z).strip("\n")
def slug(t):
 t=unicodedata.normalize("NFKD",t).encode("ascii","ignore").decode().lower()
 return re.sub(r"[^a-z0-9]+","-",t).strip("-")
def metadata(t):
 d={}
 for line in t.splitlines()[1:10]:
  m=re.match(r"- (key|tipo|carater|profundidade|estimativa_minutos|tags|status):\s*(.*)$",line)
  if m:
   k,v=m.groups()
   if k=="key":d[k]=v.strip().strip("'").strip('"')
   elif k=="estimativa_minutos":d[k]=int(v)
   elif k=="tags":d[k]=[x.strip() for x in v.strip("[]").split(",") if x.strip()]
   else:d[k]=v.strip()
 return d
def questions(t):
 out=[]
 for m in re.finditer(r"(?m)^## (Quiz|Verificação)\s*$",t):
  z=t[m.end():];e=re.search(r"(?m)^## ",z);b=z[:e.start()] if e else z
  ms=list(re.finditer(r"(?m)^(\d+)\. ",b))
  for i,x in enumerate(ms):out.append((int(x.group(1)),b[x.start():ms[i+1].start()] if i+1<len(ms) else b[x.start():],m.group(1)))
 return out
def practices(t):
 out=[]
 for m in re.finditer(r"(?m)^### (Atividade (\d+) — .+)$",t):
  z=t[m.end():];e=re.search(r"(?m)^### |^## ",z);out.append((int(m.group(2)),m.group(1),z[:e.start()] if e else z))
 return out
def cards(t):
 b=section(t,"Flashcards")
 return [x for x in (b or "").splitlines() if re.match(r"^- \*\*",x)]
def reference_items(t):
 out=[]
 for line in (section(t,"Referências") or "").splitlines():
  if not line.startswith("- "):continue
  d=re.search(r"consultad[oa]s? em (\d{2}/\d{2}/\d{4})",line,re.I)
  links=re.findall(r"\[([^\]]+)\]\(([^)]+)\)",line)
  if links:
   for title,url in links:out.append({"titulo":title,"url":url,"consultado_em":d.group(1) if d else None})
  else:out.append({"titulo":line[2:].split(" — ")[0],"url":None,"consultado_em":d.group(1) if d else None})
 return out
sources={}
for u,fn in srcnames.items():
 p=SRC/fn
 if not p.exists():raise SystemExit("source absent "+str(p))
 t=p.read_text(encoding="utf-8");h=re.search(r"(?m)^# (.+)$",t);theory=section(t,"Teoria")
 heads=re.findall(r"(?m)^### (.+)$",theory or "")
 sources[u]={"path":p.as_posix(),"text":t,"title":h.group(1),"meta":metadata(t),"sha":hashlib.sha256(p.read_bytes()).hexdigest(),"lines":len(t.splitlines()),"words":len(re.findall(r"\b[\w-]+\b",t)),"heads":heads}
 if u in topics and len(heads)!=len(topics[u]):raise SystemExit(f"{u} theory headings mismatch")
 if u in Q and len(questions(t))!=len(Q[u]):raise SystemExit(f"{u} Q mismatch")
 if u in P and len(practices(t))!=len(P[u]):raise SystemExit(f"{u} P mismatch")
 if u in FC and len(cards(t))!=len(FC[u]):raise SystemExit(f"{u} flashcards mismatch")
if (len(sources),sum(map(lambda x:len(questions(x["text"])),sources.values())),sum(map(lambda x:len(cards(x["text"])),sources.values())),sum(map(lambda x:len(practices(x["text"])),sources.values())),sum(map(len,topics.values())))!=(16,25,27,33,47):raise SystemExit("source totals mismatch")

files={u:{} for u in srcnames};ids=[];paths=[];milestones={}
def add(u,a,path,kind,selector,ass=None,item=None,answers=None,marker=None,scale=None,mid=None,title=None,note=None):
 aid="f9-"+u.replace(".","-")+"-"+slug(path[:-3])
 r={"path":path,"tipo":kind,"arquivo_id":aid,"origem":{"arquivo_origem":sources[u]["path"],"seletor":selector}}
 if ass:
  ss=[topics[u][int(x)-1][0] for x in ass]
  if len(ss)==1:r["assunto"]=ss[0]
  else:r["assuntos"]=ss
 if item is not None:r["item_origem"]=item
 if answers is not None:r["responde_a"]=answers
 if marker:r["origem"]["marcador_literal"]=marker
 if scale:r["escala_rubrica"]=scale
 if mid:r["marco_id"]=mid;r["titulo_marco"]=title
 if note:r["nota"]=note
 if a in files[u]:raise SystemExit("alias duplicate "+u+"/"+a)
 files[u][a]=r;ids.append(aid);paths.append((u,path))

for u in srcnames:
 t=sources[u]["text"];project=sources[u]["meta"].get("tipo")=="projeto"
 add(u,"IDX","README.md","topic_index","H1 literal + lista de metadados original sob H1")
 if not project:
  for a,path,typ,h in [("OBJ","00_objetivo.md","objetivo","Objetivo"),("SUM","01_resumo.md","resumo","Resumo"),("CRI","02_criterio_de_conclusao.md","criterio","Critério de conclusão"),("CON","03_conexoes.md","conexoes","Conexões"),("REF","04_referencias.md","referencias","Referências")]:
   if section(t,h) is None:raise SystemExit(f"{u} common section absent {h}")
   add(u,a,path,typ,"## "+h)
  for i,(s,title) in enumerate(topics[u],1):
   sel="### "+sources[u]["heads"][i-1]
   if u=="41.2" and i==1:sel=["parágrafo introdutório de ## Teoria",sel]
   add(u,f"T{i:02d}",s+"/01_teoria.md","theory",sel,[f"{i:02d}"],note="A abertura de 41.2 fica com assunto 01.")
  for i,(n,b,secname) in enumerate(questions(t),1):
   ass=Q[u][i-1];folder="90_integracao" if len(ass)>1 else topics[u][int(ass[0])-1][0];sel=f"## {secname} > item {n}"
   marker=("**Resposta:**" if "**Resposta:**" in b else "**Resposta esperada:**") if u=="46.1" else ("? **" if "? **" in b else "marcador inline a verificar por item")
   note="Resposta inline separada literalmente; concatenar Q+K reconstrói o item original."
   add(u,f"Q{i:02d}",f"{folder}/Q{i:02d}_quiz.md","quiz",sel,ass,f"Q{i:02d}",marker=marker,note=note)
   add(u,f"K{i:02d}",f"{folder}/K{i:02d}_gabarito.md","answer_key",sel,ass,f"Q{i:02d}",f"Q{i:02d}",marker,note=note)
  groups={}
  for i,c in enumerate(cards(t),1):groups.setdefault(tuple(FC[u][i-1]),[]).append(i)
  for j,(ass,numbers) in enumerate(sorted(groups.items(),key=lambda x:min(x[1])),1):
   folder="90_integracao" if len(ass)>1 else topics[u][int(ass[0])-1][0]
   add(u,f"F{j:02d}",f"{folder}/F{j:02d}_flashcards.md","flashcards",[f"## Flashcards > cartão {n}" for n in numbers],[f"{int(x):02d}" for x in ass],[f"FC{n:02d}" for n in numbers])
  for i,(n,title,b) in enumerate(practices(t),1):
   ass=P[u][i-1];folder="90_integracao" if len(ass)>1 else topics[u][int(ass[0])-1][0];sel="### "+title
   add(u,f"P{i:02d}",f"{folder}/P{i:02d}_pratica.md","practice",sel,ass,f"P{i:02d}",note="Manter enunciado e critérios; separar somente bloco de feedback/rubrica existente.")
   fb=re.search(r"(?m)^\*\*(Feedback(?: esperado| de referência| para revisar)?|Solução(?: comentada)?):\*\*",b)
   if fb:add(u,f"KP{i:02d}",f"{folder}/KP{i:02d}_feedback_pratica.md","answer_key_pratica",sel+" > **"+fb.group(1)+":**",ass,f"P{i:02d}",f"P{i:02d}",marker="**"+fb.group(1)+":**")
   rb=re.search(r"(?m)^\*\*Rubrica \(0–2 cada, total 10\):\*\*",b)
   if rb:add(u,f"R{i:02d}",f"{folder}/R{i:02d}_rubrica.md","rubric",sel+" > "+rb.group(0),ass,f"P{i:02d}",marker=rb.group(0),scale="0–2 por critério; cinco critérios; total 10; demais condições literais.")
 else:
  add(u,"OBJ","00_objetivo.md","objetivo","## Objetivo")
  if u=="46.2":
   add(u,"SCP","01_escopo_e_premissas.md","project_scope","## Escopo e premissas")
   add(u,"R00","07_rubrica_final.md","rubric","## Verificação final e rubrica",scale="0–2 por critério; seis dimensões; total 12; limiares/bloqueadores literais.")
  else:
   add(u,"SCP","01_escopo_e_opcoes.md","project_scope",["## Regras de escolha e escopo","## Tipos disponíveis na Fase 9"],note="Concatenar em ordem; tabela T1–T5 permanece íntegra.")
   add(u,"R00","08_rubrica_final.md","rubric","## Rubrica final",scale="0–2 por critério; seis dimensões; total 12; limiares/bloqueadores literais.")
  if section(t,"Resumo") is not None:add(u,"SUM","02_resumo.md","resumo","## Resumo")
  if section(t,"Critério de conclusão") is not None:add(u,"CRI","03_criterio_de_conclusao.md","criterio","## Critério de conclusão")
  if section(t,"Conexões") is not None:add(u,"CON","04_conexoes.md","conexoes","## Conexões")
  if section(t,"Referências") is not None:add(u,"REF","05_referencias.md","referencias","## Referências")
  ms=[(int(m.group(1)),m.group(0).strip()) for m in re.finditer(r"(?m)^### Entrega (\d+) — .+$",t)]
  if len(ms)!=4:raise SystemExit(f"{u} milestone count mismatch")
  milestones[u]=[x[1] for x in ms]
  for n,title in ms:
   s=slug(title.split("—",1)[1])
   add(u,f"M{n:02d}",f"M{n:02d}_{s}.md","project_milestone",title,mid=f"M{n:02d}",title=title)
   add(u,f"C{n:02d}",f"C{n:02d}_aceite_{s}.md","checklist",title+" > **Critérios de aceite:**",marker="**Critérios de aceite:**",mid=f"M{n:02d}",title=title)
if len(paths)!=len(set(paths)) or len(ids)!=len(set(ids)):raise SystemExit("destination or ID duplicate")

oldids=set()
for p in Path("docs/migracao").glob("mapa_de_migracao*.yml"):
 if p.name.endswith("fase9.yml"):continue
 data=yaml.safe_load(p.read_text(encoding="utf-8"))
 def walk(v):
  if isinstance(v,dict):
   if isinstance(v.get("arquivo_id"),str):oldids.add(v["arquivo_id"])
   for z in v.values():walk(z)
  elif isinstance(v,list):
   for z in v:walk(z)
 walk(data)
if set(ids)&oldids or any(not x.startswith("f9-") for x in ids):raise SystemExit("global ID collision")
types={};perunit={}
for u,fs in files.items():
 perunit[u]=len(fs)
 for f in fs.values():types[f["tipo"]]=types.get(f["tipo"],0)+1
total=sum(perunit.values())
if total!=302 or (types.get("quiz"),types.get("answer_key"),types.get("practice"),types.get("checklist"),types.get("project_milestone"))!=(25,25,33,8,8):raise SystemExit(f"unexpected output totals {total} {types}")

def coverage(u):
 d={s[0]:{"quiz_exclusivos":[],"quiz_compartilhados":[],"praticas_exclusivas":[],"praticas_compartilhadas":[],"flashcards_exclusivos":[],"flashcards_compartilhados":[]} for s in topics[u]}
 for typ,mapping in [("quiz",Q),("praticas",P),("flashcards",FC)]:
  for i,ass in enumerate(mapping.get(u,[]),1):
   key=typ+("_exclusivos" if len(ass)==1 else "_compartilhados")
   item=("Q" if typ=="quiz" else "P" if typ=="praticas" else "FC")+f"{i:02d}"
   for x in ass:d[topics[u][int(x)-1][0]][key].append(item)
 esn={"E":0,"S":0,"N":0}
 for v in d.values():
  e=sum(len(v[k]) for k in ("quiz_exclusivos","praticas_exclusivas","flashcards_exclusivos"))
  sh=sum(len(v[k]) for k in ("quiz_compartilhados","praticas_compartilhadas","flashcards_compartilhados"))
  esn["E" if e else "S" if sh else "N"]+=1
 return d,esn
proposals=[]
for u in topics:
 cv,esn=coverage(u)
 for s,v in cv.items():
  e=sum(len(v[k]) for k in ("quiz_exclusivos","praticas_exclusivas","flashcards_exclusivos"))
  sh=sum(len(v[k]) for k in ("quiz_compartilhados","praticas_compartilhadas","flashcards_compartilhados"))
  if not e:proposals.append({"unidade":u,"slug":s,"cobertura":"S-only" if sh else "N","proposta":"[PROPOSTA EM ESPERA] avaliar verificação exclusiva; não criar na migração."})
units={}
for u in srcnames:
 s=sources[u];t=s["text"];cv,esn=coverage(u) if u in topics else ({},{})
 qlist=[]
 for i,(n,b,secname) in enumerate(questions(t),1):
  ass=Q[u][i-1]
  marker=("**Resposta:**" if "**Resposta:**" in b else "**Resposta esperada:**") if u=="46.1" else ("? **" if "? **" in b else "marcador inline a confirmar")
  qlist.append({"id":f"Q{i:02d}","origem":f"## {secname} > item {n}","assuntos":[topics[u][int(x)-1][0] for x in ass],"classificacao":"exclusivo" if len(ass)==1 else "compartilhado","marcador_resposta":marker,"resposta_inline":True})
 plist=[]
 for i,(n,title,b) in enumerate(practices(t),1):
  ass=P[u][i-1];fb=bool(re.search(r"(?m)^\*\*(Feedback(?: esperado| de referência| para revisar)?|Solução(?: comentada)?):\*\*",b));rb=bool(re.search(r"(?m)^\*\*Rubrica \(0–2 cada, total 10\):\*\*",b))
  plist.append({"id":f"P{i:02d}","titulo_original":title,"origem":f"### {title}","assuntos":[topics[u][int(x)-1][0] for x in ass],"classificacao":"exclusivo" if len(ass)==1 else "compartilhado","feedback_existente":fb,"rubrica_existente":rb})
 flist=[]
 for i,_ in enumerate(cards(t),1):
  ass=FC[u][i-1];flist.append({"id":f"FC{i:02d}","origem":f"## Flashcards > cartão {i}","assuntos":[topics[u][int(x)-1][0] for x in ass],"classificacao":"exclusivo" if len(ass)==1 else "compartilhado"})
 conn=section(t,"Conexões") or ""
 record={"key":u,"pasta":Path(srcnames[u]).stem,"origem":s["path"],"sha256_origem":s["sha"],"titulo_original":s["title"],"modulo":{"id":u.split(".")[0],"nome":mods[u.split(".")[0]]},"metadados_originais":s["meta"],"metadados_origem":"lista Markdown sob H1; transportar sem alteração ao README YAML","estatisticas_origem":{"linhas":s["lines"],"palavras_estimadas":s["words"],"microtopicos_teoria":len(topics.get(u,[])),"questoes":len(qlist),"flashcards":len(flist),"praticas_convencionais":len(plist),"entregas_projeto":4 if u in milestones else 0},"arquivos":files[u],"assuntos":[x[0] for x in topics.get(u,[])],"detalhe_assuntos":[{"slug":x[0],"titulo":x[1],"microtopicos_origem":(["parágrafo introdutório em Teoria",f"### {s['heads'][i]}"] if u=="41.2" and i==0 else [f"### {s['heads'][i]}"]),"classificacao":"[PROPOSTA] reconstruída de fonte; sem aprovação histórica documentada."} for i,x in enumerate(topics.get(u,[]))],"questoes":qlist,"praticas":plist,"flashcards":flist,"cobertura":{"por_assunto":cv,"E_S_N":esn},"relacoes_curriculares_fonte":{"origem":"## Conexões","texto_literal":conn,"wikilinks":re.findall(r"\[\[(.*?)\]\]",conn),"tratamento":"preservar literalmente; normalizar links Markdown somente com alvo comprovado"},"referencias_por_fonte":reference_items(t),"consultado_em_regra":"por referência, nunca uma data global"}
 if u in levels:record["nivel_dominio"]=levels[u]
 if u=="46.2":record.update({"stack_mode":"alternativa","escolha_do_aluno":True,"stack_opcoes":stacks,"stack_selecionada":None,"escala_rubrica":"0–2 por critério; 6 dimensões; total 12","marcos":4,"aceites":4,"checklist_final":False})
 if u=="46.3":record.update({"stack_mode":"principal","escolha_do_aluno":False,"stack_opcoes":stacks,"stack_selecionada":None,"escala_rubrica":"0–2 por critério; 6 dimensões; total 12","marcos":4,"aceites":4,"checklist_final":False})
 units[u]=record

linkfix=[]
if not GUIDE.exists():raise SystemExit("guide target missing")
for u in ("46.2","46.3"):
 for line_no,line in enumerate(sources[u]["text"].splitlines(),1):
  for label,href in re.findall(r"\[([^\]]+)\]\(([^)]+)\)",line):
   if href.startswith("../"):
    if not (SRC/href).resolve().exists():raise SystemExit(f"source relative target missing {u}:{line_no} {href}")
    linkfix.append({"unidade":u,"origem":sources[u]["path"],"linha":line_no,"texto_visivel":label,"href_origem":href,"href_destino":"../../../Guia_Projetos_e_Rotacao_de_Tipos.md","destino_repositorio":GUIDE.as_posix()})
if len(linkfix)!=3:raise SystemExit("expected 3 guide links")
relations=[
 {"tema":"40.x ↔ F7 33.1/35.1","fonte_canonica":"33.1 para conceitos gerais de mensageria; 35.1 para serviços/eventos cloud específicos.","fronteira":"F9 detalha RabbitMQ, Kafka e comparação multi-broker; não copia novamente fundamentos gerais."},
 {"tema":"41.x ↔ F7 35.1 e F8 38.x/39.x","fonte_canonica":"35.1 cloud/events; 38.1/38.2 sinais/ferramentas; 39.1 operação madura.","fronteira":"41.1 padrões distribuídos gerais e 41.2 fronteiras/custo. Referenciar observabilidade sem duplicar catálogo."},
 {"tema":"Stacks 42.x–45.1 ↔ F5/F6","fonte_canonica":"F5 18.1–20.x e unidades canônicas de API/testes das Fases 5–6.","fronteira":"F9 trata equivalentes específicos; fundamentos REST/ORM/auth/testes permanecem nas fases-base."},
 {"tema":"46.2/46.3 ↔ projetos anteriores","fonte_canonica":"Cada projeto mantém escopo, marcos e rubrica próprios.","fronteira":"46.2 evolui Trilho A; 46.3 Trilho B. Não copiar requisitos/escalas de projetos anteriores."}]
manifest={"versao_esquema":1,"status_manifesto":"rascunho_para_aprovacao","fase":"Fase_9","base_commit":BASE,"id_prefix":"f9","destino_raiz":DEST,"ordem_unidades":list(srcnames),"paths":{"unidade_pasta":"relativa_a_destino_raiz","arquivos_unidade":"relativos_a_pasta_da_unidade","origem":"relativa_a_raiz_do_repositorio","links_markdown":"relativos_ao_arquivo_de_destino","sem_absolutos":True},"regras":{"estrutural_apenas":True,"criar_conteudo_educacional":False,"preservar_texto_origem":True,"itens_compartilhados":"um destino físico em 90_integracao por unidade; todos os assuntos relacionados referenciados","gabaritos_quiz":"answer_key separado; resposta inline separada por item e marcador literal","gabaritos_pratica":"KP / answer_key_pratica só para feedback/solução existente","rubricas":"separar somente blocos existentes; preservar escalas e descritores","projetos":"marcos planos, aceite checklist, titulo_marco literal; sem marcos inventados","metadados":"lista Markdown transportada ao README YAML sem alterar valores","json":"intocado","originais":"intocados","propostas":"não executar"},"decisoes_aprovadas":{"stacks_candidatas":stacks,"repertorio_fora_da_escolha":["42.2","42.3","43.2","44.2"],"nivel_dominio":"implementar | reconhecer | repertorio","46.2":{"stack_mode":"alternativa","escolha_do_aluno":True,"escolher_uma_stack":stacks},"46.3":{"stack_mode":"principal"}},"fontes_decisao":{"pagina_oficial":PAGE,"referencias":REFS,"mapa_historico":"não localizado; divisões e cobertura reconstruídas marcadas [PROPOSTA]","unidades":"docs/courses/trilhacode/Conteudos/Fase_9"},"modulos":[{"id":m,"nome":n,"unidades":[u for u in srcnames if u.startswith(m+".")]} for m,n in mods.items()],"unidades":units,"normalizacoes_links_relativos_planejadas":linkfix,"propostas_expansao_em_espera":proposals,"reconciliacao_curricular":relations,"estimativa_arquivos":{"por_tipo":types,"por_unidade":perunit,"total":total,"fontes":{"unidades":16,"assuntos":47,"questoes":25,"respostas_inline":25,"flashcards":27,"praticas":33,"rubricas_pratica":9,"rubricas_projeto":2,"marcos":8,"aceites":8},"nota":"Theory por microtópico; Q/K separados; flashcards agrupados por associação; KP/rubric/checklist somente quando há bloco original."}}
manifest_text=yaml.safe_dump(manifest,allow_unicode=True,sort_keys=False,width=120)
parsed=yaml.safe_load(manifest_text)
if len(parsed["unidades"])!=16 or sum(len(x["arquivos"]) for x in parsed["unidades"].values())!=302:raise SystemExit("manifest round trip or total invalid")
if any(not Path(f["origem"]["arquivo_origem"]).exists() for u in units.values() for f in u["arquivos"].values()):raise SystemExit("missing mapped origin")

L=[]
def put(*args):L.extend(args)
put("# Planejamento estrutural — Fase 9","","Estado: rascunho para aprovação; sem geração da árvore.","Base: "+BASE+"; branch migracao-estrutura.","",
"## Decisões e escopo","",
"- Aprovadas previamente: stacks implementáveis 42.1 Django/DRF, 43.1 Laravel, 44.1 ASP.NET Core, 45.1 Spring; 42.2, 42.3, 43.2 e 44.2 fora da escolha. 44.2 é legado; as duas unidades de noções são reconhecimento/repertório.",
"- 46.2: uma stack alternativa escolhida pelo estudante; 46.3 usa stack principal. A escolha concreta fica sem valor até o estudante decidir.",
"- Campo contextual nivel_dominio não substitui os metadados originais. Nenhum mapa histórico de assuntos foi encontrado no checkout; divisões e cobertura semântica abaixo são [PROPOSTA].",
"- Migração futura somente estrutural; expansões ficam em espera.","",
"## Inventário de unidades","",
"Foram comparados página oficial e pasta de fontes: 16/16 arquivos ativos em sete módulos. Metadados estão em listas sob H1, não em frontmatter YAML.","",
"| Unidade | Módulo | Título original | tipo/caráter/profundidade | minutos; tags; status | linhas/palavras | teoria | Q | FC | P |","|---|---|---|---|---|---:|---:|---:|---:|---:|---:|")
for u in srcnames:
 s=sources[u];m=s["meta"]
 put(f"| {u} | {mods[u.split('.')[0]]} | {s['title']} | {m['tipo']}/{m['carater']}/{m['profundidade']} | {m['estimativa_minutos']}; {', '.join(m['tags'])}; {m['status']} | {s['lines']}/{s['words']} | {len(topics.get(u,[]))} | {len(questions(s['text']))} | {len(cards(s['text']))} | {len(practices(s['text']))} |")
put("","Todos os 16 arquivos contêm os sete metadados. A transferência ao README mantém valores, sem preencher ou inferir campos.","","## Assuntos e microtópicos","",
"Cada assunto acompanha um cabeçalho de teoria. O parágrafo inicial de 41.2 permanece com assunto 01. Divisões são propostas, não decisões históricas.","",
"| Unidade | slug | título | origem literal |","|---|---|---|---|")
for u,ss in topics.items():
 for i,(slugv,title) in enumerate(ss):
  origin=("parágrafo inicial + " if u=="41.2" and i==0 else "")+"### "+sources[u]["heads"][i]
  put(f"| {u} | {slugv} | {title} | {origin} |")
put("","Total: 47 assuntos convencionais; 46.2 e 46.3 são contêineres de projeto, sem assuntos fictícios.","","## Cobertura item a item","",
"E = exclusivo; S = compartilhado entre os slugs indicados e com um único destino em 90_integracao; S-only = só tem itens compartilhados; N = sem item. Q, prática e flashcard são tratados como tipos distintos. Classificação [PROPOSTA] segundo enunciado; item integrador não substitui cobertura exclusiva.","")
exp=[]
for u in topics:
 put("### "+u,"")
 def names(a):return ", ".join(topics[u][int(x)-1][0] for x in a)
 for i,(n,b,secname) in enumerate(questions(sources[u]["text"])):
  a=Q[u][i];put(f"- Q{i+1:02d} {'exclusiva' if len(a)==1 else 'compartilhada'} → {names(a)}; origem ## {secname}, item {n}; resposta inline.")
 for i,(n,title,b) in enumerate(practices(sources[u]["text"])):
  a=P[u][i];fb=bool(re.search(r"(?m)^\*\*(Feedback(?: esperado| de referência| para revisar)?|Solução(?: comentada)?):\*\*",b));rb=bool(re.search(r"(?m)^\*\*Rubrica \(0–2 cada, total 10\):\*\*",b))
  put(f"- P{i+1:02d} {title}: {'exclusiva' if len(a)==1 else 'compartilhada'} → {names(a)}; feedback existente={fb}; rubrica prática existente={rb}.")
 for i,c in enumerate(cards(sources[u]["text"])):
  a=FC[u][i];front=c[5:].split("**",1)[0].strip()
  put(f"- FC{i+1:02d} {'exclusivo' if len(a)==1 else 'compartilhado'} → {names(a)}; frente: {front}.")
 cv,esn=coverage(u);put(f"E/S/N={esn['E']}/{esn['S']}/{esn['N']}.","")
 for sl,v in cv.items():
  e=sum(len(v[k]) for k in ("quiz_exclusivos","praticas_exclusivas","flashcards_exclusivos"));sh=sum(len(v[k]) for k in ("quiz_compartilhados","praticas_compartilhadas","flashcards_compartilhados"))
  if not e:exp.append((u,sl,"S-only" if sh else "N"))
put("### Assuntos sem avaliação exclusiva","",
"Lacunas ficam como proposta; nenhum exercício é criado.","","| unidade | slug | hoje | proposta |","|---|---|---|---|")
for u,sl,state in exp:put(f"| {u} | {sl} | {state} | [PROPOSTA EM ESPERA] avaliar verificação própria; não criar na migração. |")
put("","Na leitura atual, 43.1/02 tem FC02 específico sobre Eloquent e é exclusivo; portanto, uma expansão antiga para 43.1/02 não se confirma. 43.1/03 permanece S-only: FC03 e P02 combinam fila/autorização/Eloquent. Não se escreve conteúdo.","","## Projetos","",
"| unidade | objetivo existente (síntese) | entregas e aceites | rubrica | stack/dependências |","|---|---|---|---|---|")
for u in ("46.2","46.3"):
 obj=re.sub(r"\\s+"," ",section(sources[u]["text"],"Objetivo") or "")
 ms="<br>".join(f"M{i+1:02d} {x}" for i,x in enumerate(milestones[u]))
 stack="Trilho A e stack principal preservada; entrega 4 escolhe uma alternativa das quatro stacks aprovadas." if u=="46.2" else "Trilho B e escolha de tipo conforme Guia; stack_mode principal."
 put(f"| {u} | {obj} | {ms}; quatro blocos de aceite | seis dimensões, 0–2 cada, total 12 | {stack} |")
put("","Arquivos planos M01–M04 com titulo_marco literal; C01–C04 com os aceites existentes; R00 com rubrica existente. Sem checklist final adicional. T1–T5 segue dentro do bloco de opções de 46.3.","",
"## Duplicações e fronteiras","",
"| relação | fonte canônica | fronteira Fase 9 |","|---|---|---|",
"| 40.x ↔ F7 33.1/35.1 | 33.1 fundamentos mensageria; 35.1 serviços/events cloud | F9 especifica RabbitMQ, Kafka, cenários e comparação; não duplica fundamentos gerais. |",
"| 41.x ↔ F7 35.1 e F8 38.x/39.x | 35.1 integrações; 38.1/38.2 observabilidade; 39.1 operação madura | F9 41.1 padrões distribuídos; 41.2 limites/custo; referenciar telemetria sem recopiá-la. |",
"| 42.x–45.1 ↔ F5/F6 | F5 18.1–20.x e unidades canônicas de API/testes das Fases 5–6 | F9 apresenta equivalências específicas; REST, ORM, auth e testes base continuam nas fases anteriores. |",
"| 46.2/46.3 ↔ projetos anteriores | cada projeto tem seu brief/rubrica | 46.2 Trilho A; 46.3 Trilho B; sem copiar critérios anteriores. |",
"","Relações literais e wikilinks de cada unidade estão registrados no manifesto.","","## Referências que envelhecem","",
"consultado_em é por referência, nunca global; as fontes atuais registram principalmente 15/10/2026. Links sem data ficam sem data.","",
"- Revalidar preços/drivers SQS, Pub/Sub, MSK; variam por região, configuração e uso, sem tarifa numérica fixa a migrar.",
"- Revalidar versões/suporte nomeados: Kafka 4.2; RabbitMQ, DLX e quorum queues; PHP 7.4 legado, Laravel 13/PHP 8.3+; Phalcon 5.18/6.0/PHP 8.1+; .NET 8/9/10 e janelas; Django 6.1; Java 25/Spring.",
"- APIs/documentação oficial, limites, compatibilidade e suporte podem mudar. Não atualizar durante migração; revisão editorial futura registra data por fonte.",
"- Não há nomes de modelos de IA nem endpoints de IA nas fontes; o conteúdo volátil aqui é framework, serviços, versão e preços.","",
"## Links","",
"- Preservar wikilinks literalmente; vault Obsidian não confirmado.",
"- Três links Markdown de 46.2/46.3 apontam para Guia_Projetos_e_Rotacao_de_Tipos.md, alvo comprovado. Para os arquivos migrados planos, destino relativo proposto: ../../../Guia_Projetos_e_Rotacao_de_Tipos.md. Texto visível intacto; registrar normalização no manifesto/gerador.","",
"## Estimativa de arquivos por unidade","",
"| unidade | assuntos/projeto | Q | K | arquivos FC (cards) | P | KP | rubricas | marcos | aceites | total |","|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
for u in srcnames:
 fs=files[u];n=lambda typ:sum(r["tipo"]==typ for r in fs.values())
 put(f"| {u} | {len(topics.get(u,[])) if u in topics else 'projeto'} | {n('quiz')} | {n('answer_key')} | {n('flashcards')} ({len(cards(sources[u]['text']))}) | {n('practice')} | {n('answer_key_pratica')} | {n('rubric')} | {n('project_milestone')} | {n('checklist')} | {perunit[u]} |")
put("","### Total por tipo","","| tipo | arquivos |","|---|---:|")
for k,v in types.items():put(f"| {k} | {v} |")
put(f"| **Total** | **{total}** |","",
"Estimativa: 302 arquivos, sem arquivos artificiais: 47 theory, 25 quiz + 25 answer_key, 27 cartões agrupados em 24 arquivos, 33 practice, 24 KP de feedback/solução já existente, 9 rubricas de prática e 2 de projeto, 8 milestones, 8 checklists, 16 índices e arquivos comuns/scope. Arquivos comuns e integração sem assuntos fictícios.","",
"## Validação do rascunho","",
"- 16 fontes, 47 assuntos, 25 Q/respostas, 27 flashcards, 33 práticas, 11 rubricas totais, 8 entregas e 8 aceites.",
f"- Parser YAML passou; {total} caminhos e {len(ids)} IDs f9 únicos; sem colisões nos manifestos F1–F8 ({len(oldids)} IDs lidos). Origens, aliases e slugs validados.",
"- Itens compartilhados têm associação explícita e destino único; respostas permanecem ligadas à Q; rubricas/checklists têm origem.",
"- Arquivos 46.2/46.3 mantêm quatro entregas e aceites, escalas originais; sem 8.4/8.x extra.",
"- Nenhuma árvore, JSON, fonte, fase homologada, importador ou commit foi alterado.","",
"## Decisões para a revisão","",
"1. Aprovar slugs e agrupamentos [PROPOSTA], incluindo itens S-only.",
"2. Confirmar split de feedback existente em KP, sem alterar texto.",
"3. Deixar escolha concreta de stack de 46.2/46.3 para o estudante.",
"4. Revalidar referências e versões antes da publicação, com data individual por fonte.")
plan="\n".join(L)+"\n"
outy=Path("docs/migracao/mapa_de_migracao_fase9.yml");outm=Path("docs/migracao/PLANEJAMENTO_FASE9.md")
if outy.exists() or outm.exists():raise SystemExit("Fase 9 planning exists; refuse overwrite")
outy.write_text(manifest_text,encoding="utf-8",newline="\n");outm.write_text(plan,encoding="utf-8",newline="\n")
print(json.dumps({"units":len(units),"theory":sum(map(len,topics.values())),"Q":25,"K":25,"FC":27,"P":33,"practice_feedback_KP":types.get("answer_key_pratica",0),"rubrics":types.get("rubric",0),"milestones":8,"acceptance":8,"files":total,"types":types,"per_unit":perunit,"IDs":len(ids),"paths":len(paths),"guide_links":len(linkfix)},ensure_ascii=False,indent=2))
