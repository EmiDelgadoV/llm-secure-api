import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException
from anthropic import (
    APITimeoutError,
    APIConnectionError,
    InternalServerError,
)

from app.llm import consultar_llm


@pytest.fixture
def mock_anthropic_response():
    """Genera una respuesta exitosa simulada con estructura idéntica al SDK de Anthropic."""
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="Esta es una respuesta simulada de prueba.")]
    mock_response.usage.input_tokens = 15
    mock_response.usage.output_tokens = 25
    return mock_response

@pytest.mark.asyncio
async def test_consultar_llm_exito(mock_anthropic_response):
    with patch("app.llm.client.messages.create", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_anthropic_response

        respuesta = await consultar_llm("¿Qué es la fotosíntesis?")

        assert respuesta == "Esta es una respuesta simulada de prueba."
        assert mock_create.call_count == 1

@pytest.mark.asyncio
async def test_consultar_llm_timeout_lanza_504():
    mock_request = MagicMock()
    
    with patch("app.llm.client.messages.create", new_callable=AsyncMock) as mock_create:
        # Simula que la llamada supera los 10s de timeout configurados
        mock_create.side_effect = APITimeoutError(request=mock_request)

        with pytest.raises(HTTPException) as exc_info:
            await consultar_llm("Consulta de prueba")

        assert exc_info.value.status_code == 504
        assert "Gateway Timeout" in exc_info.value.detail

@pytest.mark.asyncio
async def test_consultar_llm_reintentos_agotados_lanza_503():
    mock_request = MagicMock()

    with patch("app.llm.client.messages.create", new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = APIConnectionError(request=mock_request)

        with pytest.raises(HTTPException) as exc_info:
            await consultar_llm("Consulta de prueba")
        assert mock_create.call_count == 3
        assert exc_info.value.status_code == 503
        assert "no se encuentra disponible" in exc_info.value.detail


@pytest.mark.asyncio
async def test_consultar_llm_recuperacion_en_segundo_intento(mock_anthropic_response):
    mock_request = MagicMock()

    with patch("app.llm.client.messages.create", new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = [
            InternalServerError(message="Error interno del proveedor", response=MagicMock(), body=None),
            mock_anthropic_response
        ]

        respuesta = await consultar_llm("Consulta con recuperación")

        assert respuesta == "Esta es una respuesta simulada de prueba."
        assert mock_create.call_count == 2