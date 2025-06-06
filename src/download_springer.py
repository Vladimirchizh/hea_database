import requests
import pandas as pd

if __name__ == "__main__":
    df = pd.read_csv('old_stuff/database_HEA.csv')

    elsveir_papers = df.loc[df["source"]=="SPRINGER"].drop_duplicates(subset=['reference'])
    # print(list(elsveir_papers))
    for doi in list(elsveir_papers["URL"]):
        request_url = doi.replace("article/", "content/pdf/") + ".pdf"
        print(request_url)
        response = requests.get(request_url)
        doi = doi.replace("https:/link.springer.com/article/", "").replace("/","-") + ".pdf"
        save_path = "springer/"+doi
        # print(response.content)
        # print(response.text)

        if response.status_code == 200:
            # print("Content-Length:", response.headers.get('Content-Length'))
            # print("Content-Type:", response.headers.get('Content-Type'))

            with open(save_path, 'wb') as f:
                f.write(response.content)
            print(f"Article downloaded successfully: {save_path}")
        else:
            print(f"Failed to download article. Status code: {response.status_code} - {response.text}")
