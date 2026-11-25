# Arquitectura

## Capas
- `frontend/`: Next.js, React y TypeScript. Solo consume la API local; no contiene claves de proveedor.
- `backend/app/api`: endpoints HTTP.
- `backend/app/connectors`: clientes HTTP específicos para GitHub y Hugging Face.
- `backend/app/services/identify.py`: clasificación automática por dominio y ruta.
- `backend/app/services/analyzer.py`: orquestación de recolección, evidencias y reporte.
- `backend/app/services/ai.py`: adaptadores Ollama/OpenAI y fallback sin IA.
- `backend/app/core`: configuración, validación de URL y SQLAlchemy.
- SQLite almacena el informe completo como JSON para facilitar una migración posterior.

## Flujo
1. Validar URL HTTPS y proveedor permitido.
2. Identificar tipo de recurso.
3. Consultar API oficial y README cuando esté disponible.
4. Construir evidencias con procedencia.
5. Enviar un subconjunto acotado de datos al proveedor IA con instrucciones explícitas para tratar contenido externo como no confiable.
6. Validar JSON de salida y persistir informe.
7. Si no hay IA, devolver datos y evidencias sin fingir una interpretación.

## Límites actuales
- No se ejecuta código de repositorios ni Spaces.
- No se descargan datasets completos ni pesos de modelos.
- La recuperación GitHub usa una selección inicial de endpoints y no pagina exhaustivamente todos los issues/PR.
- El progreso de la interfaz refleja una solicitud en curso, no etapas individuales del backend.
- La evaluación de seguridad es indicativa, no un escaneo exhaustivo de CVE/SBOM.
- La comparación entre recursos y benchmarks ejecutables quedan como trabajo pendiente.
