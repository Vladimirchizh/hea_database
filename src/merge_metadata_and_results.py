import os
import json
import csv
from json import JSONDecodeError
import xml.etree.ElementTree as ET
import pandas as pd

def extract_article_title(file_path):
    """Extracts the article title from an XML file."""
    try:
        # Parse the XML file
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Define namespaces
        namespaces = {
            'default': 'http://www.elsevier.com/xml/svapi/article/dtd',
            'dc': 'http://purl.org/dc/elements/1.1/',
        }

        # Search for the title using the correct namespace
        title_element = root.find('.//dc:title', namespaces)

        if title_element is not None:
            return title_element.text.strip()
        else:
            return "Title not found"
    except Exception as e:
        return f"Error processing file {file_path}: {e}"

def process_directory(directory):
    """Processes all XML files in a directory."""
    titles = {}
    for file_name in os.listdir(directory):
        if file_name.endswith(".xml"):
            file_path = os.path.join(directory, file_name)
            title = extract_article_title(file_path)
            titles[file_name.replace(".xml", "")] = title
    return titles


titles = process_directory("/Users/vdc/hea_llm_rag/elsevier")

def cd_to_csv(papers_names: list, papers_jsons: list) -> None:
    """
    Args:
        papers_jsons: list of responses from LLM (each response contains a ```json block)
    Returns:
        Writes data to output2.csv
    """
    with open('output11.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        headers = [
            'id', 'Paper', "Name", 'Alloy', 'Nb of phase', 'Phase',
            'Experimental or theoretical', 'Experimental details',
            'Theoretical details', 'Special conditions', 'Type of solution'
        ]
        writer.writerow(headers)

        for i, json_data in enumerate(papers_jsons):
            # Extract JSON block from response
            try:
                json_data = json_data.split("```json")[1].split("```")[0]
            except IndexError:
                print("No valid ```json block found in this paper's response")
                continue

            # Load JSON data into a Python dictionary
            try:
                data = json.loads(json_data)
            except JSONDecodeError as e:
                print(f"json decode error for paper {papers_names[i]}: {e}")
                continue

            # Iterate over each alloy in the data
            for alloy_key, alloy_data in data.items():
                # Basic info
                id = i
                paper = papers_names[i]
                print(paper)
                try:
                    name = titles[paper.replace('.txt', '')]
                except KeyError:
                    name = 'N/A'

                alloy = alloy_data.get('chemical_formula', alloy_key)

                # Extract phases
                crystallographic_phases = alloy_data.get('crystallographic_phases', [])

                if len(crystallographic_phases) == 0:
                    # print(alloy_data)
                    crystallographic_phases = alloy_data.get('phases', [])

                nb_of_phase = len(crystallographic_phases)
                if nb_of_phase == 0:
                    print(f"No crystallographic phases found for {alloy}")
                    print(alloy_data)

                phases = []
                for phase in crystallographic_phases:
                    structure = phase.get('structure', '')
                    structure_lower = structure.lower()
                    if structure_lower == 'body-centered cubic':
                        structure_abbrev = 'BCC'
                    elif structure_lower == 'face-centered cubic':
                        structure_abbrev = 'FCC'
                    elif structure_lower == 'hexagonal':
                        structure_abbrev = 'HCP'
                    else:
                        # If the structure isn't one of the known ones, just use it directly
                        structure_abbrev = structure if structure else 'Unknown'

                    # If it's explicitly intermetallic
                    if phase.get('phase_type', '').lower() == 'intermetallic':
                        structure_abbrev += ' (Intermetallic)'

                    phases.append(structure_abbrev)

                phase_str = ' + '.join(phases) if phases else 'N/A'

                # Determine if it's experimental, theoretical, or both
                exp_or_theo = 'N/A'
                experimental_details = 'N/A'
                theoretical_details = 'N/A'

                # Check for synthesis_or_calculation hui
                synthesis = alloy_data.get('synthesis_or_calculation', None)
                if synthesis:
                    exp_or_theo = synthesis.get('type', 'N/A')  # .capitalize()
                    method = synthesis.get('method', '')
                    if method or parameters:
                        parameters = synthesis.get('parameters', {})
                        detail_parts = [method] if method else []
                        if isinstance(parameters, dict):
                            for k, v in parameters.items():
                                param_str = f"{k.replace('_', ' ').capitalize()}: {v}"
                                detail_parts.append(param_str)
                        else:
                            param_str = parameters
                        if detail_parts:
                            experimental_details = ', '.join(detail_parts)
                    if exp_or_theo in ['experimental', 'theoretical and experimental', "combination", "both"]:
                        experimental = synthesis.get('experimental_details', {})
                        if experimental:
                            method = experimental.get('method', '')
                            parameters = experimental.get('parameters', {})
                            detail_parts = [method] if method else []
                            if isinstance(parameters, dict):
                                for k, v in parameters.items():
                                    param_str = f"{k.replace('_', ' ').capitalize()}: {v}"
                                    detail_parts.append(param_str)
                            else:
                                detail_parts.append(str(parameters))
                            if detail_parts:
                                experimental_details = ', '.join(detail_parts)
                        else:
                            syn_details = alloy_data.get('synthesis_details', {})
                            method = syn_details.get('method', '')
                            parameters = syn_details.get('parameters', {})
                            if method or parameters:
                                exp_or_theo = 'experimental'
                            detail_parts = [method] if method else []
                            if isinstance(parameters, dict):
                                for k, v in parameters.items():
                                    param_str = f"{k.replace('_', ' ').capitalize()}: {v}"
                                    detail_parts.append(param_str)
                            else:
                                param_str = parameters
                            if detail_parts:
                                experimental_details = ', '.join(detail_parts)
                            # print(exp_or_theo+" + "+experimental_details)

                    if exp_or_theo in ['theoretical', 'theoretical and experimental', "combination", "both"]:
                        # Extract Theoretical Details
                        theoretical = synthesis.get('theoretical_details', {})
                        if theoretical:
                            method = theoretical.get('method', '')
                            parameters = theoretical.get('parameters', {})
                            detail_parts = [method] if method else []
                            if isinstance(parameters, dict):
                                for k, v in parameters.items():
                                    param_str = f"{k.replace('_', ' ').capitalize()}: {v}"
                                    detail_parts.append(param_str)
                            else:
                                detail_parts.append(str(parameters))
                            if detail_parts:
                                theoretical_details = ', '.join(detail_parts)
                        else:
                            syn_details = alloy_data.get('synthesis_details', {})
                            method = syn_details.get('method', '')
                            parameters = syn_details.get('parameters', {})
                            if method or parameters:
                                exp_or_theo = 'experimental'
                                detail_parts = [method] if method else []
                                if isinstance(parameters, dict):
                                    for k, v in parameters.items():
                                        param_str = f"{k.replace('_', ' ').capitalize()}: {v}"
                                        detail_parts.append(param_str)
                                else:
                                    detail_parts.append(str(parameters))
                                if detail_parts:
                                    experimental_details = ', '.join(detail_parts)
                else:
                    # Check for synthesis_details instead
                    syn_details = alloy_data.get('synthesis_details', {})
                    method = syn_details.get('method', '')
                    parameters = syn_details.get('parameters', {})
                    if method:
                        exp_or_theo = 'Experimental'
                    detail_parts = [method] if method else []
                    if isinstance(parameters, dict):
                        for k, v in parameters.items():
                            param_str = f"{k.replace('_', ' ').capitalize()}: {v}"
                            detail_parts.append(param_str)
                    else:
                        param_str = parameters
                    if detail_parts:
                        experimental_details = ', '.join(detail_parts)

                special_conditions = alloy_data.get('special_conditions', 'N/A')
                type_of_solution = alloy_data.get('phase_classification', 'N/A')

                row = [
                    id, paper, name, alloy, nb_of_phase, phase_str,
                    exp_or_theo, experimental_details,
                    theoretical_details, special_conditions, type_of_solution
                ]
                writer.writerow(row)

        print("Data has been successfully written to 'output3.csv'")

if __name__ == "__main__":
    df = pd.read_csv('/Users/vdc/result_multiple_prompts-batch-mds-1127-1.csv')

    batches = [
        "result_multiple_prompts-batch-mds-rsc.csv",
        "result_multiple_prompts-batch-mds-rsc2.csv",
        "result_multiple_prompts-batch-mds-springer.csv",
        "result_multiple_prompts-batch-mds-springer2.csv",
    ]
    for batch in batches:
        temp = pd.read_csv(f'/Users/vdc/{batch}')
        df = pd.concat([df, temp], ignore_index=True)


    for i in range(2, 11):
        temp = pd.read_csv(f'/Users/vdc/result_multiple_prompts-batch-mds-1127-{i}.csv')
        df = pd.concat([df, temp], ignore_index=True)



    df = df.loc[df["context_missread_bug"] == True].reset_index(drop=True)
    df['reference'] = df['article'].str.replace('.txt', '')
    df["reference"] = df["article"].str.replace('parsed_output--', '')
    df["reference"] = df["article"].str.replace('parsed_output-', '')
    df["reference"] = df["reference"].str.replace('.pdf.md', '')
    df["reference"] = df["reference"].str.upper()

    metadata = pd.read_csv("/Users/vdc/hea_llm_rag/old_stuff/database_HEA.csv")
    # metadata = metadata.loc[metadata["source"] == "ELSVIER"].drop(columns=["Unnamed: 0", "Unnamed: 0.1"])

    metadata = metadata.groupby(['reference','source','URL'])['compound'].apply(', '.join).reset_index()
    metadata["reference"] = metadata["reference"].str.replace('10.1039-', '')

    metadata.drop_duplicates(inplace=True)

    merged_df = pd.merge(df, metadata, on='reference', how='left')


    merged_df.to_csv("~/merged_data.csv")


    # Process the files and print the titles
    cd_to_csv(papers_names=list(merged_df["reference"]), papers_jsons=list(merged_df["prompt5"]))
