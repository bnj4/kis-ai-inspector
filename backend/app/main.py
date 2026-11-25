from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import os, secrets
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db
from app.api.routes import router

app=FastAPI(title=settings.app_name,version='3.0.0',description='Inspección basada en evidencias de recursos GitHub y Hugging Face')
app.add_middleware(CORSMiddleware,allow_origins=[x.strip() for x in settings.cors_origins.split(',')],allow_credentials=True,allow_methods=['*'],allow_headers=['*'])
@app.middleware('http')
async def internal_access(request: Request, call_next):
    if request.url.path == '/api/health':
        return await call_next(request)
    expected = settings.internal_api_token
    if os.getenv('RAILWAY_PROJECT_ID') and not expected:
        return JSONResponse({'detail':'Falta configurar INTERNAL_API_TOKEN.'},status_code=503)
    if expected and not secrets.compare_digest(request.headers.get('x-kis-internal-token','').encode(),expected.encode()):
        return JSONResponse({'detail':'Acceso no autorizado.'},status_code=401)
    return await call_next(request)
app.include_router(router,prefix='/api')
@app.on_event('startup')
async def startup(): await init_db()
