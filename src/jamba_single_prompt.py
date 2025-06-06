import csv
import os
import markdown
import pandas as pd
from ai21 import AI21Client
from ai21.models.chat import ChatMessage
from llama_parse import LlamaParse

import requests
from old_stuff.walk_trough_papers_multiple_ import multiple_prompts
from prompts import system_prompt, single_prompt

from os import listdir
from os.path import isfile, join

LLAMA_PARSE_API = os.getenv("LLAMA_PARSE_API")

model = "jamba-1.5-large"

client = AI21Client(
    api_key=os.getenv("AI21_API_KEY")
)
parser = LlamaParse(
    api_key=LLAMA_PARSE_API,
    result_type="markdown"
)
file_extractor = {".pdf": parser}


def walk_through_papers(scientific_papers: list, filename: str):
    with open(filename, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["article", "json_dictionary"])
        rows = []

        for scientific_paper in scientific_papers:
            with open(scientific_paper, 'r') as f:
                d = markdown.markdown(f.read())
            messages = [
                ChatMessage(
                    content=system_prompt,
                    role="system",
                ),
                ChatMessage(
                    content=f"Here is the paper in the markdown for your analysis: {d}",
                    role="user",
                ),
                ChatMessage(
                    content=single_prompt,
                    role="user",
                )

            ]

            llm_request = client.chat.completions.create(
                messages=messages,
                model=model,
            )
            responses = []
            responses.append(llm_request.choices[0].message.content)
            print(llm_request.choices[0].finish_reason)
            # print(llm_request.choices[0])
            def check_if_finished(llm_request):
                if llm_request.choices[0].finish_reason == "length":
                    messages.append(ChatMessage(content=responses[-1]+"\n continue", role="assistant"))
                    print(responses[-1])

                    llm_request = client.chat.completions.create(
                        messages=messages,
                        model=model,
                    )
                    responses.append(llm_request.choices[0].message.content)
                    check_if_finished(llm_request)

            check_if_finished(llm_request)
            print(len(responses))
            rows.append([scientific_paper, "".join(responses)])
            csvwriter.writerows(rows)
            rows = []


if __name__ == "__main__":


    walk_through_papers([], 'result_single_prompts-batch-mds-1120.csv')
