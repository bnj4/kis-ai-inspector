# KIS AI Inspector V3 · Cloud

Versión derivada de V2: conserva análisis, informes, historial, recomendaciones externas y de consultas reales, con OpenAI y configuración para Railway. Consulta [tutorial de despliegue](docs/RAILWAY.md).

## Local (Windows)
Requisitos: Python 3.12, Node.js 22+, Visual Studio Code. Abre la carpeta raíz. Terminal 1:

```powershell
cd backend
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

Si se bloquean scripts: `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`, y vuelve a activar el entorno. Edita `backend/.env`: `AI_PROVIDER=openai`, `OPENAI_API_KEY=tu_clave`, `OPENAI_MODEL=gpt-4o-mini`. Mantén `INTERNAL_API_TOKEN` vacío en local. También puedes usar `AI_PROVIDER=ollama` o `none`. No publiques el archivo .env.

```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Terminal 2 desde raíz:

```powershell
cd frontend
npm install
npm run dev
```

Abre http://localhost:3000. El proxy de Next.js conecta automáticamente con el backend en http://127.0.0.1:8000. API docs local: http://127.0.0.1:8000/docs. Para futuras sesiones, no recrees venv ni reinstales dependencias si no cambian. Conserva la V2 como respaldo.

## Nube
Dos servicios Docker con raíz independiente y un volumen SQLite. Solo frontend tiene dominio público; el backend se comunica por red privada y secreto interno. El acceso web usa una contraseña compartida. Sigue [docs/RAILWAY.md](docs/RAILWAY.md) para configurar. No es un sistema multiusuario con cuentas y permisos separados. Usa una réplica del backend.

## Alcance
Los conectores recogen metadatos y documentación de recursos públicos, sin ejecutar código externo. Las recomendaciones se basan en etiquetas/temas/lenguajes y frecuencia de consultas, no en similitud semántica mediante IA. No se inventa actividad. El historial cuenta consultas, no personas únicas. El análisis no equivale a una auditoría certificada. Consulta docs/FEATURE_MATRIX.md para límites originales y docs/RAILWAY.md para validación pendiente de V3.
