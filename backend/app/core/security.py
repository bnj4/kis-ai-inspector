import ipaddress, socket
from urllib.parse import urlparse

ALLOWED_HOSTS = {"github.com", "api.github.com", "huggingface.co", "www.huggingface.co"}

def validate_resource_url(raw: str) -> str:
    p = urlparse(raw.strip())
    if p.scheme != "https" or not p.hostname or p.username or p.password:
        raise ValueError("La URL debe ser HTTPS y no puede contener credenciales.")
    host = p.hostname.lower().rstrip(".")
    if host not in ALLOWED_HOSTS:
        raise ValueError("Proveedor no compatible. Se admiten GitHub y Hugging Face.")
    try:
        for item in socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM):
            ip = ipaddress.ip_address(item[4][0])
            if not ip.is_global:
                raise ValueError("La URL resuelve a una dirección no pública.")
    except socket.gaierror:
        pass
    return raw.strip()
