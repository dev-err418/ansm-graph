import requests
from bs4 import BeautifulSoup
from typing import Optional
    
async def get_ansm_content(id: int) -> Optional[str]:
    try:
        url = f"https://base-donnees-publique.medicaments.gouv.fr/affichageDoc.php?specid={id}&typedoc=R"
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        content_div = soup.find(id='contentDocument')
        if content_div:
            text_content = content_div.get_text()
            return text_content

    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")