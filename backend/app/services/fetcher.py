import httpx
from bs4 import BeautifulSoup


async def fetch_job_listing(url: str) -> str:
    async with httpx.AsyncClient(follow_redirects=True, timeout=15) as client:
        response = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "nav", "header", "footer", "aside"]):
        tag.decompose()

    text = soup.get_text(separator="\n", strip=True)
    lines = [l for l in text.splitlines() if l.strip()]
    return "\n".join(lines[:300])
