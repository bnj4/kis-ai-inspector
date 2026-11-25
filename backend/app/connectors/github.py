import httpx
from app.core.config import settings

class GitHubConnector:
    def __init__(self):
        self.headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
        if settings.github_token: self.headers["Authorization"] = f"Bearer {settings.github_token}"

    async def get(self, path: str):
        async with httpx.AsyncClient(timeout=settings.request_timeout, follow_redirects=False) as c:
            r = await c.get("https://api.github.com" + path, headers=self.headers)
            r.raise_for_status(); return r.json()

    async def collect(self, owner: str, repo: str):
        base = f"/repos/{owner}/{repo}"
        repo_data = await self.get(base)
        if repo_data.get("private"):
            raise ValueError("Solo se admiten repositorios públicos en este espacio compartido.")
        tasks = {
            "readme": self.get(base + "/readme"),
            "languages": self.get(base + "/languages"),
            "contents": self.get(base + "/contents"),
            "releases": self.get(base + "/releases?per_page=5"),
            "issues": self.get(base + "/issues?state=all&per_page=10"),
            "contributors": self.get(base + "/contributors?per_page=10"),
            "workflows": self.get(base + "/actions/workflows"),
        }
        out = {"repository": repo_data}
        for key, coro in tasks.items():
            try: out[key] = await coro
            except Exception as e: out[key] = {"unavailable": str(e)}
        return out
