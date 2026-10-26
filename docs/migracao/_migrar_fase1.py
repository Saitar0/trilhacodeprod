from pathlib import Path, PurePosixPath
from collections import Counter,defaultdict
import csv,hashlib,json,re,subprocess,sys
ROOT=Path.cwd()
MP=ROOT/"docs/migracao/mapa_de_migracao.yml"
DEST=PurePosixPath("docs/courses/trilhacode/Conteudos_migrado/Fase_1")
MAPCSV=PurePosixPath("docs/migracao/relatorio_mapeamento_fase1.csv")
REPORT=PurePosixPath("docs/migracao/relatorio_validacao_fase1.md")
BASE="9b79751278496e51134a6ab8d495706bb2c700a7"
TICK=chr(96)

def parts(s,sep=","):
    out=[];a=0;q=None;e=False;st=[]
    for i,c in enumerate(s):
        if q:
            if e:e=False
            elif c=="\\" and q=='"':e=True
            elif c==q:q=None
        elif c in ('"',"'"):q=c
        elif c in "[{(":st.append(c)
        elif c in "]})":
            if st:st.pop()
        elif c==sep and not st:out.append(s[a:i].strip());a=i+1
    out.append(s[a:].strip());return out

def pair(s):
    q=None;e=False;st=[]
    for i,c in enumerate(s):
        if q:
            if e:e=False
            elif c=="\\" and q=='"':e=True
            elif c==q:q=None
        elif c in ('"',"'"):q=c
        elif c in "[{(":st.append(c)
        elif c in "]})":
            if st:st.pop()
        elif c==":" and not st:return s[:i].strip(),s[i+1:].strip()
    raise ValueError("bad YAML pair: "+s)

def val(s):
    s=s.strip()
    if not s:return None
    if s.startswith("[") and s.endswith("]"):
        x=s[1:-1].strip();return [] if not x else [val(y) for y in parts(x)]
    if s.startswith("{") and s.endswith("}"):
        x=s[1:-1].strip();d={}
        for z in parts(x) if x else []:
            k,v=pair(z);k=val(k)
            if k in d:raise ValueError("duplicate flow key")
            d[k]=val(v)
        return d
    if s.startswith('"') and s.endswith('"'):return json.loads(s)
    if s.startswith("'") and s.endswith("'"):return s[1:-1].replace("''","'")
    if s.lower()=="true":return True
    if s.lower()=="false":return False
    if s.lower() in ("null","~"):return None
    if re.fullmatch(r"-?\d+",s):return int(s)
    return s

def yaml(s,label):
    ls=s.splitlines();root={};stack=[(-1,root)]
    for i,line in enumerate(ls):
        if not line.strip() or line.lstrip().startswith("#"):continue
        ind=len(line)-len(line.lstrip(" "));x=line.strip()
        while stack and stack[-1][0]>=ind:stack.pop()
        parent=stack[-1][1]
        if x.startswith("- "):
            if not isinstance(parent,list):raise ValueError(f"{label}:{i+1}: list")
            v=val(x[2:]);parent.append(v)
            if isinstance(v,dict):stack.append((ind+1,v))
        else:
            if not isinstance(parent,dict):raise ValueError(f"{label}:{i+1}: map")
            k,v=pair(x);k=val(k)
            if k in parent:raise ValueError(f"{label}:{i+1}: duplicate {k}")
            if v:parent[k]=val(v)
            else:
                nxt=next((z for z in ls[i+1:] if z.strip()),"");ni=len(nxt)-len(nxt.lstrip(" ")) if nxt else -1
                c=[] if ni>ind and nxt.strip().startswith("- ") else {}
                parent[k]=c;stack.append((ind,c))
    return root

def fm(s,label):
    m=re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)",s,re.S)
    if not m:raise ValueError(label+": frontmatter missing")
    return m.group(0).rstrip("\r\n"),yaml(m.group(1),label),s[m.end():]

def fence(s):
    s=s.lstrip()
    if s.startswith(TICK*3):return TICK,len(s)-len(s.lstrip(TICK))
    if s.startswith("~~~"):return "~",len(s)-len(s.lstrip("~"))
    return None

def hpositions(s,n):
    ls=s.splitlines(keepends=True);p=[];fc=None;fn=0;prefix="#"*n+" "
    for i,line in enumerate(ls):
        x=line.rstrip("\r\n")
        if fc:
            y=x.lstrip();k=len(y)-len(y.lstrip(fc))
            if k>=fn and not y[k:].strip():fc=None;fn=0
            continue
        f=fence(x)
        if f:fc,fn=f;continue
        if x.startswith(prefix):p.append(i)
    return ls,p

def split_headings(s,n):
    ls,p=hpositions(s,n)
    if not p:return s,[]
    pre="".join(ls[:p[0]]);out=[]
    for j,start in enumerate(p):
        end=p[j+1] if j+1<len(p) else len(ls)
        out.append((ls[start].rstrip("\r\n")[n+1:].strip(),"".join(ls[start:end])))
    return pre,out

def numbered(s):
    ls=s.splitlines(keepends=True);p=[];fc=None;fn=0
    for i,line in enumerate(ls):
        x=line.rstrip("\r\n")
        if fc:
            y=x.lstrip();k=len(y)-len(y.lstrip(fc))
            if k>=fn and not y[k:].strip():fc=None;fn=0
            continue
        f=fence(x)
        if f:fc,fn=f;continue
        m=re.match(r"^(\d+)\.\s",x)
        if m:p.append((i,int(m.group(1))))
    if not p:return "".join(ls),[]
    out=[]
    for j,(start,num) in enumerate(p):
        end=p[j+1][0] if j+1<len(p) else len(ls);out.append((num,"".join(ls[start:end])))
    return "".join(ls[:p[0][0]]),out

def sha(s):return hashlib.sha256(s.replace("\r\n","\n").replace("\r","\n").encode()).hexdigest()
def fhash(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def words(s):return len(re.findall(r"\b[\wÀ-ÖØ-öø-ÿ]+(?:['’-][\wÀ-ÖØ-öø-ÿ]+)*\b",s))

def fix_manifest(s):
    def one(old,new):
        nonlocal s
        if s.count(old)!=1:raise ValueError("manifest patch mismatch: "+old[:40])
        s=s.replace(old,new,1)
    one("raiz_vault_obsidian: pendente_confirmacao",'raiz_vault_obsidian: "confirmada externamente; fora do repositorio"')
    old='links_obsidian: "Não emitir wikilinks até confirmar a raiz do vault."'
    new='links_obsidian: "README usa links Markdown relativos; wikilinks de origem são preservados. O vault configurado não contém a árvore migrada; incompatibilidade registrada."'
    one(old,new)
    one(new+'\njson:',new+'\ncompatibilidade_obsidian: "Destino fora do vault configurado; wikilinks preservados podem não resolver até integração pelo dono."\njson:')
    one('  campos: [arquivo_id, parent_key, tipo_arquivo, assunto, ordem]\n', '  campos: [arquivo_id, parent_key, tipo_arquivo, assunto, ordem]\n  campos_opcionais: [itens_origem, titulo_marco, escala_rubrica]\n')
    old='        "'+TICK+'.gitignore'+TICK+'": T01'
    if old not in s:
        old='        ".gitignore": T01'
        if old not in s:raise ValueError("slug .gitignore not found in 3.1 map")
        s=s.replace(old,'        "'+TICK+'.gitignore'+TICK+'": T01',1)
    a='      - {tipo: complementar, destino: "3.2"}\n    propostas_em_espera:\n      - "Quiz curto para histórico e branches; não criar."\n'
    b='      - {tipo: complementar, destino: "3.2"}\n    ajustes_conexoes:\n      - "Remover relacao duplicada com 2.1; manter pre-requisito 2.1."\n    propostas_em_espera:\n      - "Quiz curto para histórico e branches; não criar."\n'
    one(a,b)
    return s

def fm_fields(unit_key,rel,kind,subject=None,items=None,order=None,title=None,scale=None):
    fields=[("arquivo_id",file_id(unit_key,rel)),("parent_key",unit_key),("tipo_arquivo",kind)]
    if subject and subject!=".":fields.append(("assunto",subject))
    if order is not None:fields.append(("ordem",order))
    if items:fields.append(("itens_origem",items))
    if title:fields.append(("titulo_marco",title))
    if scale:fields.append(("escala_rubrica",scale))
    return fields

def yaml_scalar(v):return json.dumps(v,ensure_ascii=False)
def frontmatter(fields):
    lines=["---"]
    for k,v in fields:
        if isinstance(v,list):val="["+", ".join(yaml_scalar(x) for x in v)+"]"
        elif isinstance(v,bool):val="true" if v else "false"
        elif isinstance(v,int):val=str(v)
        else:val=yaml_scalar(str(v))
        lines.append(f"{k}: {val}")
    return "\n".join(lines)+"\n---\n\n"
def file_id(uk,rel):
    key=re.sub(r"[^a-zA-Z0-9]+","-",uk).strip("-").lower()
    stem=re.sub(r"[^a-zA-Z0-9]+","-",str(PurePosixPath(rel).with_suffix("")).strip("/")).strip("-").lower()
    return f"f1-{key}-{stem}"
def put(uk,rel,kind,body,subject=None,items=None,order=None,title=None,scale=None):
    path=DEST/PurePosixPath(manifest["unidades"][uk]["pasta"])/PurePosixPath(rel)
    content=frontmatter(fm_fields(uk,rel,kind,subject,items,order,title,scale))+norm(body)
    if path in output:raise ValueError("duplicate physical output path: "+str(path))
    output[path]=content
    return rel

def record(uk,item,text,rel,kind):
    ledger.append((uk,item,norm(text),rel,kind))
def src(uk):return (ROOT/"docs/courses/trilhacode"/manifest["unidades"][uk]["origem"]).read_text(encoding="utf-8-sig")
def section(sections,name):
    matches=[block for title,block in sections if title==name]
    if len(matches)!=1:raise ValueError(f"section {name!r} count={len(matches)}")
    return matches[0]
def h3_chunks(text):return split_headings(text,3)
def marker(line):
    if re.match(r"\*\*(?:Gabarito|Referência para autocorreção)",line):return "answer"
    if re.match(r"\*\*(?:Critérios de autocorreção|Autocorreção:)",line):return "rubric"
    if re.match(r"\*\*(?:Aceite:|Critérios:|Verificação final:)",line):return "checklist"
    return None
def split_markers(text):
    out=[];buf=[];kind=None
    for line in norm(text).splitlines(keepends=True):
        if line.startswith("**Retorno espaçado:**") and kind=="rubric":
            out.append((kind,"".join(buf)));buf=[];kind=None
        k=marker(line)
        if k:
            if buf:out.append((kind,"".join(buf)));buf=[]
            kind=k
        buf.append(line)
    if buf:out.append((kind,"".join(buf)))
    return out
def norm(s):return s.replace("\r\n","\n").replace("\r","\n")
def adjust_connections(uk,text):
    drop={"3.1":("Relacionado","2.1"),"3.4":("Relacionado","3.3"),"3.5":("Complementar","3.3")}.get(uk)
    if not drop:return text
    relation,dest=drop;kept=[];found=[]
    for line in norm(text).splitlines(keepends=True):
        if line.startswith("- "+relation+":") and f"#{dest} " in line:found.append(line)
        else:kept.append(line)
    if len(found)!=1:raise ValueError(f"{uk}: duplicate relation expected once, found {len(found)}")
    removed.append((uk,dest,relation,found[0].rstrip("\n")))
    return "".join(kept)
def make_readme(uk,u,origfm,title):
    header,_,_=fm(origfm,"source frontmatter")
    header=header.rsplit("---",1)[0]+f"arquivo_id: {file_id(uk,'README.md')}\ntipo_arquivo: topic_index\n---"
    lines=[header,"",title,"","## Índice","","### Arquivos comuns"]
    for code,c in manifest["arquivos_comuns"].items():
        if code!="IDX":lines.append(f"- [{c['tipo']}]({c['path']})")
    lines += ["","### Assuntos"]
    for slug in u.get("assuntos",[]):
        lines.append(f"\n#### `{slug}`")
        for rel in u.get("arquivos",{}).values():
            if rel.startswith(slug+"/"):lines.append(f"- [{PurePosixPath(rel).name}]({rel})")
    integration=[rel for rel in u.get("arquivos",{}).values() if rel.startswith("90_integracao/")]
    if integration:
        lines += ["","### Integração"]
        lines += [f"- [{PurePosixPath(rel).name}]({rel})" for rel in integration]
    listed={rel for rel in u.get("arquivos",{}).values() if any(rel.startswith(s+"/") for s in u.get("assuntos",[])) or rel.startswith("90_integracao/")}
    extras=[rel for rel in u.get("arquivos",{}).values() if rel not in listed]
    if extras:
        lines += ["","### Projeto e materiais"]
        lines += [f"- [{PurePosixPath(rel).name}]({rel})" for rel in extras]
    root=DEST/PurePosixPath(u["pasta"]);path=root/"README.md"
    if path in output:raise ValueError("duplicate README")
    output[path]="\n".join(lines)+"\n"
def quiz_split(text):
    pre,subs=split_headings(text,3);qpre="";apre="";qitems=[];aitems=[]
    if subs:
        for h,part in subs:
            if "gabarito" in h.casefold():
                apre,answers=numbered(part);aitems.extend(answers)
            else:
                p,qs=numbered(part)
                if not qpre:qpre=pre+p
                qitems.extend(qs)
    else:qpre,qitems=numbered(text)
    if not qitems:raise ValueError("quiz has no numbered questions")
    qs={};ans={}
    for n,block in qitems:
        out=[];key=[]
        for line in norm(block).splitlines(keepends=True):
            m=re.search(r"\s*(\*\*Resposta:.*?\*\*.*?)(\n)?$",line)
            if m:
                out.append(line[:m.start(1)].rstrip()+("\n" if line.endswith("\n") else ""));key.append(m.group(1)+("\n" if line.endswith("\n") else ""))
            else:out.append(line)
        qs[n]="".join(out)
        if key:ans[n]="".join(key)
    for n,block in aitems:
        if n in ans:raise ValueError(f"duplicate answer for Q{n}")
        ans[n]=block
    return qpre,apre,qs,ans

def emit_common(uk,u,sections):
    common=[("OBJ","Objetivo"),("RES","Resumo"),("CRI","Critério de conclusão"),("CON","Conexões"),("REF","Referências")]
    for i,(code,title) in enumerate(common,1):
        block=section(sections,title)
        if code=="CON":block=adjust_connections(uk,block)
        rel=manifest["arquivos_comuns"][code]["path"]
        put(uk,rel,manifest["arquivos_comuns"][code]["tipo"],block,order=i)
        record(uk,title,block,rel,"common")
def emit_theory(uk,u,sections):
    block=section(sections,"Teoria");pre,parts=h3_chunks(block)
    mapping=u["blocos_origem"]["teoria"];groups=defaultdict(list);items=defaultdict(list)
    for h,b in parts:
        if h not in mapping:raise ValueError(f"{uk}: unmapped theory heading {h!r}")
        groups[mapping[h]].append(b);items[mapping[h]].append(h)
    expected={fid for fid in u["arquivos"] if fid.startswith("T")}
    if set(groups)!=expected:raise ValueError(f"{uk}: theory ids mapped {set(groups)}, expected {expected}")
    first=sorted(groups,key=lambda x:int(x[1:]))[0]
    groups[first].insert(0,pre)
    if pre.strip():record(uk,"Teoria/cabeçalho",pre,u["arquivos"][first],"theory")
    for fid in sorted(groups,key=lambda x:int(x[1:])):
        rel=u["arquivos"][fid];subject=str(PurePosixPath(rel).parent)
        put(uk,rel,"theory","".join(groups[fid]),subject,items[fid],int(fid[1:]))
        for h,b in zip(items[fid],[x for n,x in parts if mapping[n]==fid]):record(uk,"Teoria/"+h,b,rel,"theory")
def emit_practice(uk,u,sections):
    names={n for n,b in sections}
    pname="Prática — revisão periódica do repositório" if "Prática — revisão periódica do repositório" in names else "Prática — três níveis"
    block=section(sections,pname);pre,parts=h3_chunks(block)
    pmap=u["blocos_origem"].get("pratica",{});pids=[k for k in pmap if re.fullmatch(r"P\d+",k)];pids.sort(key=lambda x:int(x[1:]))
    if len(pids)==len(parts):activities=[(pids[i],(pre if i==0 else "")+b) for i,(_,b) in enumerate(parts)]
    elif len(pids)==len(parts)+1 and pre.strip():activities=[(pids[0],pre)]+[(pids[i+1],b) for i,(_,b) in enumerate(parts)]
    else:raise ValueError(f"{uk}: practice mapping blocks={len(parts)} items={len(pids)}")
    for item,activity in activities:
        spec=pmap[item];fid=spec["arquivo"];rel=u["arquivos"][fid]
        subject=spec.get("assunto")
        if not subject and len(spec.get("assuntos",[]))==1:subject=spec["assuntos"][0]
        if not subject:subject=None if rel.startswith("90_integracao/") else str(PurePosixPath(rel).parent)
        kept=[];moved=[]
        for kind,frag in split_markers(activity):
            if kind is None:kept.append(frag);continue
            target={"answer":"resposta","rubric":"rubrica","checklist":"checklist"}[kind]
            if target not in spec:raise ValueError(f"{uk}/{item}: {kind} marker has no destination")
            moved.append((kind,spec[target],frag))
        put(uk,rel,"practice","".join(kept),subject,[item],int(item[1:]))
        for i,frag in enumerate(kept,1):record(uk,item+f"/conteudo_{i}",frag,rel,"practice")
        for kind,dfid,frag in moved:
            artifact_fragments[(uk,dfid)].append((item,frag))
            record(uk,item+"/"+kind,frag,u["arquivos"][dfid],{"answer":"answer_key_pratica","rubric":"rubric","checklist":"checklist"}[kind])
def split_project_block(block):
    body=[];check=[];rub=[]
    for line in norm(block).splitlines(keepends=True):
        if line.startswith("**Aceite:**") or line.startswith("**Critérios:**") or line.startswith("**Verificação final:**"):check.append(line)
        elif line.startswith("**Rubrica comum para cada marco"):rub.append(line)
        else:body.append(line)
    return "".join(body),"".join(check),"".join(rub)
def emit_project(uk,u,sections):
    block=section(sections,"Projeto — base de trabalho do curso");pre,parts=h3_chunks(block)
    intro=u["blocos_origem"]["projeto"]["intro"];rel=u["arquivos"][intro["arquivo"]]
    put(uk,rel,"project_brief",pre,order=0);record(uk,"Projeto/intro",pre,rel,"project_brief")
    expected={k:v for k,v in u["blocos_origem"]["projeto"].items() if re.fullmatch(r"M\d+",k)}
    seen=set();rubrics=[];review=[]
    for title,part in parts:
        if title=="Revisão final do projeto":review.append(part);continue
        pair=[(k,v) for k,v in expected.items() if v["titulo_marco"]==title]
        if len(pair)!=1:raise ValueError(f"3.5: source milestone title mismatch: {title!r}")
        code,spec=pair[0];seen.add(code);body,check,rub=split_project_block(part)
        mrel=u["arquivos"][spec["arquivo"]]
        put(uk,mrel,"milestone",body,items=[code],order=int(code[1:]),title=title)
        record(uk,code+"/body",body,mrel,"milestone")
        if not check:raise ValueError(f"3.5 {code}: acceptance text missing")
        cfid=spec["checklist"];crel=u["arquivos"][cfid]
        artifact_fragments[(uk,cfid)].append((code,check));record(uk,code+"/acceptance",check,crel,"checklist")
        if rub:rubrics.append(rub)
    if seen!=set(expected) or len(review)!=1 or len(rubrics)!=1:raise ValueError("3.5 milestones/review/rubric incomplete")
    cfid=u["blocos_origem"]["projeto"]["checklist_final"]["arquivo"];crel=u["arquivos"][cfid]
    put(uk,crel,"checklist",review[0],items=["revisao_final"],order=0);record(uk,"Projeto/revisao_final",review[0],crel,"checklist")
    rfid=u["blocos_origem"]["projeto"]["rubrica"]["arquivo"];rrel=u["arquivos"][rfid]
    put(uk,rrel,"rubric",rubrics[0],items=["rubrica_comum"],order=0,scale="0-4");record(uk,"Projeto/rubrica_comum",rubrics[0],rrel,"rubric")

def emit_quiz(uk,u,sections):
    block=section(sections,"Verificação — quiz");pre,answer_pre,qs,answers=quiz_split(block)
    qmap=u["blocos_origem"].get("quiz",{})
    if set(qmap)!={"Q"+str(n) for n in qs}:raise ValueError(f"{uk}: quiz mapping/source IDs differ")
    if set(answers)!=set(qs):raise ValueError(f"{uk}: quiz answer IDs differ: Q={set(qs)}, A={set(answers)}")
    qgroups=defaultdict(list);kgroups=defaultdict(list);qrefs=defaultdict(list);krefs=defaultdict(list)
    for n in sorted(qs):
        item="Q"+str(n);spec=qmap[item];qfid=spec["arquivo"];kfid=spec["resposta"]
        qgroups[qfid].append(qs[n]);kgroups[kfid].append(answers[n]);qrefs[qfid].append(item);krefs[kfid].append(item)
        qrel=u["arquivos"][qfid];krel=u["arquivos"][kfid]
        record(uk,item,qs[n],qrel,"quiz");record(uk,item+"/answer",answers[n],krel,"answer_key")
    firstq=next(iter(qgroups));qgroups[firstq].insert(0,pre)
    if pre.strip():record(uk,"Quiz/header",pre,u["arquivos"][firstq],"quiz")
    if answer_pre:
        firstk=next(iter(kgroups));kgroups[firstk].insert(0,answer_pre)
        record(uk,"Quiz/answer_header",answer_pre,u["arquivos"][firstk],"answer_key")
    for fid,chunks in qgroups.items():
        rel=u["arquivos"][fid];s=str(PurePosixPath(rel).parent);put(uk,rel,"quiz","".join(chunks),None if s=="90_integracao" else s,qrefs[fid],int(re.search(r"\d+",fid).group()))
    for fid,chunks in kgroups.items():
        rel=u["arquivos"][fid];s=str(PurePosixPath(rel).parent);put(uk,rel,"answer_key","".join(chunks),None if s=="90_integracao" else s,krefs[fid],int(re.search(r"\d+",fid).group()))
def emit_unit(uk,u):
    original=src(uk);header,original_meta,body=fm(original,u["origem"]);_,sections=split_headings(body,2)
    h1=title_from(body);original_headers[uk]=header;source_meta[uk]=original_meta;source_titles[uk]=h1
    emit_common(uk,u,sections);emit_theory(uk,u,sections)
    if u.get("tipo_unidade")=="projeto":emit_project(uk,u,sections)
    else:emit_quiz(uk,u,sections);emit_practice(uk,u,sections)
    make_readme(uk,u,header,h1)
def file_ids_for(uk,u):
    root=DEST/PurePosixPath(u["pasta"]);items={root/"README.md"}
    items.update(root/PurePosixPath(p) for p in u["arquivos"].values())
    items.update(root/PurePosixPath(c["path"]) for k,c in manifest["arquivos_comuns"].items() if k!="IDX")
    return items
def flush_artifacts(uk,u):
    for (owner,fid),items in list(artifact_fragments.items()):
        if owner!=uk:continue
        if fid not in u["arquivos"]:raise ValueError(f"{uk}: unmapped artifact {fid}")
        rel=u["arquivos"][fid];kind="answer_key_pratica" if fid.startswith("KP") else "rubric" if fid.startswith("R") else "checklist"
        body="".join(x[1] for x in items)
        if not body.strip():raise ValueError(f"empty artifact: {uk}/{fid}")
        parent=str(PurePosixPath(rel).parent);subject=None if parent=="90_integracao" else parent
        put(uk,rel,kind,body,subject,[x[0] for x in items],int(re.search(r"\d+",fid).group()),scale="0-4" if uk=="3.5" and fid=="R00" else None)
def expected_all():
    result=set()
    for uk,u in manifest["unidades"].items():result |= file_ids_for(uk,u)
    return result
def validate_all(snapshots,json_hash):
    errors=[];expected=expected_all()
    if set(output)!=expected:errors.append(f"output path set mismatch missing={len(expected-set(output))}, extra={len(set(output)-expected)}")
    ids={};types=Counter()
    for path,text in output.items():
        try:header,meta,body=fm(text,str(path)); parsed=yaml(header[4:-4],str(path))
        except Exception as exc:errors.append(f"invalid frontmatter {path}: {exc}");continue
        fid=parsed.get("arquivo_id")
        if not fid:errors.append(f"arquivo_id missing: {path}")
        elif fid in ids:errors.append(f"duplicate arquivo_id {fid}: {ids[fid]} / {path}")
        else:ids[fid]=path
        types[parsed.get("tipo_arquivo","?")]+=1
        if path.name!="README.md":
            if not parsed.get("parent_key"):errors.append(f"parent_key missing: {path}")
            if any(k in parsed for k in ("key","estimativa_minutos","tags","status")):errors.append(f"parent metadata duplicated in child: {path}")
        if not body.strip():errors.append(f"empty generated file: {path}")
    # Verify each recorded source block fragment occurs in its single mapped destination.
    for uk,item,fragment,rel,kind in ledger:
        root=DEST/PurePosixPath(manifest["unidades"][uk]["pasta"]);path=root/PurePosixPath(rel)
        if path not in output:errors.append(f"mapped destination absent {uk}/{item}: {path}");continue
        target=fm(output[path],str(path))[2]
        if norm(fragment) not in norm(target):errors.append(f"block not found at mapped destination {uk}/{item} -> {rel}")
    # Validate coverage classifications and that shared content has one integration destination.
    for uk,u in manifest["unidades"].items():
        maps=u.get("blocos_origem",{});items={**maps.get("quiz",{}),**{k:v for k,v in maps.get("pratica",{}).items() if re.fullmatch(r"P\d+",k)}}
        if set(u.get("cobertura",{}).get("exclusivos",{})) & set(u.get("cobertura",{}).get("compartilhados",{})):errors.append(f"coverage class overlap {uk}")
        cov=u.get("cobertura",{}); exclusive={}
        for subject,labels in cov.get("exclusivos",{}).items():
            for label in labels:exclusive[label]=[subject]
        shared=cov.get("compartilhados",{});allcov={**exclusive,**shared}
        for label,subjects in allcov.items():
            spec=items.get(label)
            if not spec:errors.append(f"coverage item has no source mapping {uk}/{label}");continue
            assoc=subjects if isinstance(subjects,list) else [subjects]
            rel=u["arquivos"].get(spec.get("arquivo"),"")
            if len(assoc)>1 and not rel.startswith("90_integracao/"):errors.append(f"shared item not unique in integration {uk}/{label}")
            if len(assoc)==1 and spec.get("assunto") and assoc[0]!=spec["assunto"]:errors.append(f"exclusive subject mismatch {uk}/{label}")
            if len(assoc)>1 and set(assoc)!=set(spec.get("assuntos",[])):errors.append(f"shared subject mismatch {uk}/{label}")
        # Relative Markdown links in each topic index must resolve.
        root=DEST/PurePosixPath(u["pasta"]);readme=output[root/"README.md"]
        for href in re.findall(r"\]\(([^)]+)\)",readme):
            target=root/PurePosixPath(href)
            if "://" not in href and not href.startswith("#") and target not in output:errors.append(f"README link not found {uk}: {href}")
        original=src(uk);_,origmeta,srcbody=fm(original,u["origem"]);_,readmeta,_=fm(readme,"README")
        for k,v in origmeta.items():
            if readmeta.get(k)!=v:errors.append(f"original metadata changed {uk}/{k}")
        srcwords=words(srcbody);dstwords=words(title_from(srcbody))
        for path,text in output.items():
            if root in path.parents and path.name!="README.md":dstwords+=words(fm(text,str(path))[2])
        removed_words=sum(words(line) for unit,dest,rel,line in removed if unit==uk)
        if srcwords!=dstwords+removed_words:errors.append(f"word count mismatch {uk}: source={srcwords}, migrated={dstwords}, authorized_removed={removed_words}")
        if uk!="3.5":
            quiz=quiz_split(section(split_headings(fm(original,u["origem"])[2],2)[1],"Verificação — quiz"))[2]
            if set("Q"+str(x) for x in quiz)!=set(maps.get("quiz",{})):errors.append(f"quiz mapping mismatch {uk}")
    for rel,h in snapshots.items():
        if fhash(ROOT/rel)!=h:errors.append("original source changed: "+rel)
    if fhash(ROOT/json_rel)!=json_hash:errors.append("import JSON changed")
    return errors,types

def title_from(text):
    m=re.search(r"(?m)^# .+$",text);return m.group(0) if m else ""
common_order={"OBJ":1,"RES":2,"CRI":3,"CON":4,"REF":5}
def run(apply=False):
    global manifest,output,ledger,artifact_fragments,removed,original_headers,source_meta,source_titles,json_rel
    output={};ledger=[];artifact_fragments=defaultdict(list);removed=[];original_headers={};source_meta={};source_titles={}
    manifest_text=fix_manifest(MP.read_text(encoding="utf-8-sig"));manifest=yaml(manifest_text,"migration manifest")
    head=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
    branch=subprocess.check_output(["git","branch","--show-current"],cwd=ROOT,text=True).strip()
    if head!="9b79751278496e51134a6ab8d495706bb2c700a7":raise SystemExit("HEAD não corresponde à base verificada; interrompido.")
    if branch!="migracao-estrutura":raise SystemExit("branch isolada inesperada; interrompido.")
    if subprocess.call(["git","diff","--quiet","HEAD","--"],cwd=ROOT)!=0:raise SystemExit("há alterações rastreadas no worktree isolado; interrupção preventiva.")
    dest=ROOT/DEST
    if dest.exists():raise SystemExit("destino já existe; não sobrescrever.")
    src_rel=["docs/courses/trilhacode/"+u["origem"] for u in manifest["unidades"].values()]
    src_rel.append("docs/courses/trilhacode/Fase_1_Base_Tecnica.md")
    snapshots={rel:fhash(ROOT/rel) for rel in src_rel}
    json_rel="docs/courses/trilhacode/trilha-code-bulk-import.json";json_hash=fhash(ROOT/json_rel)
    for uk in manifest["ordem_unidades"]:emit_unit(uk,manifest["unidades"][uk])
    for uk in manifest["ordem_unidades"]:flush_artifacts(uk,manifest["unidades"][uk])
    errors,types=validate_all(snapshots,json_hash)
    if errors:
        print("VALIDATION FAILED")
        for error in errors:print("- "+error)
        return 2
    perunit=[]
    for uk in manifest["ordem_unidades"]:
        u=manifest["unidades"][uk];root=DEST/PurePosixPath(u["pasta"])
        source=fm(src(uk),u["origem"])[2]
        destwords=words(title_from(source))+sum(words(fm(txt,str(p))[2]) for p,txt in output.items() if root in p.parents and p.name!="README.md")
        removedwords=sum(words(line) for unit,destid,rel,line in removed if unit==uk)
        perunit.append((uk,words(source),destwords,removedwords,sum(1 for p in output if root in p.parents),sum(1 for row in ledger if row[0]==uk)))
    if not apply:
        print(f"DRY-RUN OK | base={head} | branch={branch} | units={len(manifest['ordem_unidades'])} | files={len(output)} | mappings={len(ledger)}")
        print("types="+json.dumps(types,ensure_ascii=True,sort_keys=True))
        for row in perunit:print("unit="+"|".join(map(str,row)))
        print("removed_connections="+str(len(removed))+" source_hashes="+str(len(snapshots))+" json="+json_hash)
        return 0
    # The authorized write boundary is only the isolated Fase 1 tree and migration audit files.
    for rel,text in sorted(output.items(),key=lambda x:str(x[0])):
        target=ROOT/rel;target.parent.mkdir(parents=True,exist_ok=True)
        with target.open("w",encoding="utf-8",newline="\n") as stream:stream.write(norm(text))
    with MP.open("w",encoding="utf-8",newline="\n") as stream:stream.write(norm(manifest_text))
    persisted={}
    for rel in expected_all():
        path=ROOT/rel
        if not path.is_file():errors.append("missing persisted file: "+str(rel))
        else:persisted[rel]=path.read_text(encoding="utf-8-sig")
    output=persisted
    errors2,types2=validate_all(snapshots,json_hash);errors.extend(errors2)
    if errors:
        print("POST-WRITE VALIDATION FAILED")
        for error in errors:print("- "+error)
        return 3
    with (ROOT/MAPCSV).open("w",encoding="utf-8",newline="") as stream:
        writer=csv.writer(stream);writer.writerow(["unidade","origem","bloco","tipo","destino","palavras","sha256_bloco"])
        for uk,item,fragment,rel,kind in ledger:
            destrel=DEST/PurePosixPath(manifest["unidades"][uk]["pasta"])/PurePosixPath(rel)
            writer.writerow([uk,manifest["unidades"][uk]["origem"],item,kind,str(destrel),words(fragment),sha(fragment)])
    report=["# Auditoria da migração estrutural — Fase 1","",f"- Base Git: `{head}`","- Branch isolada: `{branch}`","- Destino: `{DEST}/`","- Unidades: {len(manifest['ordem_unidades'])}",f"- Arquivos criados: {len(output)}",f"- Blocos mapeados: {len(ledger)}","- JSON: não modificado nem importado.","", "## Tipos de arquivo", ""]
    report += [f"- `{kind}`: {n}" for kind,n in sorted(types2.items())]
    report += ["", "## Integridade por unidade", "", "| Unidade | Palavras origem | Palavras migradas | Remoção aprovada | Arquivos | Blocos mapeados | Resultado |", "|---|---:|---:|---:|---:|---:|---|"]
    for uk,sw,dw,rw,nf,nm in perunit:report.append(f"| {uk} | {sw} | {dw} | {rw} | {nf} | {nm} | OK |")
    report += ["", "## Validações", "", "- Todos os caminhos declarados e os arquivos comuns esperados estão presentes; nenhum destino extra foi gerado.","- Cada fragmento registrado no CSV foi encontrado no arquivo físico mapeado.","- Itens compartilhados têm um destino físico em `90_integracao/`; cobertura e slugs conferem com o manifesto.","- Frontmatter é YAML parseável; `arquivo_id` é único; valores originais permanecem no README e metadados de unidade não se repetem nos filhos.","- Todos os links Markdown relativos de README resolvem dentro da unidade.","- Contagem de palavras por unidade coincide; a diferença registrada corresponde apenas às relações duplicadas aprovadas.","- SHA-256 de cada unidade original, da nota de fase e do JSON permaneceu inalterado.","- O importador não foi executado; nenhuma escala de rubrica foi alterada.","", "## Links Obsidian", "", "O vault configurado é externo ao repositório e contém uma cópia antiga independente da Fase 1. Os wikilinks de origem foram preservados em `03_conexoes.md`; eles não resolvem para esta árvore enquanto ela ficar fora do vault. Os links do README são relativos ao repositório e foram validados.","", "## Remoções estruturais aprovadas", ""]
    for uk,destid,rel,line in removed:report.append(f"- {uk}: {rel} `{destid}` removida por duplicar o pré-requisito; texto original mantido no CSV/hash e removido somente conforme decisão aprovada.")
    report += ["", "## Hashes de controle", ""]
    for rel,h in sorted(snapshots.items()):report.append(f"- `{rel}`: `{h}` (inalterado)")
    report.append(f"- `{json_rel}`: `{json_hash}` (inalterado)")
    report += ["", "O mapeamento por bloco está em `docs/migracao/relatorio_mapeamento_fase1.csv`.",""]
    with (ROOT/REPORT).open("w",encoding="utf-8",newline="\n") as stream:stream.write("\n".join(report))
    print(f"MIGRATION OK | base={head} | branch={branch} | files={len(output)} | mappings={len(ledger)}")
    print("types="+json.dumps(types2,ensure_ascii=True,sort_keys=True))
    for row in perunit:print("unit="+"|".join(map(str,row)))
    print(f"report={REPORT} map={MAPCSV} source_hashes={len(snapshots)} json_hash={json_hash}")
    return 0
if __name__=="__main__":raise SystemExit(run("--apply" in sys.argv))
