import re
from fastapi import HTTPException

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
PATRON_NUMEROS_SENSIBLES = r'\b\d{7,16}\b'  # DNIs, CUITs o Números de Tarjeta


def enmascarar_pii(texto: str) -> str:
    """Detecta y reemplaza emails y números sensibles por tokens genéricos."""
    texto = re.sub(PATRON_EMAIL, "[EMAIL_PROTEGIDO]", texto)
    texto = re.sub(PATRON_NUMEROS_SENSIBLES, "[DATO_PROTEGIDO]", texto)
    return texto


def sanitizar_input(texto: str) -> str:
    if not texto or not texto.strip():
        raise HTTPException(status_code=400, detail="Input vacío")
    
    if len(texto) > 1000:
        raise HTTPException(status_code=400, detail="Input demasiado largo")
    
    texto_lower = texto.lower()
    for frase in FRASES_PELIGROSAS:
        if frase in texto_lower:
            raise HTTPException(
                status_code=400, 
                detail="Input no permitido: patrón de prompt injection detectado"
            )
    

    texto_limpio = texto.strip()
    return enmascarar_pii(texto_limpio)


def validar_output(respuesta: str) -> str:
    if not respuesta or not respuesta.strip():
        raise HTTPException(
            status_code=500, 
            detail="Respuesta vacía del modelo"
        )
    
    if len(respuesta) < 10:
        raise HTTPException(
            status_code=500,
            detail="Respuesta demasiado corta para ser válida"
        )
    
    return respuesta.strip()