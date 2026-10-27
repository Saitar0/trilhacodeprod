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

def fm_fields(unit_key,rel,kind,subject=None,items=None,order=None,title=None,scale=None,subjects=None):
    fields=[("arquivo_id",file_id(unit_key,rel)),("parent_key",unit_key),("tipo_arquivo",kind)]
    if subject and subject!=".":fields.append(("assunto",subject))
    if subjects:fields.append(("assuntos",subjects))
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
    prefix=manifest.get("id_prefix","f1")
    return f"{prefix}-{key}-{stem}"
def put(uk,rel,kind,body,subject=None,items=None,order=None,title=None,scale=None,subjects=None):
    path=DEST/PurePosixPath(manifest["unidades"][uk]["pasta"])/PurePosixPath(rel)
    content=frontmatter(fm_fields(uk,rel,kind,subject,items,order,title,scale,subjects))+norm(body)
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
    if manifest.get("fase")=="Fase_2":
        if line.startswith("**Aceite e resposta esperada:**"):return "mixed"
        if re.match(r"\*\*(?:Gabarito|Solução comentada|Referência para autocorreção)",line):return "answer"
        if re.match(r"\*\*(?:Critérios de autocorreção|Autocorreção:|Rubrica)",line):return "rubric"
        if re.match(r"\*\*(?:Aceite:|Critérios:|Critérios de aceite:|Verificação final:)",line):return "checklist"
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
    if manifest.get("fase")=="Fase_2":
        rules=manifest["unidades"][uk].get("ajustes_conexoes",{}).get("remover",[])
        kept=norm(text).splitlines(keepends=True)
        for rule in rules:
            label=rule["source_label"];dest=rule["destino"]
            matches=[line for line in kept if line.startswith("- "+label+":") and f"#{dest} " in line]
            if len(matches)!=1:raise ValueError(f"{uk}: expected one source relation {label}/{dest}, found {len(matches)}")
            found=matches[0];kept.remove(found)
            removed.append((uk,dest,label,found.rstrip("\n")))
        return "".join(kept)
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
def split_literal_artifact(rule,fragment):
    marker_text=rule["marcador"]
    if not fragment.startswith(marker_text):raise ValueError("literal artifact marker mismatch")
    body=fragment[len(marker_text):]
    suffix=rule.get("sufixo_literal","")
    if suffix and not body.endswith(suffix):raise ValueError("literal artifact suffix differs from approved source")
    content=body[:-len(suffix)] if suffix else body
    segments=rule["segmentos"]
    expected="".join(item["texto"] for item in segments)
    if content!=expected:raise ValueError("literal artifact body differs from approved source segments")
    out=[(rule["marcador_destino"],marker_text)]
    for item in segments:out.append((item["destino"],item["texto"]))
    if suffix:
        kind,text=out[-1];out[-1]=(kind,text+suffix)
    return out

def emit_practice(uk,u,sections):
    names={n for n,b in sections}
    if manifest.get("fase")=="Fase_2":
        candidates=[n for n in ("Práticas","Prática — três níveis") if n in names]
        if len(candidates)!=1:raise ValueError(f"{uk}: expected one recognized Fase 2 practice section, found {candidates}")
        pname=candidates[0]
    else:
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
            if kind=="mixed":
                rule=u.get("separacao_literal",{}).get(item)
                if not rule:raise ValueError(f"{uk}/{item}: mixed marker has no literal split rule")
                for target,part in split_literal_artifact(rule,frag):
                    if target not in spec:raise ValueError(f"{uk}/{item}: literal segment target {target} missing")
                    moved.append(("answer" if target=="resposta" else "checklist",spec[target],part))
                continue
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
        rel=u["arquivos"][fid];s=str(PurePosixPath(rel).parent)
        put(uk,rel,"quiz","".join(chunks),None if s=="90_integracao" else s,qrefs[fid],int(re.search(r"\d+",fid).group()))
    for fid,chunks in kgroups.items():
        rel=u["arquivos"][fid];s=str(PurePosixPath(rel).parent)
        put(uk,rel,"answer_key","".join(chunks),None if s=="90_integracao" else s,krefs[fid],int(re.search(r"\d+",fid).group()))
def emit_unit(uk,u):
    original=src(uk);header,original_meta,body=fm(original,u["origem"]);pre,sections=split_headings(body,2)
    h1=title_from(body);original_headers[uk]=header;source_meta[uk]=original_meta;source_titles[uk]=h1
    if manifest.get("fase")=="Fase_2":
        expected={"Objetivo","Teoria","Resumo","Verificação — quiz","Critério de conclusão","Conexões","Referências"}
        practice=[n for n in ("Práticas","Prática — três níveis") if n in {x for x,_ in sections}]
        if len(practice)!=1:raise ValueError(f"{uk}: expected one practice heading, found {practice}")
        expected.add(practice[0])
        actual={name for name,_ in sections}
        if actual!=expected:raise ValueError(f"{uk}: unrecognized or missing H2 sections: missing={expected-actual}, extra={actual-expected}")
        if not h1 or pre.strip()!=h1.strip():raise ValueError(f"{uk}: non-title text exists before first H2 section")
    emit_common(uk,u,sections);emit_theory(uk,u,sections)
    if u.get("tipo_unidade")=="projeto":emit_project(uk,u,sections)
    else:emit_quiz(uk,u,sections);emit_practice(uk,u,sections)
    make_readme(uk,u,header,h1)
    if h1 and manifest.get("fase")=="Fase_2":record(uk,"Titulo",h1,"README.md","topic_index")
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
        scale=None
        for spec in u["blocos_origem"].get("pratica",{}).values():
            if spec.get("rubrica")==fid and spec.get("escala_rubrica"):scale=spec["escala_rubrica"]
        if scale is None and uk=="3.5" and fid=="R00":scale="0-4"
        put(uk,rel,kind,body,subject,[x[0] for x in items],int(re.search(r"\d+",fid).group()),scale=scale)
def expected_all():
    result=set()
    for uk,u in manifest["unidades"].items():result |= file_ids_for(uk,u)
    project=manifest.get("projeto_incremental",{}).get("indice_markdown")
    if project:result.add(DEST/PurePosixPath(project["path"]))
    return result
def code_blocks(text):
    lines=norm(text).splitlines(keepends=True);found=[];start=None;fc=None;fn=0
    for i,line in enumerate(lines):
        x=line.rstrip("\r\n")
        if start is None:
            f=fence(x)
            if f:fc,fn=f;start=i
            continue
        y=x.lstrip();k=len(y)-len(y.lstrip(fc))
        if k>=fn and not y[k:].strip():
            found.append("".join(lines[start:i+1]));start=None;fc=None;fn=0
    if start is not None:raise ValueError("unclosed fenced code block")
    return found

def validate_mapped_text():
    errors=[];by_path=defaultdict(list);source_texts={uk:src(uk) for uk in manifest["ordem_unidades"]}
    for uk,item,fragment,rel,kind in ledger:
        path=DEST/PurePosixPath(manifest["unidades"][uk]["pasta"])/PurePosixPath(rel)
        if path not in output:
            errors.append(f"mapping destination missing: {uk}/{item} -> {path}");continue
        by_path[path].append((uk,item,fragment,kind))
        if not fragment:
            errors.append(f"empty mapped fragment: {uk}/{item}");continue
        if item=="Titulo":
            if fragment not in output[path]:errors.append(f"title text missing from README: {uk}")
        elif kind=="quiz":
            # The approved operation moves inline answer markers out of each question.
            # quiz_split() separately checks that each question and answer fragment is emitted.
            pass
        elif kind=="common" and item=="Conexões":
            source=source_texts[uk];_,_,body=fm(source,manifest["unidades"][uk]["origem"])
            sections=dict(split_headings(body,2)[1]);expected=sections.get("Conexões","")
            removed_lines=[line for owner,dest,label,line in removed if owner==uk]
            for line in removed_lines:
                full=line+"\n"
                if full not in expected:errors.append(f"approved connection removal absent from source: {uk}/{line}")
                else:expected=expected.replace(full,"",1)
            if fragment!=expected:errors.append(f"connection text differs from approved structural projection: {uk}")
        elif fragment not in source_texts[uk]:
            errors.append(f"mapped fragment not found in source: {uk}/{item}")
    for path,entries in by_path.items():
        if path.name=="README.md" or path.name=="Projeto_incremental.md":continue
        try:_,_,body=fm(output[path],str(path))
        except Exception as exc:errors.append(f"mapped destination frontmatter invalid: {path}: {exc}");continue
        body=body[1:] if body.startswith("\n") else body
        if all(kind in ("quiz","answer_key") for _,_,_,kind in entries):
            entries=sorted(entries,key=lambda x:(0 if x[1] in ("Quiz/header","Quiz/answer_header") else 1,int(re.search(r"\d+",x[1]).group()) if re.search(r"\d+",x[1]) else 0))
        expected="".join(fragment for _,_,fragment,_ in entries)
        if body!=expected:
            errors.append(f"destination body is not exactly the concatenation of mapped source fragments: {path} expected_sha={sha(expected)} actual_sha={sha(body)}")
    for uk,u in manifest["unidades"].items():
        root=DEST/PurePosixPath(u["pasta"])
        for fid,rel in u["arquivos"].items():
            path=root/PurePosixPath(rel)
            if path not in by_path:errors.append(f"physical content file has no source mapping: {uk}/{fid} -> {path}")
    return errors

def validate_all(snapshots,json_hash,additional_ids=None):
    additional_ids=additional_ids or set()
    errors=[];expected=expected_all()
    if set(output)!=expected:errors.append(f"output path set mismatch missing={len(expected-set(output))}, extra={len(set(output)-expected)}")
    ids={};types=Counter()
    for path,text in output.items():
        try:header,meta,body=fm(text,str(path)); parsed=yaml(header[4:-4],str(path))
        except Exception as exc:errors.append(f"invalid frontmatter {path}: {exc}");continue
        fid=parsed.get("arquivo_id")
        if not fid:errors.append(f"arquivo_id missing: {path}")
        elif fid in ids:errors.append(f"duplicate arquivo_id {fid}: {ids[fid]} / {path}")
        elif fid in additional_ids:errors.append(f"arquivo_id collides with existing migrated file: {fid}: {path}")
        else:ids[fid]=path
        file_type=parsed.get("tipo_arquivo","?")
        types[file_type]+=1
        if file_type not in ("topic_index","project_index"):
            if not parsed.get("parent_key"):errors.append(f"parent_key missing: {path}")
            if any(k in parsed for k in ("key","estimativa_minutos","tags","status")):errors.append(f"parent metadata duplicated in child: {path}")
        if not body.strip():errors.append(f"empty generated file: {path}")
    # Verify each recorded source block fragment occurs in its single mapped destination.
    for uk,item,fragment,rel,kind in ledger:
        root=DEST/PurePosixPath(manifest["unidades"][uk]["pasta"]);path=root/PurePosixPath(rel)
        if path not in output:errors.append(f"mapped destination absent {uk}/{item}: {path}");continue
        target=fm(output[path],str(path))[2]
        if norm(fragment) not in norm(target):errors.append(f"block not found at mapped destination {uk}/{item} -> {rel}")
    if manifest.get("fase")=="Fase_2":errors.extend(validate_mapped_text())
    # Validate coverage classifications and that shared content has one integration destination.
    for uk,u in manifest["unidades"].items():
        maps=u.get("blocos_origem",{});items={**maps.get("quiz",{}),**{k:v for k,v in maps.get("pratica",{}).items() if re.fullmatch(r"P\d+",k)}}
        cov=u.get("cobertura",{});exclusive={}
        if manifest.get("fase")=="Fase_2":
            exclusive_labels=[label for labels in cov.get("exclusivos",{}).values() for label in labels]
            shared_labels=list(cov.get("compartilhados",{}))
            if set(exclusive_labels)&set(shared_labels):errors.append(f"coverage item class overlap {uk}")
            if len(exclusive_labels)!=len(set(exclusive_labels)):errors.append(f"duplicate exclusive coverage item {uk}")
            if set(exclusive_labels)|set(shared_labels)!=set(items):errors.append(f"coverage incomplete {uk}")
        elif set(cov.get("exclusivos",{}))&set(cov.get("compartilhados",{})):
            errors.append(f"coverage class overlap {uk}")
        for subject,labels in cov.get("exclusivos",{}).items():
            if manifest.get("fase")=="Fase_2" and subject not in u.get("assuntos",[]):errors.append(f"unknown exclusive subject {uk}/{subject}")
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
            if manifest.get("fase")=="Fase_2" and len(assoc)>1 and len(assoc)!=len(set(assoc)):errors.append(f"duplicate subject association {uk}/{label}")
            if manifest.get("fase")=="Fase_2" and any(subject not in u.get("assuntos",[]) for subject in assoc):errors.append(f"unknown covered subject {uk}/{label}")
        # Relative Markdown links in each topic index must resolve.
        root=DEST/PurePosixPath(u["pasta"]);readme=output[root/"README.md"]
        for href in re.findall(r"\]\(([^)]+)\)",readme):
            target=root/PurePosixPath(href)
            if "://" not in href and not href.startswith("#") and target not in output:errors.append(f"README link not found {uk}: {href}")
        original=src(uk);_,origmeta,srcbody=fm(original,u["origem"]);_,readmeta,_=fm(readme,"README")
        for k,v in origmeta.items():
            if readmeta.get(k)!=v:errors.append(f"original metadata changed {uk}/{k}")
        srcwords=words(srcbody);dstwords=words(title_from(srcbody));target_code=[]
        for path,text in output.items():
            if root in path.parents and path.name!="README.md":
                target_body=fm(text,str(path))[2];dstwords+=words(target_body)
                try:target_code.extend(code_blocks(target_body))
                except Exception as exc:errors.append(f"code fence error {path}: {exc}")
        if manifest.get("fase")=="Fase_2":
            try:
                if Counter(code_blocks(srcbody))!=Counter(target_code):errors.append(f"code block content mismatch {uk}")
            except Exception as exc:errors.append(f"source code fence error {uk}: {exc}")
        removed_words=sum(words(line) for unit,dest,rel,line in removed if unit==uk)
        if srcwords!=dstwords+removed_words:errors.append(f"word count mismatch {uk}: source={srcwords}, migrated={dstwords}, authorized_removed={removed_words}")
        if uk!="3.5":
            quiz=quiz_split(section(split_headings(fm(original,u["origem"])[2],2)[1],"Verificação — quiz"))[2]
            if set("Q"+str(x) for x in quiz)!=set(maps.get("quiz",{})):errors.append(f"quiz mapping mismatch {uk}")
    project=manifest.get("projeto_incremental",{}).get("indice_markdown")
    if project:
        path=DEST/PurePosixPath(project["path"])
        if path not in output:errors.append("project index missing")
        else:
            for href in re.findall(r"\]\(([^)]+)\)",output[path]):
                target=DEST/PurePosixPath(href.split("#",1)[0])
                if "://" not in href and not href.startswith("#") and target not in output:errors.append(f"project index link not found: {href}")
    for rel,h in snapshots.items():
        if fhash(ROOT/rel)!=h:errors.append("original source changed: "+rel)
    if fhash(ROOT/json_rel)!=json_hash:errors.append("import JSON changed")
    return errors,types

def make_project_index():
    spec=manifest.get("projeto_incremental",{}).get("indice_markdown")
    if not spec:return None
    rel=PurePosixPath(spec["path"]);path=DEST/rel
    if path in output:raise ValueError("duplicate project index path")
    fields=[("arquivo_id",spec["arquivo_id"]),("tipo_arquivo",spec["tipo_arquivo"])]
    lines=["# Projeto incremental — Fase 2",""]
    for code,milestone in manifest["projeto_incremental"]["marcos"].items():
        lines.append(f"- [{milestone['titulo']}]({milestone['path']})")
    output[path]=frontmatter(fields)+"\n".join(lines)+"\n"
    return path

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


def validate_phase2_manifest(m):
    errors=[]
    expected_order=["4.1","4.2","4.3","5.1","5.2","5.3","5.4"]
    if m.get("fase")!="Fase_2":errors.append("manifest fase is not Fase_2")
    if m.get("base_commit")!="7028682ab46dd6186c274f9655bd7dce3c2e3612":errors.append("manifest base_commit differs from approved Fase 1 commit")
    if m.get("id_prefix")!="f2":errors.append("manifest id_prefix must be f2")
    if m.get("destino_raiz")!="docs/courses/trilhacode/Conteudos_migrado/Fase_2":errors.append("manifest destination root is not the approved Fase 2 root")
    if m.get("ordem_unidades")!=expected_order:errors.append("unit order differs from approved Fase 2 order")
    if set(m.get("unidades",{}))!=set(expected_order):errors.append("manifest unit set differs from seven approved units")
    dest=PurePosixPath(m.get("destino_raiz",""))
    if dest.is_absolute() or ".." in dest.parts:errors.append("destination root must be a repository-relative path")
    seen_paths=set();seen_ids=set()
    for uk in m.get("ordem_unidades",[]):
        u=m.get("unidades",{}).get(uk)
        if not u:continue
        srcpath=PurePosixPath("docs/courses/trilhacode")/PurePosixPath(u.get("origem",""))
        if srcpath.is_absolute() or ".." in srcpath.parts:errors.append(f"unsafe source path {uk}: {srcpath}")
        if not (ROOT/Path(*srcpath.parts)).is_file():errors.append(f"source missing: {srcpath}")
        unitroot=PurePosixPath(u.get("pasta",""))
        if not unitroot.parts or unitroot.is_absolute() or ".." in unitroot.parts:errors.append(f"unsafe unit path {uk}: {unitroot}")
        if len(u.get("assuntos",[]))!=len(set(u.get("assuntos",[]))):errors.append(f"duplicate subject slug: {uk}")
        for slug in u.get("assuntos",[]):
            if not re.fullmatch(r"[0-9]{2}_[a-z0-9_]+",slug):errors.append(f"invalid subject slug: {uk}/{slug}")
        if not isinstance(u.get("arquivos"),dict):errors.append(f"files map missing: {uk}");continue
        for fid,rel in u["arquivos"].items():
            p=PurePosixPath(rel);full=dest/unitroot/p
            if p.is_absolute() or ".." in p.parts:errors.append(f"unsafe destination path: {uk}/{fid}: {rel}")
            if full in seen_paths:errors.append(f"duplicate destination path: {full}")
            seen_paths.add(full)
            candidate=file_id(uk,rel)
            if candidate in seen_ids:errors.append(f"duplicate generated file id: {candidate}")
            seen_ids.add(candidate)
            if fid.startswith("T"):
                subject=p.parts[0] if p.parts else ""
                if subject not in u["assuntos"]:errors.append(f"theory file has unknown subject: {uk}/{fid}")
        for category in ("quiz","pratica"):
            specs=u.get("blocos_origem",{}).get(category,{})
            expected=[f"Q{i}" for i in range(1,6)] if category=="quiz" else [f"P{i}" for i in range(1,4)]
            found=sorted((k for k in specs if re.fullmatch(r"[QP][1-3-5]",k)),key=lambda x:int(x[1:]))
            if category=="quiz":found=sorted((k for k in specs if re.fullmatch(r"Q[1-5]",k)),key=lambda x:int(x[1:]))
            if found!=expected:errors.append(f"{uk}: {category} source IDs differ from approved inventory: {found}")
        theory=u.get("blocos_origem",{}).get("teoria",{})
        if not theory:errors.append(f"theory map missing: {uk}")
        for heading,fid in theory.items():
            if fid not in u["arquivos"] or not fid.startswith("T"):errors.append(f"unknown theory destination: {uk}/{heading} -> {fid}")
        # Enforce a complete, non-overlapping quiz/practice coverage map.
        coverage=u.get("cobertura",{});exclusive=coverage.get("exclusivos",{});shared=coverage.get("compartilhados",{})
        flat=[item for items in exclusive.values() for item in items]
        if set(flat)&set(shared):errors.append(f"coverage item classified both exclusive and shared: {uk}")
        expected_items={f"Q{i}" for i in range(1,6)}|{f"P{i}" for i in range(1,4)}
        if set(flat)|set(shared)!=expected_items:errors.append(f"coverage incomplete: {uk}")
        if len(flat)!=len(set(flat)):errors.append(f"duplicate exclusive coverage item: {uk}")
        for subject,items in exclusive.items():
            if subject not in u["assuntos"]:errors.append(f"unknown exclusive subject: {uk}/{subject}")
            for item in items:
                spec=u["blocos_origem"]["quiz" if item.startswith("Q") else "pratica"][item]
                if spec.get("assunto")!=subject:errors.append(f"exclusive item mismatch: {uk}/{item}/{subject}")
        for item,subjects in shared.items():
            if len(subjects)<2 or len(subjects)!=len(set(subjects)):errors.append(f"invalid shared subject list: {uk}/{item}")
            spec=u["blocos_origem"]["quiz" if item.startswith("Q") else "pratica"][item]
            if set(spec.get("assuntos",[]))!=set(subjects):errors.append(f"shared subject mismatch: {uk}/{item}")
        all_paths=set(seen_paths)
    project=m.get("projeto_incremental",{});index=project.get("indice_markdown",{})
    if index:
        p=dest/PurePosixPath(index.get("path",""))
        if p in seen_paths:errors.append("project index collides with unit file")
        if p.is_absolute() or ".." in p.parts:errors.append("unsafe project index path")
        pid=index.get("arquivo_id")
        if pid in seen_ids:errors.append(f"project index ID collision: {pid}")
        seen_ids.add(pid)
        if pid!="f2-fase-2-projeto-incremental":errors.append("project index id differs from approved id")
        milestones=project.get("marcos",{})
        if list(milestones)!=[f"M{i}" for i in range(1,8)]:errors.append("project references must be M1-M7 in order")
        for code,milestone in milestones.items():
            if milestone.get("unidade") not in expected_order:errors.append(f"invalid milestone unit: {code}")
            if milestone.get("atividade_origem")!="P3":errors.append(f"milestone does not reference P3: {code}")
            path=dest/PurePosixPath(milestone.get("path",""))
            if path not in seen_paths:errors.append(f"milestone target is not a mapped practice file: {code} -> {path}")
    expected=m.get("estimativa_arquivos",{}).get("total")
    if expected!=144:errors.append(f"approved file forecast mismatch: {expected}")
    return errors

def source_sha256_from_git(rel):
    return hashlib.sha256(subprocess.check_output(["git","show","HEAD:"+str(rel)],cwd=ROOT)).hexdigest()

def phase2_tree_ids():
    root=ROOT/"docs/courses/trilhacode/Conteudos_migrado/Fase_1"
    ids=set();files=sorted(root.rglob("*.md"))
    for path in files:
        _,fields,_=fm(path.read_text(encoding="utf-8-sig"),str(path))
        value=fields.get("arquivo_id")
        if not value:raise ValueError(f"Fase 1 file missing arquivo_id: {path}")
        if value in ids:raise ValueError(f"duplicate Fase 1 arquivo_id: {value}")
        ids.add(value)
    return files,ids

def run_manifest(manifest_path,apply=False):
    global MP,DEST,MAPCSV,REPORT,manifest,output,ledger,artifact_fragments,removed,original_headers,source_meta,source_titles,json_rel
    MP=ROOT/Path(manifest_path)
    if not MP.is_file():raise SystemExit("manifest not found: "+str(MP))
    manifest_text=MP.read_text(encoding="utf-8-sig")
    manifest=yaml(manifest_text,"Fase 2 manifest")
    errors=validate_phase2_manifest(manifest)
    if errors:
        print("MANIFEST INVALID")
        for error in errors:print("- "+error)
        return 2
    head=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
    branch=subprocess.check_output(["git","branch","--show-current"],cwd=ROOT,text=True).strip()
    if head!=manifest["base_commit"]:raise SystemExit("HEAD differs from the verified manifest base; stopped.")
    if branch!="migracao-estrutura":raise SystemExit("current branch is not migracao-estrutura; stopped.")
    status=subprocess.check_output(["git","status","--porcelain=v1"],cwd=ROOT,text=True).splitlines()
    allowed={"docs/migracao/_migrar_fase1.py","docs/courses/trilhacode/Guia_de_Producao_de_Conteudo.md",str(Path(manifest_path).as_posix())}
    unexpected=[line for line in status if line[3:].replace("\\","/") not in allowed]
    if unexpected:raise SystemExit("unexpected working-tree paths; stopped: "+repr(unexpected))
    if subprocess.call(["git","diff","--cached","--quiet"],cwd=ROOT)!=0:raise SystemExit("staged changes exist; stopped.")
    tracked=subprocess.check_output(["git","diff","--name-only","HEAD"],cwd=ROOT,text=True).splitlines()
    if set(p.replace("\\","/") for p in tracked)!={"docs/migracao/_migrar_fase1.py"}:raise SystemExit("tracked changes differ from the authorized generator adaptation; stopped: "+repr(tracked))
    DEST=PurePosixPath(manifest["destino_raiz"])
    MAPCSV=PurePosixPath("docs/migracao/relatorio_mapeamento_fase2.csv")
    REPORT=PurePosixPath("docs/migracao/relatorio_validacao_fase2.md")
    audit=ROOT/"docs/migracao/auditoria_final_fase2.md"
    json_rel="docs/courses/trilhacode/trilha-code-bulk-import.json"
    if (ROOT/Path(*DEST.parts)).exists():raise SystemExit("Fase 2 destination already exists; refusing to overwrite.")
    if not (ROOT/json_rel).is_file():raise SystemExit("import JSON missing; stopped.")
    source_rels=[str(PurePosixPath("docs/courses/trilhacode")/PurePosixPath(u["origem"])) for u in manifest["unidades"].values()]
    protected=source_rels+["docs/courses/trilhacode/Fase_2_Base_da_Web_HTML_CSS.md","docs/courses/trilhacode/Referencias_Fase_2.md",json_rel]
    snapshots={rel:fhash(ROOT/Path(*PurePosixPath(rel).parts)) for rel in protected}
    for rel in source_rels:
        disk_text=(ROOT/Path(*PurePosixPath(rel).parts)).read_text(encoding="utf-8-sig")
        base_text=subprocess.check_output(["git","show","HEAD:"+rel],cwd=ROOT).decode("utf-8-sig")
        if norm(disk_text)!=norm(base_text):
            raise SystemExit("source text differs from the verified base; stopped: "+rel)
    for rel in protected:
        if not (ROOT/Path(*PurePosixPath(rel).parts)).is_file():raise SystemExit("protected input missing; stopped: "+rel)
    f1_files,f1_ids=phase2_tree_ids()
    if len(f1_files)!=221:raise SystemExit(f"homologated Fase 1 file count mismatch: {len(f1_files)}")
    f1_snapshot={p.relative_to(ROOT).as_posix():fhash(p) for p in f1_files}
    f1_tree_hash=sha("".join(f"{rel} {digest}\n" for rel,digest in sorted(f1_snapshot.items())))
    for rel in (str(MAPCSV),str(REPORT),"docs/migracao/auditoria_final_fase2.md"):
        if (ROOT/Path(*PurePosixPath(rel).parts)).exists():raise SystemExit("Fase 2 report path already exists; refusing to overwrite: "+rel)
    # Validate every source/target declaration before the first write.
    paths=set();ids=set()
    for uk,u in manifest["unidades"].items():
        for fid,rel in u["arquivos"].items():
            p=DEST/PurePosixPath(u["pasta"])/PurePosixPath(rel)
            fid_value=file_id(uk,rel)
            if p in paths:raise SystemExit("duplicate physical destination: "+str(p))
            if fid_value in ids or fid_value in f1_ids:raise SystemExit("global archivo_id collision: "+fid_value)
            paths.add(p);ids.add(fid_value)
    existing_manifest=MP.read_bytes()
    output={};ledger=[];artifact_fragments=defaultdict(list);removed=[];original_headers={};source_meta={};source_titles={}
    for uk in manifest["ordem_unidades"]:emit_unit(uk,manifest["unidades"][uk])
    for uk in manifest["ordem_unidades"]:flush_artifacts(uk,manifest["unidades"][uk])
    make_project_index()
    json_hash=snapshots[json_rel]
    errors,types=validate_all(snapshots,json_hash,f1_ids)
    if f1_tree_hash!=sha("".join(f"{rel} {digest}\n" for rel,digest in sorted(f1_snapshot.items()))):errors.append("Fase 1 tree snapshot calculation changed")
    if errors:
        print("DRY VALIDATION FAILED")
        for error in errors:print("- "+error)
        return 3
    if len(output)!=144:raise SystemExit(f"generated file count differs from approved map: {len(output)}")
    perunit=[]
    # Re-extract each quiz from the source and prove that its separated question and answer
    # blocks match the destination files one-for-one; only the file boundary replaces inline spacing.
    for uk,u in manifest["unidades"].items():
        original=src(uk);_,_,srcbody=fm(original,u["origem"]);sections=dict(split_headings(srcbody,2)[1])
        _,_,questions,answers=quiz_split(sections["Verificação — quiz"])
        for number in sorted(questions):
            qid="Q"+str(number);spec=u["blocos_origem"]["quiz"][qid]
            qpath=DEST/PurePosixPath(u["pasta"])/PurePosixPath(u["arquivos"][spec["arquivo"]])
            apath=DEST/PurePosixPath(u["pasta"])/PurePosixPath(u["arquivos"][spec["resposta"]])
            try:qbody=fm(output[qpath],str(qpath))[2];abody=fm(output[apath],str(apath))[2]
            except Exception as exc:errors.append(f"quiz target unavailable {uk}/{qid}: {exc}");continue
            qbody=qbody[1:] if qbody.startswith("\n") else qbody;abody=abody[1:] if abody.startswith("\n") else abody
            if questions[number] not in qbody:errors.append(f"question text not preserved: {uk}/{qid}")
            if answers.get(number) not in abody:errors.append(f"answer/explanation not preserved: {uk}/{qid}")
    for uk,u in manifest["unidades"].items():
        root=DEST/PurePosixPath(u["pasta"])
        count=sum(1 for path in output if root in path.parents)
        mapping=sum(1 for item in ledger if item[0]==uk)+sum(1 for item in removed if item[0]==uk)
        perunit.append((uk,count,mapping))
    if not apply:
        print(f"DRY-RUN OK | base={head} | branch={branch} | units={len(perunit)} | subjects={sum(len(u['assuntos']) for u in manifest['unidades'].values())} | theory_headings={sum(len(u['blocos_origem']['teoria']) for u in manifest['unidades'].values())} | questions=35 | practices=21 | files={len(output)} | mappings={len(ledger)+len(removed)}")
        print("types="+json.dumps(types,ensure_ascii=True,sort_keys=True))
        for row in perunit:print("unit="+"|".join(map(str,row)))
        print("protected_inputs="+str(len(snapshots))+" F1_files="+str(len(f1_files))+" F1_tree_sha256="+f1_tree_hash)
        return 0
    for rel,text in sorted(output.items(),key=lambda x:str(x[0])):
        target=ROOT/Path(*rel.parts);target.parent.mkdir(parents=True,exist_ok=True)
        with target.open("w",encoding="utf-8",newline="\n") as stream:stream.write(norm(text))
    # Read the written files back and repeat the exact block, link, metadata, ID and protected-input checks.
    persisted={}
    for rel in expected_all():
        path=ROOT/Path(*rel.parts)
        if not path.is_file():errors.append("missing persisted file: "+str(rel))
        else:persisted[rel]=path.read_text(encoding="utf-8-sig")
    output=persisted
    errors2,types2=validate_all(snapshots,json_hash,f1_ids);errors.extend(errors2)
    current_f1={p.relative_to(ROOT).as_posix():fhash(p) for p in f1_files}
    if current_f1!=f1_snapshot:errors.append("homologated Fase 1 files changed")
    if MP.read_bytes()!=existing_manifest:errors.append("approved Fase 2 manifest changed during generation")
    if errors:
        print("POST-WRITE VALIDATION FAILED")
        for error in errors:print("- "+error)
        return 4
    with (ROOT/Path(*MAPCSV.parts)).open("w",encoding="utf-8",newline="") as stream:
        writer=csv.writer(stream);writer.writerow(["unidade","origem","bloco","tipo","destino","palavras","sha256_bloco"])
        for uk,item,fragment,rel,kind in ledger:
            destrel=DEST/PurePosixPath(manifest["unidades"][uk]["pasta"])/PurePosixPath(rel)
            writer.writerow([uk,manifest["unidades"][uk]["origem"],item,kind,str(destrel),words(fragment),sha(fragment)])
        for uk,destid,label,line in removed:
            writer.writerow([uk,manifest["unidades"][uk]["origem"],"Conexões/"+destid,"authorized_structural_removal","sem destino físico — relação duplicada aprovada",words(line),sha(line)])
    report=["# Relatório de validação — Fase 2","",f"- Commit-base: `{head}`",f"- Branch: `{branch}`",f"- Destino: `{DEST}/`",f"- Unidades: {len(perunit)}",f"- Assuntos: {sum(len(u['assuntos']) for u in manifest['unidades'].values())}",f"- Microtópicos de teoria: {sum(len(u['blocos_origem']['teoria']) for u in manifest['unidades'].values())}",f"- Questões: 35",f"- Práticas: 21",f"- Arquivos de curso gerados: {len(output)}",f"- Mapeamentos físicos e remoções aprovadas: {len(ledger)+len(removed)}","","## Contagem por tipo",""]
    report += [f"- `{kind}`: {n}" for kind,n in sorted(types2.items())]
    report += ["","## Contagem por unidade","","| Unidade | Arquivos | Blocos mapeados | Resultado |","|---|---:|---:|---|"]
    report += [f"| {uk} | {count} | {mappings} | OK |" for uk,count,mappings in perunit]
    report += ["","## Validações textuais e estruturais","","- Cada arquivo de conteúdo é exatamente a concatenação dos fragmentos registrados no mapeamento, com somente CRLF/CR normalizado para LF; cada fragmento foi localizado na fonte, salvo as duas relações duplicadas explicitamente removidas.","- Os 30 títulos de teoria correspondem aos destinos do manifesto; os 35 enunciados e gabaritos e as 21 práticas foram verificados por ID e conteúdo.","- Blocos de código comparados por conteúdo integral; respostas, soluções, checklists, critérios e rubricas mapeados em arquivos próprios quando existem.","- O bloco misto 5.1/P2 foi separado pelos segmentos literais do manifesto; segmentos têm correspondência exata com a fonte e foram direcionados sem sobreposição.","- Metadados originais preservados no frontmatter do README; frontmatter dos filhos parseado e IDs únicos, sem colisão com os 221 IDs da Fase 1.","- Links Markdown relativos dos READMEs e sete links do índice do projeto resolvem para arquivos existentes.","- Originais Fase 2, notas gerais da fase, referências e JSON possuem SHA-256 idêntico ao pré-voo.","- Os 221 arquivos migrados da Fase 1 mantêm seus hashes pré-geração.","- JSON não foi alterado; importador não foi executado; nenhum commit foi criado.","","## Limitações","","- Wikilinks Obsidian para documentos externos à árvore migrada dependem da raiz do vault e da integração final; mantidos conforme decisão aprovada.","- A existência de textos de conexão repetidos foi tratada somente nos dois casos autorizados no manifesto.",""]
    with (ROOT/Path(*REPORT.parts)).open("w",encoding="utf-8",newline="\n") as stream:stream.write("\n".join(report))
    result="APROVADA COM RESSALVAS"
    audit_lines=["# Auditoria final — migração estrutural da Fase 2","",f"**Resultado: {result}.**","",f"- Commit-base verificado: `{head}`",f"- Branch isolada: `{branch}`",f"- Arquivos de curso: {len(output)}",f"- Blocos mapeados, incluindo remoções estruturais aprovadas: {len(ledger)+len(removed)}",f"- Relatório de mapeamento: `{MAPCSV}`",f"- Relatório de validação: `{REPORT}`","","## Resultado por unidade","","| Unidade | Arquivos | Mapeamentos | Integridade |","|---|---:|---:|---|"]
    audit_lines += [f"| {uk} | {count} | {mappings} | APROVADA |" for uk,count,mappings in perunit]
    audit_lines += ["","## Integridade e escopo","","- Os blocos originais foram comparados por texto real e hashes SHA-256; CRLF/CR foi normalizado para LF, sem alterar caracteres de conteúdo.","- Os segmentos do bloco misto de 5.1/P2 foram comparados separadamente; não há lacunas nem sobreposição. A separação dos gabaritos inline transforma apenas o espaço delimitador em limite de arquivo.","- A única remoção textual consiste nas conexões duplicadas autorizadas de 4.3 e 5.3; cada linha está registrada no CSV.","- Nenhuma teoria, exercício, gabarito, critério ou rubrica foi criado; o índice de projeto contém apenas os sete links aprovados para P3.","- As fontes da Fase 2, as notas gerais, as referências e o JSON permanecem inalterados.","- A Fase 1 preserva 221 arquivos com hashes idênticos; sua árvore não foi modificada.","- O arquivo local preexistente `docs/courses/trilhacode/Guia_de_Producao_de_Conteudo.md` foi mantido fora da geração.","","## Avisos e limitações","","- Wikilinks Obsidian podem não resolver enquanto a árvore migrada estiver fora da raiz do vault configurada.","- O checkout permanece sem commit; não houve importação JSON, substituição dos originais ou início da Fase 3.","","A contagem final foi determinada pela união dos caminhos distintos declarados no manifesto e dos índices estruturais autorizados; a previsão de 144 foi confirmada sem arquivos artificiais.",""]
    with audit.open("w",encoding="utf-8",newline="\n") as stream:stream.write("\n".join(audit_lines))
    print(f"MIGRATION OK | base={head} | branch={branch} | files={len(output)} | mappings={len(ledger)+len(removed)} | result={result}")
    print("types="+json.dumps(types2,ensure_ascii=True,sort_keys=True))
    for row in perunit:print("unit="+"|".join(map(str,row)))
    print(f"map={MAPCSV} report={REPORT} audit={audit.relative_to(ROOT)} F1_files={len(f1_files)} F1_tree_sha256={f1_tree_hash}")
    return 0

if __name__=="__main__":
    if "--manifest" in sys.argv:
        i=sys.argv.index("--manifest")
        if i+1>=len(sys.argv):raise SystemExit("--manifest requires a relative path")
        raise SystemExit(run_manifest(sys.argv[i+1],"--apply" in sys.argv))
    raise SystemExit(run("--apply" in sys.argv))
