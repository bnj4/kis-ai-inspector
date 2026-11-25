import json
import pytest
import httpx
from app.services import ai

@pytest.fixture
def configured(monkeypatch):
    monkeypatch.setattr(ai.settings, 'ai_provider', 'openai')
    monkeypatch.setattr(ai.settings, 'openai_api_key', 'test-key-not-real')
    monkeypatch.setattr(ai.settings, 'openai_model', 'gpt-4o-mini')

def mock_http(monkeypatch, status, body):
    original=httpx.AsyncClient
    def handle(req):
        assert str(req.url)=='https://api.openai.com/v1/chat/completions'
        assert req.headers['authorization']=='Bearer test-key-not-real'
        payload=json.loads(req.content)
        assert payload['model']=='gpt-4o-mini'
        assert payload['store'] is False
        assert payload['max_completion_tokens']==ai.settings.openai_max_completion_tokens
        return httpx.Response(status,json=body)
    monkeypatch.setattr(ai.httpx,'AsyncClient',lambda **kw: original(transport=httpx.MockTransport(handle),**kw))

@pytest.mark.asyncio
async def test_openai_success(configured,monkeypatch):
    mock_http(monkeypatch,200,{'choices':[{'finish_reason':'stop','message':{'content':'{"summary":"prueba"}'}}]})
    content, provider=await ai.generate('prueba')
    assert provider=='openai' and json.loads(content)['summary']=='prueba'

@pytest.mark.asyncio
@pytest.mark.parametrize('status,expected',[(401,'clave API'),(429,'cuota'),(403,'permisos'),(404,'Modelo')])
async def test_openai_errors(configured,monkeypatch,status,expected):
    mock_http(monkeypatch,status,{'error':{'message':'sensitive detail'}})
    with pytest.raises(ai.AIProviderError,match=expected): await ai.generate('prueba')

@pytest.mark.asyncio
async def test_openai_missing_key(configured,monkeypatch):
    monkeypatch.setattr(ai.settings,'openai_api_key','')
    with pytest.raises(ai.AIProviderError,match='OPENAI_API_KEY'): await ai.generate('prueba')

@pytest.mark.asyncio
async def test_openai_truncated(configured,monkeypatch):
    mock_http(monkeypatch,200,{'choices':[{'finish_reason':'length','message':{'content':'{"summary":'}}]})
    with pytest.raises(ai.AIProviderError,match='incompleto'): await ai.generate('prueba')
