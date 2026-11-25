from urllib.parse import urlparse

def identify(url: str):
    p = urlparse(url); parts = [x for x in p.path.strip('/').split('/') if x]
    if p.hostname not in {"github.com", "huggingface.co", "www.huggingface.co"}: raise ValueError("Proveedor no compatible")
    if p.hostname == "github.com":
        if len(parts) < 2: raise ValueError("La URL debe apuntar a owner/repository")
        return "github", parts[0], parts[1].removesuffix(".git")
    if len(parts) >= 3 and parts[0] in {"models", "spaces", "datasets"}:
        return {"models":"model", "spaces":"space", "datasets":"dataset"}[parts[0]], parts[1], parts[2]
    # Hugging Face model pages conventionally use /owner/model without /models.
    if len(parts) == 2: return "model", parts[0], parts[1]
    raise ValueError("URL de Hugging Face no reconocida")
