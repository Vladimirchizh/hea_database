import csv
import time
import os
import markdown
import pandas as pd
from ai21 import AI21Client
from ai21.models.chat import ChatMessage
# from llama_parse import LlamaParse
# from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
import requests
from prompts import multiple_prompts

from os import listdir
from os.path import isfile, join

LLAMA_PARSE_API = os.getenv("LLAMA_PARSE_API")

model = "jamba-1.5-large"

client = AI21Client(
    api_key=os.getenv("AI21_API_KEY")
)
# parser = LlamaParse(
#     api_key=LLAMA_PARSE_API,
#     result_type="markdown"
# )
# file_extractor = {".pdf": parser}


# def download_pdf(url, output_filename):
#     try:
#         # Add headers to mimic a browser request
#         headers = {
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
#         }

#         # Make the request
#         response = requests.get(url, headers=headers, verify=True)

#         # Check if the request was successful
#         response.raise_for_status()

#         # Verify content type (optional but recommended)
#         content_type = response.headers.get('content-type', '')
#         if 'application/pdf' not in content_type.lower():
#             print(f"Warning: Content type is {content_type}, might not be a PDF")

#         # Check if we got any content
#         if len(response.content) < 100:  # Arbitrary small size check
#             print("Warning: Downloaded file seems too small to be a valid PDF")

#         # Save the file
#         with open(output_filename, 'wb') as f:
#             f.write(response.content)

#         print(f"Successfully downloaded: {output_filename}")

#     except requests.exceptions.RequestException as e:
#         print(f"An error occurred: {e}")
#         return False

#     return True


def walk_through_papers(scientific_papers: list, filename: str):
    with open(filename, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["article", "pdf_url", "prompt1", "prompt2", "prompt3", "prompt4", "prompt5", "context_missread_bug"])
        count = 0
        rows = []
        # for filename in os.listdir('/Users/vdc/hea_llm_rag/'):
        #     if "parsed_output" in filename:
        #         scientific_papers.append(filename)
        mypath = "rsc-mds"#"elseveir_txt"#
        # scientific_papers.extend([f for f in listdir(mypath) if isfile(join(mypath, f))])
        scientific_papers.append("parsed_output-10.1016-j.jmrt.2023.05.201.pdf.md")
        # print(scientific_papers)
        flag = False
        for scientific_paper in scientific_papers:
            # if scientific_paper != "parsed_output-d3dt00223c.pdf.md" and not flag:
            #     print(f"{scientific_paper} skipped")
            #     continue
            # flag = True
            #
            # loaded_file_name = scientific_paper#.split("/")[-1]
            # print(loaded_file_name)
            #
            # if not "local_papers" in scientific_paper:
            #     scientific_paper = scientific_paper.replace("article/", "content/pdf/") # + ".pdf"
            #     # Send a GET request to the URL
            #     download_pdf(scientific_paper, "output.pdf")
            #
            # documents = SimpleDirectoryReader(
            #     input_files=[loaded_file_name],
            #     file_extractor=file_extractor,
            # ).load_data()
            # print(documents)
            # with open(f'parsed_output-{scientific_paper.split("/")[-1]}.md', 'w') as f:
            #     for doc in documents:
            #         f.write(doc.text + '\n')

            # d = "\n".join([doc.text for doc in documents])
            with open(join(mypath, scientific_paper), 'r', encoding="utf-8") as f:
                try:
                    # d = markdown.markdown(f.read())
                    d = f.read()
                except Exception as e:
                    print(e)
                    continue
                # print(d)
            messages = [
                ChatMessage(
                    content=(
                        """
You are a materials science expert specializing in crystallography and high entropy alloys. Analyze scientific papers with these core behaviors:

- Process information sequentially while maintaining context between questions
- Extract and verify all quantitative data, especially chemical formulas and processing parameters
- Use proper chemical notation and consistent formatting
- Present information in structured lists
- State explicitly any uncertainties or missing information
- Pay an extra attention to the markdown tables 

For each question:
- Consider the entire paper before answering
- Cross-reference information across sections
- Flag any contradictions or inconsistencies
- Maintain scientific rigor and precision
- Present answers in clear, organized format

Quality standard: Be thorough and precise while maintaining clarity. If information is ambiguous or missing, state this explicitly.
                        """),
                    role="system"
                ),
                ChatMessage(
                    content=f"Here is the paper in the markdown for your analysis: {d}",
                    role="user"
                )

            ]
            responses = []
            try:
                for index, prompt in enumerate(multiple_prompts):
                    if len(responses) > 0:
                        messages.append(ChatMessage(content=responses[-1], role="assistant"))

                    messages.append(ChatMessage(content=prompt, role="user"))
                    print(index)
                    # if index == 4:

                    response, finish_reason = run(messages)

                    print(response)


                    responses.append(response)

                    def check_if_finished(finish_reason):
                        print(f"finish reason: {finish_reason}")
                        if finish_reason == "length":
                            messages.append(
                                ChatMessage(
                                    content=responses[-1]+"\n continue right where you dropped with the next character",
                                    role="assistant"
                                )
                            )

                            response, finish_reason = run(messages=messages)
                            responses[index] = responses[index]+response
                            check_if_finished(finish_reason)

                    check_if_finished(finish_reason)
                    # else:
                    #     responses.append("skip")
                if len(responses[-1]) < 60:
                    responses.append(False)
                else:
                    responses.append(True)
            except Exception as e:
                print(e)
                time.sleep(100)
                continue
            rows.append([scientific_paper, scientific_paper] + responses)
            csvwriter.writerows(rows)
            rows = []



def run(messages):
    llm_request = client.chat.completions.create(
        messages=messages,
        model=model,
        stream=True,
    )
    response = ""
    for chunk in llm_request:
        ch = chunk.choices[0].delta.content
        fr = chunk.choices[0].finish_reason
        if ch:
            response += ch
            print(ch, end="")

    return response, fr


if __name__ == "__main__":
    # df = pd.read_csv('old_stuff/database_HEA.csv')
    # unique_rows = df.loc[df["source"] == "SPRINGER"].drop_duplicates(subset=['reference'])
    # unique_rows_as_list = list(unique_rows)

    walk_through_papers([], 'result_multiple_prompts-batch-mds-1203.csv')
