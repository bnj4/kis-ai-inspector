# Matriz de funcionalidades

| Funcionalidad | Estado | Verificación |
|---|---|---|
| Proyecto nuevo frontend/backend | Implementado | Estructura revisada |
| Identificación GitHub | Implementado | Test unitario |
| Identificación HF Model/Space/Dataset | Implementado | Tests unitarios |
| Validación básica de URL/proveedor | Implementado | Revisión de código; requiere pruebas de seguridad adicionales |
| Recolección GitHub | Implementación inicial | No probada contra red en este entorno |
| Recolección HF | Implementación inicial | No probada contra red en este entorno |
| Ollama | Implementado | Requiere Ollama local para prueba real |
| OpenAI opcional | Implementado | Requiere API key para prueba real |
| Modo sin IA | Implementado | Ruta de fallback en código |
| Persistencia SQLite | Implementado | Requiere ejecutar backend para prueba de integración |
| Historial: listar/abrir/eliminar | Parcial | Listar/eliminar API; apertura desde UI pendiente de completar |
| Informe con evidencias | Implementado | Esquema y UI presentes |
| Exportación PDF/Markdown | Pendiente | No implementada |
| Comparación de recursos | Pendiente | No implementada |
| Benchmarks reproducibles | Pendiente | No implementados; no se ejecuta código externo |
| Progreso real por etapas | Pendiente | UI muestra estado general, no eventos por etapa |
| Paginación/caché avanzada | Pendiente | No implementada |
| Escaneo de vulnerabilidades/CVE | Parcial | Datos disponibles según permisos/API; sin escáner dedicado |
| Pruebas de integración/end-to-end | Pendiente | Requieren entorno con servicios y red |

**No se declara superada la aceptación completa.** El entorno de construcción no dispone de credenciales de proveedores ni de servicios externos para validar integraciones reales.
