import time
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

import pandas as pd


def get_pdf(year, doi, db):
    url = f"https://pubs.rsc.org/en/content/articlepdf/{year}/{db}/{doi}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    payload = {}  # Add your payload if needed

    session = requests.Session()
    retries = Retry(
        total=3,  # Try fewer times to avoid being blocked
        backoff_factor=10,  # Increase backoff to 10 seconds
        status_forcelist=[429, 500, 502, 503, 504]
    )
    session.mount('https://', HTTPAdapter(max_retries=retries))

    try:
        time.sleep(5)  # Wait before request to avoid triggering server defenses
        with session.get(url, headers=headers, data=payload, stream=True, timeout=15) as r:
            r.raise_for_status()
            with open(f'rsc/{doi}.pdf', 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
    except requests.exceptions.RequestException as e:
        print("Connection error:", e)


if __name__ == "__main__":
    df = pd.read_csv('old_stuff/database_HEA.csv')

    elsveir_papers = df.loc[df["source"]=="RSC"].drop_duplicates(subset=['reference'])

    for doi in list(elsveir_papers["URL"])[1:]:
        year = 2023
        doi = doi.split("10.1039-")[1].lower()
        db = doi[2]+doi[3]
        get_pdf(year, doi, db)
