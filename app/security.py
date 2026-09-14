import re
import structlog
from fastapi import HTTPException

logger = structlog.get_logger()

FRASES_PELIGROSAS = [
    "ignora tus instrucciones",
    "olvida lo anterior",
    "actúa como",
    "eres ahora",
    "ignore your instructions",
    "forget previous",
    "you are now",
    "jailbreak",
]

PATRON_EMAIL = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
PATRON_NUMEROS_SENSIBLES = r'\b\d{7,16}\b'

def enmascarar_pii(texto: str) -> str:
    texto_mod, emails_reemplazados = re.subn(PATRON_EMAIL, "[EMAIL_PROTEGIDO]", texto)
    texto_mod, datos_reemplazados = re.subn(PATRON_NUMEROS_SENSIBLES, "[DATO_PROTEGIDO]", texto_mod)
    
    if emails_reemplazados or datos_reemplazados:
        logger.info("pii_masked", emails_count=emails_reemplazados, datos_count=datos_reemplazados)
        
    return texto_mod

def sanitizar_input(texto: str) -> str:
    if not texto or not texto.strip():
        raise HTTPException(status_code=400, detail="Input vacío")
    
    if len(texto) > 1000:
        logger.warning("input_validation_failed", reason="length_exceeded", len=len(texto))
        raise HTTPException(status_code=400, detail="Input demasiado largo")
    
    texto_lower = texto.lower()
    for frase in FRASES_PELIGROSAS:
        if frase in texto_lower:
            logger.warning("security_alert_injection_blocked", matched_pattern=frase)
            raise HTTPException(
                status_code=400, 
                detail="Input no permitido: patrón de prompt injection detectado"
            )
    
    return enmascarar_pii(texto.strip())

def validar_output(respuesta: str) -> str:
    if not respuesta or not respuesta.strip():
        logger.error("llm_output_invalid", reason="empty_response")
        raise HTTPException(status_code=500, detail="Respuesta vacía del modelo")
    
    if len(respuesta) < 10:
        logger.error("llm_output_invalid", reason="too_short", len=len(respuesta))
        raise HTTPException(status_code=500, detail="Respuesta demasiado corta para ser válida")
    
    return respuesta.strip()