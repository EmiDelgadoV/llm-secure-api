from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from app.security import sanitizar_input, validar_output
from app.llm import consultar_llm

app = FastAPI(
    title="LLM Secure API",
    description="API segura para consultas a Claude con mitigación de Prompt Injection y protección de PII",
    version="1.0.0"
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")


class ConsultaDTO(BaseModel):
    texto: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Consulta enviada por el usuario"
    )

class RespuestaDTO(BaseModel):
    respuesta: str
    status: str = "exito"


@app.get("/")
async def root():
    return FileResponse("app/static/index.html")


@app.post("/consultar", response_model=RespuestaDTO)
async def endpoint_consultar(payload: ConsultaDTO):
    texto_limpio = sanitizar_input(payload.texto)
    respuesta_raw = await consultar_llm(texto_limpio)
    respuesta_final = validar_output(respuesta_raw)
    return RespuestaDTO(respuesta=respuesta_final)