id = 64741955
url = f"https://base-donnees-publique.medicaments.gouv.fr/affichageDoc.php?specid={id}&typedoc=R"

import requests
from bs4 import BeautifulSoup

try:
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')

    content_div = soup.find(id='contentDocument')
    if content_div:
        text_content = content_div.get_text()
        print(len(text_content))

except requests.exceptions.RequestException as e:
    print(f"Error fetching the URL: {e}")