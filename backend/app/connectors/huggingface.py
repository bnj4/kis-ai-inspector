import httpx
from app.core.config import settings

class HuggingFaceConnector:
    async def collect(self, kind: str, owner: str, name: str):
        headers = {"Authorization": f"Bearer {settings.hf_token}"} if settings.hf_token else {}
        if kind == "model": endpoint = f"https://huggingface.co/api/models/{owner}/{name}?expand[]=private&expand[]=tags&expand[]=pipeline_tag&expand[]=cardData&expand[]=config&expand[]=siblings&expand[]=lastModified"
        elif kind == "dataset": endpoint = f"https://huggingface.co/api/datasets/{owner}/{name}?expand[]=private&expand[]=tags&expand[]=cardData&expand[]=siblings&expand[]=lastModified"
        else: endpoint = f"https://huggingface.co/api/spaces/{owner}/{name}?expand[]=private&expand[]=tags&expand[]=cardData&expand[]=siblings&expand[]=runtime&expand[]=lastModified"
        async with httpx.AsyncClient(timeout=settings.request_timeout, follow_redirects=False) as c:
            r = await c.get(endpoint, headers=headers); r.raise_for_status(); data = r.json()
            if data.get("private"):
                raise ValueError("Solo se admiten recursos públicos en este espacio compartido.")
            readme = await c.get(f"https://huggingface.co/{'datasets/' if kind == 'dataset' else 'spaces/' if kind == 'space' else ''}{owner}/{name}/raw/main/README.md", headers={})
            data["readme"] = readme.text[:settings.max_file_bytes] if readme.is_success else None
            return data
