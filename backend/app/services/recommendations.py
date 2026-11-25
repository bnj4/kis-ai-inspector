import re
from collections import Counter
from app.services.identify import identify
from app.core.config import settings
import httpx

KINDS={'model':'models','space':'spaces','dataset':'datasets'}
def canonical(url):
    kind, owner, name=identify(url)
    if not all(re.fullmatch(r'[A-Za-z0-9_.-]+', x) and x not in {'.','..'} for x in (owner,name)):
        raise ValueError('Identificador inválido')
    prefix='' if kind=='model' else KINDS.get(kind,'')+'/'
    return f'https://github.com/{owner}/{name}' if kind=='github' else f'https://huggingface.co/{prefix}{owner}/{name}'

def features(report):
    raw=report.get('raw_data') or {}; r=raw.get('repository',raw)
    tags=[x for x in (r.get('topics') or r.get('tags') or []) if isinstance(x,str) and ':' not in x]
    return set(tags+[x for x in [r.get('pipeline_tag'),r.get('language'),r.get('library_name')] if isinstance(x,str)])

def item(url, name, reason, source, count=None):
    return dict(url=canonical(url),name=name,reason=reason,source=source,count=count)

async def external(report):
    kind=report['resource_type']; tags=features(report); raw=report.get('raw_data') or {}; r=raw.get('repository',raw)
    headers={}; params={}; term=None
    if kind=='github':
        topics=r.get('topics') or []; language=r.get('language'); term=next((x for x in topics if re.fullmatch(r'[\w-]+',x)),None)
        query=f'topic:{term}' if term else (f'language:{language}' if language else 'stars:>1000')
        params={'q':query,'sort':'stars','order':'desc','per_page':15}; endpoint='https://api.github.com/search/repositories'
        if settings.github_token: headers['Authorization']='Bearer '+settings.github_token
        related=bool(term or language); reason=f'Tema: {term}' if term else f'Lenguaje: {language}' if language else 'Popularidad en GitHub'
    else:
        endpoint='https://huggingface.co/api/'+KINDS[kind]; params={'limit':20,'sort':'likes','direction':-1}
        term=r.get('pipeline_tag') or next((x for x in sorted(tags) if x in {'text-to-image','image-to-image','image-text-to-text','text-generation','text-classification','automatic-speech-recognition','image-classification','text-to-speech','object-detection','translation','feature-extraction'}),None)
        if not term:
            term=next((x for x in sorted(tags) if x in {'gradio','streamlit','image-generation','computer-vision','nlp','text-to-image','image-editing','diffusers'}),None)
        if term: params['filter']=term
        related=bool(term); reason=f'Etiqueta: {term}' if term else 'Popularidad en Hugging Face'
        if settings.hf_token: headers['Authorization']='Bearer '+settings.hf_token
    async with httpx.AsyncClient(timeout=12,follow_redirects=False) as c:
        response=await c.get(endpoint,params=params,headers=headers); response.raise_for_status(); data=response.json()
    rows=data.get('items',[]) if kind=='github' else data
    out=[]; seen={canonical(report['url']).lower()}
    for row in rows:
        if row.get('private'): continue
        name=row.get('full_name') if kind=='github' else row.get('id') or row.get('modelId')
        if not isinstance(name,str) or name.count('/')!=1: continue
        prefix='https://github.com/' if kind=='github' else 'https://huggingface.co/'+('' if kind=='model' else KINDS[kind]+'/')
        try: entry=item(prefix+name,name,reason,'external')
        except ValueError: continue
        key=entry['url'].lower()
        if key in seen: continue
        seen.add(key); out.append(entry)
    return (out[:6],[]) if related else ([],out[:6])

def historical(report, events, reports):
    current=canonical(report['url']).lower(); tags=features(report); counts=Counter(); names={}
    for url in events:
        try: key=canonical(url).lower()
        except ValueError: continue
        if key!=current: counts[key]+=1; names[key]=canonical(url)
    related=[]
    for key,count in counts.items():
        other=reports.get(key)
        if not other or other.get('resource_type')!=report['resource_type']: continue
        overlap=tags & features(other)
        if not overlap: continue
        related.append((count,len(overlap),key,overlap))
    related.sort(key=lambda x:(-x[0],-x[1],x[2]))
    return [item(names[key],'/'.join(identify(names[key])[1:]),'Coincidencia: '+', '.join(sorted(overlap)[:3]),'history',count) for count,_,key,overlap in related[:6]]
