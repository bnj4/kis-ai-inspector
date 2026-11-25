import base64, json
from datetime import datetime, timezone
from app.connectors.github import GitHubConnector
from app.connectors.huggingface import HuggingFaceConnector
from app.services.identify import identify
from app.services.ai import generate, AIProviderError

async def analyze(url: str):
    kind, owner, name = identify(url)
    if kind == 'github': raw = await GitHubConnector().collect(owner, name)
    else: raw = await HuggingFaceConnector().collect(kind, owner, name)
    evidence = []
    def add(src, title, detail, link=None): evidence.append({"id":f"E{len(evidence)+1}","source":src,"title":title,"detail":str(detail)[:1800],"url":link,"kind":"documental"})
    if kind == 'github':
        r = raw.get('repository', {})
        add('GitHub API','Metadatos', {k:r.get(k) for k in ['full_name','description','language','license','stargazers_count','forks_count','open_issues_count','created_at','updated_at','pushed_at','archived']},url)
        add('GitHub API','Lenguajes',raw.get('languages',{}),url)
        add('GitHub API','Archivos raíz',[x.get('name') for x in raw.get('contents',[]) if isinstance(x,dict)],url)
        rd = raw.get('readme',{})
        if isinstance(rd,dict) and rd.get('content'):
            try: readme=base64.b64decode(rd['content']).decode('utf-8','replace')[:12000]
            except Exception: readme='README disponible, no se pudo decodificar'
            add('GitHub README','Documentación principal',readme,url)
        add('GitHub API','Releases', [{k:x.get(k) for k in ['tag_name','name','published_at','draft','prerelease']} for x in raw.get('releases',[]) if isinstance(x,dict)],url)
        add('GitHub API','Issues/PR recientes', [{k:x.get(k) for k in ['title','state','created_at','updated_at','comments','html_url','pull_request']} for x in raw.get('issues',[]) if isinstance(x,dict)],url)
        identity={"name":r.get('full_name',name),"author":owner,"type":"Repositorio GitHub","description":r.get('description'),"url":url,"analyzed_at":datetime.now(timezone.utc).isoformat()}
    else:
        add('Hugging Face Hub API','Ficha del recurso',{k:raw.get(k) for k in ['id','pipeline_tag','tags','library_name','downloads','likes','lastModified','private','gated','cardData','config','runtime','siblings']},url)
        if raw.get('readme'): add('Hugging Face README','Documentación',raw['readme'][:12000],url)
        identity={"name":raw.get('id',f'{owner}/{name}'),"author":owner,"type":{"model":"Modelo Hugging Face","space":"Hugging Face Space","dataset":"Dataset Hugging Face"}[kind],"description":(raw.get('cardData') or {}).get('description'),"url":url,"analyzed_at":datetime.now(timezone.utc).isoformat()}
    prompt = "Analiza este recurso. Devuelve JSON siguiendo el esquema del sistema. No asumas que los datos ausentes son negativos.\nRECURSO: "+json.dumps(identity,ensure_ascii=False)+"\nEVIDENCIAS:\n"+json.dumps(evidence,ensure_ascii=False)[:26000]
    content, provider = await generate(prompt)
    if content:
        try: result=json.loads(content)
        except Exception: result={}
    else: result={}
    if provider != "none" and not isinstance(result, dict):
        raise AIProviderError("El proveedor devolvió un formato de informe inválido.")
    if provider != "none" and not result:
        raise AIProviderError("El proveedor no devolvió un informe JSON válido.")
    if not result:
        result={"summary":"Se recopilaron metadatos y evidencias. No se generó interpretación automatizada porque no hay un proveedor de IA disponible.","functionality":[],"technical":{"metadata_only":True},"strengths":[],"weaknesses":["No se pudo realizar una interpretación con IA; se requiere revisar las evidencias manualmente."],"use_cases":[],"categories":[],"requirements":[],"security":["La inspección no ejecutó código externo.","La revisión de seguridad es parcial y no sustituye una auditoría."],"conclusion":"Resultado documental sin evaluación automatizada.","confidence":"limitada"}
    return {"url":url,"resource_type":kind,"identity":identity,"summary":result.get('summary',''),"functionality":result.get('functionality',[]),"technical":result.get('technical',{}),"strengths":result.get('strengths',[]),"weaknesses":result.get('weaknesses',[]),"use_cases":result.get('use_cases',[]),"categories":result.get('categories',[]),"requirements":result.get('requirements',[]),"security":result.get('security',[]),"conclusion":result.get('conclusion',''),"evidence":evidence,"confidence":result.get('confidence','limitada'),"provider":provider,"created_at":identity['analyzed_at'],"raw_data":raw}
