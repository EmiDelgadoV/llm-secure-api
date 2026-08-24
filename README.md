# LLM Secure API

API REST construida con FastAPI que integra Claude (Anthropic) aplicando buenas prácticas de seguridad para el uso de LLMs en producción.

---

## Qué demuestra este proyecto

- Mitigación de **Prompt Injection** mediante sanitización de inputs y delimitadores XML en el prompt
- **Enmascaramiento de PII** — emails y números sensibles se reemplazan antes de llegar al modelo
- **Validación de outputs** — las respuestas del LLM se verifican antes de devolverse al cliente
- **System prompt estricto** — el modelo tiene instrucciones claras para evitar alucinaciones
- Cliente asíncrono con `AsyncAnthropic` para no bloquear FastAPI
- Containerizado con Docker

---

## Stack

- Python 3.11
- FastAPI
- Anthropic SDK (Claude)
- Docker
- pytest

---

## Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/` | Frontend de consulta |
| POST | `/consultar` | Envía un mensaje a Claude con validaciones de seguridad |

---

## Flujo de seguridad

```
Input del usuario
  → Sanitización (detección de prompt injection)
  → Enmascaramiento de PII (emails, números)
  → Delimitadores XML en el prompt
  → Claude genera respuesta
  → Validación del output
  → Respuesta al cliente
```

---

## Cómo correr el proyecto

```bash
git clone https://github.com/EmiDelgadoV/llm-secure-api
cd llm-secure-api
```

Creá un archivo `.env`:

```
ANTHROPIC_API_KEY=tu_clave_aqui
```

Levantá con Docker:

```bash
docker compose up --build
```

Accedé en `http://localhost:8000`

---

## Tests

```bash
pytest tests/test_security.py -v
```

8 tests cubriendo sanitización de inputs y validación de outputs.

---

## Autor

Victor Emiliano Delgado
[github.com/EmiDelgadoV](https://github.com/EmiDelgadoV) · [linkedin.com/in/emiliano-delgado-212b042b5](https://linkedin.com/in/emiliano-delgado-212b042b5)