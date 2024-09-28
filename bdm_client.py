import aiohttp
import aiofiles

async def download_http_file(filename):
    protocol = "https:"
    host = "base-donnees-publique.medicaments.gouv.fr"
    path = "/telechargement.php"
    url = f"{protocol}//{host}{path}?fichier={filename}.txt"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()
            async with aiofiles.open(filename + '.txt', mode='wb') as f:
                async for chunk in response.content.iter_chunked(1024):
                    await f.write(chunk)
    
    async def file_reader():
        async with aiofiles.open(filename + '.txt', mode='r', encoding='latin1') as f:
            async for line in f:
                yield line.strip()

    return file_reader()
