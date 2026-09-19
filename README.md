# LLM Secure API

API REST asíncrona construida con FastAPI que integra Claude (Anthropic) aplicando patrones de producción: seguridad contra ataques LLM, observabilidad con logs estructurados, resiliencia ante fallos del proveedor y suite de tests sin costo de API.

---

## Qué demuestra este proyecto

- **Seguridad LLM**: Mitigación de Prompt Injection mediante lista de patrones peligrosos y delimitadores XML en el prompt; enmascaramiento de PII (emails y números sensibles) antes de llegar al modelo
- **Observabilidad**: Logs estructurados en JSON con `structlog`, trazabilidad HTTP por request (`request_id` UUIDv4) y medición de latencia en milisegundos; telemetría de tokens (`input_tokens` / `output_tokens`) por llamada
- **Resiliencia**: Reintentos automáticos con `tenacity` (exponential backoff + jitter) ante errores 429/500/503, timeout estricto de 10s en llamadas a Claude y mapeo a errores HTTP semánticos (503/504)
- **Validación de outputs**: Las respuestas del modelo se verifican antes de devolverse al cliente
- **Testing sin API Key**: Suite de 12 tests con `pytest-asyncio` y mocks que validan seguridad, timeouts y los 3 reintentos a costo $0
- Containerizado con Docker

---

## Stack

| Capa | Tecnología |
|---|---|
| Framework | FastAPI + Python 3.11 |
| LLM | Anthropic SDK — Claude 3.5 Sonnet |
| Observabilidad | structlog (JSON) |
| Resiliencia | tenacity 9.1.4 |
| Testing | pytest + pytest-asyncio + httpx |
| Containerización | Docker + Docker Compose |

---

## Flujo de una request

Input del usuario
→ Validación de longitud y vaciado (400)
→ Detección de Prompt Injection (400)
→ Enmascaramiento de PII — emails y números (log)
→ Delimitadores XML en el prompt
→ Llamada a Claude con timeout 10s
→ Si timeout → HTTP 504
→ Si error 429/500/503 → reintento (hasta 3 veces, exponential backoff)
→ Si reintentos agotados → HTTP 503
→ Validación del output (500 si vacío o muy corto)
→ Respuesta al cliente (200)


---

## Tabla de códigos HTTP

| Código | Situación |
|---|---|
| 200 | Consulta procesada correctamente |
| 400 | Input vacío, demasiado largo o con patrón de injection |
| 500 | Error interno o respuesta inválida del modelo |
| 503 | Claude no disponible tras agotar los 3 reintentos |
| 504 | Claude superó el timeout de 10 segundos |

---

## Observabilidad — ejemplo de log en producción

```json
{
  "event": "llm_call_success",
  "request_id": "4f3a1c2d-...",
  "path": "/consultar",
  "model": "claude-3-5-sonnet-20241022",
  "input_tokens": 42,
  "output_tokens": 118,
  "latency_ms": 843.5,
  "level": "info",
  "timestamp": "2026-09-11T05:00:00Z"
}
```

---

## Estrategia de resiliencia

`tenacity` intercepta errores `APIConnectionError`, `APITimeoutError`, `InternalServerError` y `RateLimitError`. Ante cada fallo reintentable espera entre 1 y 5 segundos con jitter aleatorio (evita thundering herd), hasta 3 intentos. Si el tercero falla, propaga HTTP 503. Si el error es timeout puro, mapea directo a HTTP 504 sin reintentos adicionales.

---

## Endpoints

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/` | Frontend de consulta |
| POST | `/consultar` | Envía un mensaje a Claude con validaciones de seguridad |

---

## Cómo correr el proyecto

```bash
git clone https://github.com/EmiDelgadoV/llm-secure-api
cd llm-secure-api
```

Creá un archivo `.env`:

ANTHROPIC_API_KEY=tu_clave_aqui


Levantá con Docker:

```bash
docker compose up --build
```

Accedé en `http://localhost:8000`

---

## Tests

La suite corre completa sin consumir API Key real — todos los llamados a Claude están mockeados.

```bash
pytest tests/ -v
```

Cobertura de `test_security.py` — sanitización de inputs, detección de injection, enmascaramiento de PII y validación de outputs.

Cobertura de `test_llm.py` — respuesta exitosa, timeout → 504, reintentos agotados → 503 con `call_count == 3`, recuperación en segundo intento.

---

## Autor

Victor Emiliano Delgado
[github.com/EmiDelgadoV](https://github.com/EmiDelgadoV) · [linkedin.com/in/emiliano-delgado-212b042b5](https://linkedin.com/in/emiliano-delgado-212b042b5)
