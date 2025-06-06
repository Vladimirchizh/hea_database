import json
import re
import csv
from json import JSONDecodeError
import pandas as pd


def extract_phase_from_details(structure: str, details: str, phase_type: str) -> str:
    """
    Extract phase information from structure and details fields.
    
    Args:
        structure: Base crystal structure
        details: Detailed phase information
        phase_type: Type of phase (e.g., intermetallic)
    
    Returns:
        str: Formatted phase description
    """
    # First convert basic structure names
    base_structure = structure
    structure_lower = structure.lower()
    structure_mapping = {
        'body-centered cubic': 'BCC',
        'face-centered cubic': 'FCC',
        #'hexagonal close-packed': 'HCP',
        'body-centered tetragonal': 'BCT',
        'hexagonal': 'HCP'
    }
    
    for key, value in structure_mapping.items():
        if key in structure_lower:
            base_structure = value
            break
    
    if not details:
        return base_structure
    
    # Check for specific phases in details
    details = details.lower()
    phase_str = base_structure
    
    # Special phase indicators
    special_phases = {
        'a2': 'A2',
        'b2': 'B2',
        'b19': 'B19',
        'l12': 'L12',
        'c14': 'C14',
        'c15': 'C15',
        'cr2ta': 'Cr2Ta',
        'ti2ni': 'Ti2Ni',
        'spinel': 'Spinel',
        'o-phase': 'O-phase',
        'laves': 'Laves',
        'dr+id': 'DR+ID',
        'amorphous': 'Amorphous'
    }
    
    # Check for numbered variants (BCC1, BCC2, etc.)
    # if any(char.isdigit() for char in details):
    #     for i in range(1, 10):  # Check numbers 1-9
    #         if str(i) in details:
    #             phase_str = f"{base_structure}{i}"
    #             break
    
    # Check for special phases
    for key, value in special_phases.items():
        if (key in details.lower()) and (key not in structure_lower) and (key not in phase_str.lower()):
            if phase_str == base_structure:  # If we haven't modified the base structure yet
                phase_str += (" "+value) 
            else:
                if key in ["a2", "b2", "l12", "c14", "c15", "laves"]:
                    phase_str += " "+value
                else:
                    phase_str += f" + {value}"
    
    # Check for oxides and other compounds
    oxide_patterns = [
        r'cro\d+',  # Match CrO3, CrO4, etc.
        r'al2o3',   # Match Al2O3
        r'(co-fe)7w6',  # Match (Co-Fe)7W6
        r'alni'     # Match AlNi
    ]
    
    for pattern in oxide_patterns:
        matches = re.findall(pattern, details.lower())
        for match in matches:
            compound = match.upper()
            if 'CRO' in compound:
                compound = f"CrO{compound[-1]}"
            elif 'AL2O3' in compound:
                compound = 'Al2O3'
            elif '(CO-FE)7W6' in compound:
                compound = '(Co-Fe)7W6'
            elif 'ALNI' in compound:
                compound = 'AlNi'
            phase_str += f" + {compound}"
    
    # Handle martensite
    if 'martensite' in details.lower():
        phase_str += ' martensite'
    
    # Handle specific element groupings
    if 'tivzr' in details.lower() and 'taw' in details.lower():
        phase_str += ' (TiVZr + TaW)'
    
    # Add intermetallic designation if needed
    if phase_type.lower() == 'intermetallic' and 'laves' not in phase_str.lower():
        phase_str += ' (Intermetallic)'
    
    return phase_str


def cd_to_csv(output_file: str, papers_names: list, names_list: list,  papers_jsons: list) -> None:
    """
    Args:
        output_file: name of the output file
        papers_names: list of paper names
        names_list: list of authors names
        papers_jsons: list of responses from LLM (each response contains a ```json block)
    Returns:
        Writes data to output2.csv
    """
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        headers = [
            'id', 'Paper', 'Name', 'Alloy', 'Nb of phase', 'Phase',
            'Experimental or theoretical', 'Experimental details',
            'Theoretical details', 'Special conditions', 'Type of solution'
        ]
        writer.writerow(headers)

        for i, json_data in enumerate(papers_jsons):
            # Extract JSON block from response
            try:
                if '```json' not in json_data:
                    json_data = json_data.split("```python")[1].split("```")[0]
                else:
                    json_data = json_data.split("```json")[1].split("```")[0]
            except (TypeError, IndexError, AttributeError) as e:
                print(f"No valid ```json block found in this paper's response {e}")
                print(json_data)
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
                no_solid_solution = False
                id = i
                paper = papers_names[i]
                name = names_list[i]
                alloy = alloy_data.get('chemical_formula', alloy_key)

                # Extract phases
                crystallographic_phases = alloy_data.get('crystallographic_phases', [])

                if len(crystallographic_phases) == 0:
                    crystallographic_phases = alloy_data.get('phases', [])

                
                phases = []
                for phase in crystallographic_phases:
                    phase_str = extract_phase_from_details(
                        phase.get('structure', ''),
                        phase.get('details', ''),
                        phase.get('phase_type', '')
                    )
                    if (phase_str) and (phase_str not in " ".join(phases)):
                        phases.append(phase_str)


                # Join phases and remove duplicates
                phase_str = ' + '.join(sorted(set(phases))) if phases else 'N/A'

                lower_phase_str = phase_str.lower().replace("-","")
                precipitates = alloy_data.get('precipitates', [])
                if len(precipitates) > 0:
                    for precipitate in precipitates:
                        if (type(precipitate) == str):
                            if (precipitate.lower() not in lower_phase_str):
                                phase_str += " + " + precipitate
                        elif precipitate.get("chemical_formula", "N/A").lower() not in lower_phase_str:
                            phase_str += " + " + precipitate.get("chemical_formula", "N/A")
                        else:
                            continue
                        

                nb_of_phase = phase_str.count("+") + 1 # len(crystalographic_phases)

                for structure in ["BCC", "FCC", "HCP"]:
                    if structure in phase_str:
                        no_solid_solution = False
                        break
                    no_solid_solution = True


                if "morphous" in phase_str and no_solid_solution:
                    type_of_solution = "Amorphous"
                elif no_solid_solution:
                    type_of_solution = "Intermetallic"
                else:
                    type_of_solution = alloy_data.get('phase_classification', 'N/A')

                # Determine if it's experimental, theoretical, or both
                exp_or_theo = 'N/A'
                experimental_details = 'N/A'
                theoretical_details = 'N/A'

                # Check for synthesis_or_calculation hui
                synthesis = alloy_data.get('synthesis_or_calculation', None)
                if synthesis:
                    exp_or_theo = synthesis.get('type', 'N/A')# .capitalize()
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
                            try:
                                experimental_details = ', '.join(detail_parts)
                            except TypeError:
                                dp = []
                                for a in detail_parts:
                                    dp.append(str(a))
                                experimental_details = ', '.join(dp)

                    if exp_or_theo in ['experimental', 'theoretical and experimental', "combination","both"]:
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

                row = [
                    id, paper, name, alloy, nb_of_phase, phase_str,
                    exp_or_theo, experimental_details,
                    theoretical_details, special_conditions, type_of_solution
                ]
                writer.writerow(row)

        print(f"Data has been successfully written to '{output_file}'")


if __name__ == "__main__":
    # This block remains as in your original code. Adjust the CSV input or filtering as needed.
    # df = pd.read_csv('/Users/vdc/result_multiple_prompts-batch-mds-1127-1.csv')#~/Downloads/esult_multiple_prompts-batch-mds-1127-1.csv')
    df = pd.read_csv('/Users/vdc/merged_data.csv')
    # df = pd.read_csv('/Users/vdc/jamba-1022.csv')# hea_llm_rag/shaping results/new-test-sample.csv')#
    # df = df.loc[df["context_missread_bug"] == True]
    # df = pd.read_csv('/Users/vdc/Downloads/deepseek-r1_results_right_dois_reordered.csv')
    cd_to_csv(
        output_file="merged_data_unnested.csv",
        papers_names=list(df["pdf_url"]), 
        names_list=list(df["article"]), 
        papers_jsons=list(df["prompt5"]), # list(df["prompt5"]),
    )