# KIS AI Inspector V3 — OpenAI + Railway

## Antes de comenzar

Necesitas una cuenta en https://github.com, una cuenta en https://railway.com, Git (https://git-scm.com/download/win), Node.js 22 o superior si quieres probar en tu PC, y una clave API de OpenAI con saldo/acceso al modelo: https://platform.openai.com/api-keys. No compartas la clave. La suscripción de ChatGPT y la facturación de API son distintas.

## 1. Subir el proyecto a GitHub

Descomprime el ZIP, abre en VS Code la carpeta que contiene backend y frontend. Crea un repositorio **privado y vacío** en GitHub (sin README inicial). En la terminal de la raíz, usa:

```powershell
git init
git add .
git status
git commit -m "KIS AI Inspector V3 Cloud"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/TU_REPOSITORIO.git
git push -u origin main
```

Comprueba antes del commit que no aparezcan `.env`, `.env.local`, bases `.db`, claves, `venv`, `node_modules`. El ZIP incluye `.gitignore`. Si Git pide nombre y correo, configúralos con `git config --global user.name` y `git config --global user.email`. No copies los secretos de la V2 al repositorio.

## 2. Railway: crear backend

Crea un proyecto nuevo (entorno nuevo, con red privada IPv4). Despliega desde el repositorio GitHub. Nombra el servicio exactamente `backend`. En Settings, establece Root Directory `/backend`. Railway detectará el Dockerfile. Deja Build/Start Command sin sobrescribir. En Variables agrega:

```dotenv
PORT=8000
AI_PROVIDER=openai
OPENAI_API_KEY=PEGA_TU_CLAVE_REAL_AQUI
OPENAI_MODEL=gpt-4o-mini
OPENAI_MAX_COMPLETION_TOKENS=3000
DATABASE_URL=sqlite+aiosqlite:////data/kis_inspector.db
DAILY_ANALYSIS_LIMIT=30
INTERNAL_API_TOKEN=GENERA_UN_SECRETO_ALEATORIO_LARGO
```

Genera el secreto en PowerShell si tienes Python: `py -3.12 -c "import secrets; print(secrets.token_urlsafe(32))"`. Este secreto no es la clave OpenAI. No lo guardes en GitHub. Añade un volumen al backend con ruta `/data` (clic derecho sobre servicio → Attach Volume, o Add Volume). No generes dominio público para backend. Configura Healthcheck Path `/api/health`. Despliega. Mantén **una sola réplica**. Si desplegaste antes del volumen, repite el despliegue después de adjuntarlo. Esperado en logs: Uvicorn en 0.0.0.0:8000, Application startup complete. La base se crea automáticamente en el volumen.

## 3. Railway: crear frontend

En el mismo proyecto y entorno, agrega otro servicio desde el mismo repositorio. Nómbralo `frontend` y establece Root Directory `/frontend`. Deja que el Dockerfile construya y arranque. En Variables:

```dotenv
PORT=3000
BACKEND_URL=http://${{backend.RAILWAY_PRIVATE_DOMAIN}}:8000
INTERNAL_API_TOKEN=${{backend.INTERNAL_API_TOKEN}}
APP_USERNAME=kis
APP_PASSWORD=ELIGE_UNA_CONTRASENA_LARGA_Y_UNICA
```

El nombre `backend` en las referencias debe coincidir exactamente con el nombre del servicio. Para `APP_PASSWORD` elige al menos 20 caracteres aleatorios. No uses la clave OpenAI. Railway resolverá las referencias. En Settings → Networking → Public Networking → Generate Domain, genera una dirección HTTPS para frontend. Configura Healthcheck Path `/healthz`. Despliega. Esperado: Next.js Ready. Abre el dominio HTTPS y el navegador pedirá el usuario y la contraseña. **No configures NEXT_PUBLIC_API_URL ni expongas la API por separado**: la web llama al proxy del mismo dominio y este al backend privado. No es necesario cambiar CORS.

## 4. Comprobar

1. Entra con las credenciales compartidas. Prueba la ruta del frontend `/api/health` (debe responder `{"status":"ok"}`).
2. En Configuración, OpenAI debe aparecer configurado. Este indicador solo comprueba que hay una clave; la prueba real es generar un informe.
3. Analiza un repositorio público nuevo, por ejemplo https://github.com/ollama/ollama. Espera a que termine y comprueba `IA: openai`. Verifica recomendaciones y analiza una de ellas.
4. Repite la misma URL; si ya existe informe OpenAI, se reutiliza. Comprueba historial, vuelve a desplegar backend y verifica que el historial siga presente.
5. Si deseas verificar acceso, abre una ventana privada: sin credenciales debe pedirlas antes de mostrar informes o ejecutar consultas.

## 5. Costos y problemas comunes

- El límite `DAILY_ANALYSIS_LIMIT=30` cuenta intentos de análisis nuevos por día UTC, incluso fallidos. El caché no consume un intento. Puedes bajar a 10; `0` desactiva el límite. No equivale a un límite de dinero. El límite solo está diseñado para una réplica del backend.
- OpenAI API: controla saldo y límites en https://platform.openai.com/settings/organization/billing/overview y uso en https://platform.openai.com/usage. Configura un límite de gasto efectivo donde esté disponible; no confíes solo en alertas. Railway también factura según su plan/consumo: https://railway.com/pricing.
- Error de cuota/saldo: revisa Billing y Limits de OpenAI. Crear una clave no añade saldo automáticamente.
- Error de conexión backend: verifica Root Directory, nombres, puerto 8000, referencia BACKEND_URL y que ambos servicios estén en el mismo entorno. Si el entorno es antiguo IPv6-only, crea uno nuevo con red dual stack o adapta el bind IPv6.
- Error de acceso interno: verifica que el secreto de backend coincida con la referencia de frontend. Redepiega si cambias valores.
- Historial vacío tras redeploy: revisa el volumen `/data` y DATABASE_URL.
- La contraseña compartida no es un sistema de cuentas individuales. Los usuarios autorizados comparten el historial y pueden eliminar informes. No analices contenido privado ni subas una base antigua con datos sensibles. Para uso público masivo se necesita autenticación individual, permisos y controles adicionales.

## Referencias
- https://docs.railway.com/deployments/monorepo
- https://docs.railway.com/builds/dockerfiles
- https://docs.railway.com/variables
- https://docs.railway.com/volumes
- https://docs.railway.com/networking/private-networking
- https://developers.openai.com/api/docs/models/gpt-4o-mini

## Validación de entrega
Se ejecutaron pruebas unitarias de identificación, recomendaciones y OpenAI con respuestas HTTP simuladas. No se usó una clave real. El entorno de preparación no pudo descargar dependencias de npm ni dispone de aiosqlite; por tanto, quedan pendientes la compilación Next.js, pruebas de integración de la base, validación de autenticación de extremo a extremo y despliegue real. Antes de compartir la URL, ejecuta las verificaciones anteriores y confirma que el build y ambos servicios arrancan. Las dependencias npm se resolverán al instalar (no se pudo generar un lockfile aquí); conserva el package-lock.json que genere npm para instalaciones reproducibles.
