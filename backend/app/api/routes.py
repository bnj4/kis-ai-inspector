from fastapi import APIRouter, HTTPException
from sqlalchemy import select, func
from datetime import datetime, timezone
import asyncio
from app.core.config import settings
from app.models.schemas import AnalyzeRequest
from app.services.analyzer import analyze
from app.core.database import Session, Analysis, SearchEvent, AnalysisAttempt
from app.services.ai import ollama_status, AIProviderError
import json, httpx
from app.services.recommendations import canonical, external, historical

router=APIRouter()
analysis_lock=asyncio.Lock()

async def reserve_attempt(db):
    limit=settings.daily_analysis_limit
    if limit <= 0: return
    day=datetime.now(timezone.utc).date().isoformat()
    count=await db.scalar(select(func.count(AnalysisAttempt.id)).where(AnalysisAttempt.day==day))
    if count >= limit:
        raise HTTPException(429, "Se alcanzó el límite diario de análisis nuevos. Los informes guardados siguen disponibles.")
    db.add(AnalysisAttempt(day=day)); await db.commit()

@router.post('/analyze')
async def create_analysis(req: AnalyzeRequest):
    from app.core.security import validate_resource_url
    try:
        url=canonical(validate_resource_url(str(req.url)))
        async with analysis_lock:
            async with Session() as db:
                if not req.force_refresh:
                    old=await db.scalar(select(Analysis).where(Analysis.url==url).order_by(Analysis.id.desc()))
                    if old:
                        data=json.loads(old.report_json)
                        # A previous no-AI or Ollama report does not prevent a new OpenAI analysis.
                        if settings.ai_provider.lower() != 'openai' or data.get('provider') == 'openai':
                            db.add(SearchEvent(url=url)); await db.commit()
                            data['id']=old.id; return data
                await reserve_attempt(db)
            report=await analyze(url)
            async with Session() as db:
                row=Analysis(url=url,resource_type=report['resource_type'],report_json=json.dumps(report,ensure_ascii=False)); db.add(row); db.add(SearchEvent(url=url)); await db.commit(); await db.refresh(row)
                report['id']=row.id
            return report
    except HTTPException: raise
    except AIProviderError as e: raise HTTPException(502,str(e))
    except ValueError as e: raise HTTPException(400,str(e))
    except httpx.HTTPStatusError as e: raise HTTPException(502,f"El proveedor externo respondió {e.response.status_code}.")
    except httpx.RequestError: raise HTTPException(504,"No se pudo conectar con el proveedor externo.")
    except Exception: raise HTTPException(500,"No se pudo completar el análisis. Revisa los registros del servidor.")

@router.get('/history')
async def history():
    async with Session() as db:
        rows=(await db.scalars(select(Analysis).order_by(Analysis.id.desc()).limit(100))).all()
        return [{"id":x.id,"url":x.url,"resource_type":x.resource_type,"created_at":x.created_at.isoformat()} for x in rows]

@router.get('/history/{analysis_id}')
async def get_history(analysis_id:int):
    async with Session() as db:
        row=await db.get(Analysis,analysis_id)
        if not row: raise HTTPException(404,'Análisis no encontrado')
        data=json.loads(row.report_json); data['id']=row.id; return data

@router.delete('/history/{analysis_id}')
async def delete_history(analysis_id:int):
    async with Session() as db:
        row=await db.get(Analysis,analysis_id)
        if not row: raise HTTPException(404,'Análisis no encontrado')
        await db.delete(row); await db.commit(); return {"deleted":True}

@router.get('/providers')
async def providers():
    ok, models=await ollama_status() if settings.ai_provider.lower() in {"auto","ollama"} else (False,[])
    return {"ollama":{"available":ok,"model":models},"openai":{"configured":bool(settings.openai_api_key)}}

@router.get('/health')
async def health(): return {"status":"ok"}

@router.get('/recommendations/{analysis_id}')
async def recommendations(analysis_id:int):
    async with Session() as db:
        row=await db.get(Analysis,analysis_id)
        if not row: raise HTTPException(404,'Análisis no encontrado')
        report=json.loads(row.report_json)
        events=(await db.scalars(select(SearchEvent.url).order_by(SearchEvent.id.desc()).limit(5000))).all()
        rows=(await db.scalars(select(Analysis).order_by(Analysis.id.desc()).limit(500))).all()
        reports={}
        for x in rows:
            try: reports.setdefault(canonical(x.url).lower(),json.loads(x.report_json))
            except ValueError: continue
    history=historical(report,events,reports)
    try: similar,popular=await external(report); warning=None
    except (httpx.HTTPError,ValueError,KeyError,TypeError): similar,popular=[],[]; warning='No se pudieron consultar las recomendaciones externas.'
    return {'similar':similar,'history':history,'popular':popular,'warning':warning}
