import csv
import os
import requests
import pandas as pd


def download_article(doi: str, api_key: str, save_path: str) -> None:
    """
    Downloads an article from Elsevier by DOI.

    Args:
    doi (str): The DOI of the article to download.
    api_key (str): Your API key for Elsevier's API.
    save_path (str): Path to save the downloaded article.
    """
    # headers = {
    #     'X-ELS-APIKey': api_key,
    #     'Accept': 'application/pdf'  # This specifies that you want the article in PDF format.
    # }

    # url = f'https://api.elsevier.com/content/article/doi/{doi}'

    request_url = f'https://api.elsevier.com/content/article/doi/{doi}?apiKey={api_key}&httpAccept=text%2Fxml'
    response = requests.get(request_url)
    # print(response.content)
    print(response.text)

    if response.status_code == 200:
        print("Content-Length:", response.headers.get('Content-Length'))
        print("Content-Type:", response.headers.get('Content-Type'))

        with open(save_path, 'wb') as f:
            f.write(response.content)
        print(f"Article downloaded successfully: {save_path}")
    else:
        print(f"Failed to download article. Status code: {response.status_code} - {response.text}")


def open_access_check(doi: str) -> bool:
    """
    Checks metadata of the article for open access flag
    """
    api_res = requests.get(f"https://api.openalex.org/works/https://doi.org/{doi}")
    metadata = api_res.json()
    if metadata.get("results") is not None:
        metadata = metadata["results"][0]
    is_oa = metadata["open_access"]["is_oa"]
    print(f"paper {doi} open access:")
    print(is_oa)
    return is_oa



if __name__ == "__main__":
    api_key = os.getenv("ELSVIER_API_KEY")
    # df = pd.read_csv('old_stuff/database_HEA.csv')

    # elsveir_papers = df.loc[df["source"]=="ELSVIER"].drop_duplicates(subset=['reference'])
    # elsveir_papers = elsveir_papers["URL"].str.replace("https://doi.org/", "")
    with open("elsveier_papers/non_oa.csv", 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["url"])
        metadata_exception = dict()
        count_oa = 0
        count_non_oa = 0
        elsveir_papers = ["10.1016-j.actamat.2013.01.042"]
        for doi in list(elsveir_papers):
            try:
                #oa = open_access_check(doi=doi)
                #
                # if oa:
                download_article(
                    doi=doi,
                    api_key=api_key,
                    save_path=(
                        "elsveier_papers/"
                        +doi.replace('/', '--')
                        +".xml"
                    )
                )
                count_oa+=1
                # else:
                #     csvwriter.writerow([doi])
                #     count_non_oa+=1

            except Exception as e:
                metadata_exception[doi] = e
                print(e)
                pass

            print(f"oa:{count_oa} vs non-oa:{count_non_oa}")
        print(metadata_exception)
        print(len(metadata_exception))
