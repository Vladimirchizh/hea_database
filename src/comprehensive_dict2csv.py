import json
import re
import csv
from json import JSONDecodeError
import pandas as pd
from rapidfuzz import fuzz, process


# ==================== Fuzzy Matching Utilities ====================

def fuzzy_match_dict(query: str, mapping: dict, threshold: int = 80) -> str | None:
    """
    Find the best fuzzy match for a query string in a dictionary's keys.
    
    Args:
        query: The string to match
        mapping: Dictionary with keys to match against
        threshold: Minimum similarity score (0-100) to consider a match
    
    Returns:
        The mapped value if a match is found, None otherwise
    """
    if not query:
        return None
    
    query_lower = query.lower()
    
    # First try exact match (fastest)
    for key in mapping:
        if key in query_lower:
            return mapping[key]
    
    # Fall back to fuzzy matching
    result = process.extractOne(
        query_lower,
        mapping.keys(),
        scorer=fuzz.partial_ratio,
        score_cutoff=threshold
    )
    
    if result:
        matched_key, score, _ = result
        return mapping[matched_key]
    
    return None


def fuzzy_contains(query: str, candidates: list[str], threshold: int = 85) -> bool:
    """
    Check if query fuzzy-matches any candidate in the list.
    
    Args:
        query: The string to check
        candidates: List of strings to match against
        threshold: Minimum similarity score (0-100)
    
    Returns:
        True if a fuzzy match is found
    """
    if not query or not candidates:
        return False
    
    query_lower = query.lower().replace("-", "").replace(" ", "")
    
    for candidate in candidates:
        candidate_clean = candidate.lower().replace("-", "").replace(" ", "")
        # Exact substring check first
        if candidate_clean in query_lower or query_lower in candidate_clean:
            return True
        # Fuzzy check
        if fuzz.ratio(query_lower, candidate_clean) >= threshold:
            return True
    
    return False


def fuzzy_match_type(query: str, type_variants: dict[str, list[str]], threshold: int = 80) -> str:
    """
    Match experimental/theoretical type strings with fuzzy matching.
    
    Args:
        query: The type string to classify
        type_variants: Dict mapping canonical type to list of variants
        threshold: Minimum similarity score
    
    Returns:
        The canonical type string, or 'N/A' if no match
    """
    if not query:
        return 'N/A'
    
    query_lower = query.lower().strip()
    
    for canonical, variants in type_variants.items():
        for variant in variants:
            if variant in query_lower:
                return canonical
            if fuzz.ratio(query_lower, variant) >= threshold:
                return canonical
    
    return query  # Return original if no match found


# Type classification variants for fuzzy matching
EXPERIMENTAL_VARIANTS = [
    'experimental', 'experiment', 'exp', 'synthesized', 'synthesis',
    'fabricated', 'prepared', 'measured', 'characterized'
]

THEORETICAL_VARIANTS = [
    'theoretical', 'theory', 'theo', 'calculated', 'calculation',
    'simulated', 'simulation', 'computed', 'computational', 'predicted', 'dft'
]

BOTH_VARIANTS = [
    'theoretical and experimental', 'experimental and theoretical',
    'combination', 'both', 'combined', 'theo+exp', 'exp+theo'
]

TYPE_VARIANTS = {
    'experimental': EXPERIMENTAL_VARIANTS,
    'theoretical': THEORETICAL_VARIANTS,
    'theoretical and experimental': BOTH_VARIANTS
}


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
    # First convert basic structure names using fuzzy matching
    base_structure = structure
    structure_mapping = {
        'body-centered cubic': 'BCC',
        'body centered cubic': 'BCC',
        'bcc': 'BCC',
        'face-centered cubic': 'FCC',
        'face centered cubic': 'FCC',
        'fcc': 'FCC',
        'hexagonal close-packed': 'HCP',
        'hexagonal close packed': 'HCP',
        'hexagonal': 'HCP',
        'hcp': 'HCP',
        'body-centered tetragonal': 'BCT',
        'body centered tetragonal': 'BCT',
        'bct': 'BCT'
    }
    
    # Use fuzzy matching for structure identification
    matched_structure = fuzzy_match_dict(structure, structure_mapping, threshold=75)
    if matched_structure:
        base_structure = matched_structure
    
    if not details:
        return base_structure
    
    # Check for specific phases in details
    details_lower = details.lower()
    structure_lower = structure.lower()
    phase_str = base_structure
    
    # Special phase indicators - separated by matching strategy
    # Short identifiers that need EXACT word boundary matching (not fuzzy)
    exact_match_phases = {
        'a2': 'A2',
        'b2': 'B2',
        'b19': 'B19',
        'l12': 'L12',
        'c14': 'C14',
        'c15': 'C15',
    }
    
    # Longer identifiers that can use fuzzy matching
    fuzzy_match_phases = {
        'cr2ta': 'Cr2Ta',
        'ti2ni': 'Ti2Ni',
        'spinel': 'Spinel',
        'laves': 'Laves',
        'laves phase': 'Laves',
        'amorphous': 'Amorphous',
        'sigma phase': 'Sigma',
        'sigma-phase': 'Sigma',
        'mu-phase': 'Mu',
        'mu phase': 'Mu',
        'dr+id': 'DR+ID',
    }
    
    # O-phase requires special handling - only match if explicitly mentioned
    # (not fuzzy, as "o" matches too many things like Co, Mo, No, etc.)
    o_phase_patterns = ['o-phase', 'o phase', 'orthorhombic phase']
    
    # Check for numbered variants (BCC1, BCC2, etc.)
    # if any(char.isdigit() for char in details):
    #     for i in range(1, 10):  # Check numbers 1-9
    #         if str(i) in details:
    #             phase_str = f"{base_structure}{i}"
    #             break
    
    # Detect phases using appropriate matching strategy
    primary_phases = ["a2", "b2", "l12", "c14", "c15", "laves"]
    detected_phases = []
    
    # Exact matching for short identifiers (word boundary aware)
    for key, value in exact_match_phases.items():
        # Use word boundary regex to avoid partial matches like "b2" in "nb2"
        pattern = r'\b' + re.escape(key) + r'\b'
        if re.search(pattern, details_lower) and not re.search(pattern, structure_lower):
            if not fuzzy_contains(key, [phase_str.lower()]):
                detected_phases.append((key, value))
    
    # Fuzzy matching only for longer, unambiguous identifiers
    for key, value in fuzzy_match_phases.items():
        # Require higher threshold and minimum length match
        if len(key) >= 5 and fuzz.partial_ratio(key, details_lower) >= 90:
            if not fuzzy_contains(value, [structure_lower, phase_str.lower()]):
                detected_phases.append((key, value))
        elif key in details_lower:  # Exact fallback for shorter ones
            if not fuzzy_contains(value, [structure_lower, phase_str.lower()]):
                detected_phases.append((key, value))
    
    # Special handling for O-phase - exact match only
    for pattern in o_phase_patterns:
        if pattern in details_lower:
            if 'O-phase' not in phase_str:
                detected_phases.append(('o-phase', 'O-phase'))
            break
    
    # Process detected phases in order, avoiding duplicates
    added_values = set()
    for key, value in detected_phases:
        if value not in added_values:
            added_values.add(value)
            if phase_str == base_structure:
                phase_str += " " + value
            else:
                if key in primary_phases:
                    phase_str += " " + value
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
        matches = re.findall(pattern, details_lower)
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
    
    # Handle martensite with fuzzy matching
    martensite_variants = ['martensite', 'martensitic', 'martensite phase']
    if any(fuzz.partial_ratio(var, details_lower) >= 85 for var in martensite_variants):
        phase_str += ' martensite'
    
    # Handle specific element groupings
    if 'tivzr' in details_lower and 'taw' in details_lower:
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
                    # Use fuzzy matching to avoid duplicate phases
                    if phase_str and not fuzzy_contains(phase_str, phases, threshold=80):
                        phases.append(phase_str)


                # Join phases and remove duplicates
                phase_str = ' + '.join(sorted(set(phases))) if phases else 'N/A'

                # Use fuzzy matching for precipitate duplicate detection
                lower_phase_str = phase_str.lower().replace("-","")
                existing_phases = [p.strip() for p in phase_str.split('+')]
                precipitates = alloy_data.get('precipitates', [])
                if len(precipitates) > 0:
                    for precipitate in precipitates:
                        precip_formula = None
                        if isinstance(precipitate, str):
                            precip_formula = precipitate
                        elif isinstance(precipitate, dict):
                            precip_formula = precipitate.get("chemical_formula", None)
                        
                        if precip_formula:
                            # Fuzzy check against existing phases
                            if not fuzzy_contains(precip_formula, existing_phases, threshold=80):
                                phase_str += " + " + precip_formula
                                existing_phases.append(precip_formula)
                        

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

                # Check for synthesis_or_calculation
                synthesis = alloy_data.get('synthesis_or_calculation', None)
                if synthesis:
                    raw_type = synthesis.get('type', 'N/A')
                    # Use fuzzy matching to normalize the type
                    exp_or_theo = fuzzy_match_type(raw_type, TYPE_VARIANTS)
                    method = synthesis.get('method', '')
                    parameters = synthesis.get('parameters', {})
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

                    if exp_or_theo in ['experimental', 'theoretical and experimental']:
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
                            
                    if exp_or_theo in ['theoretical', 'theoretical and experimental']:
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
        output_file="database_of_HEA_fuzz.csv",
        papers_names=list(df["pdf_url"]), 
        names_list=list(df["article"]), 
        papers_jsons=list(df["prompt5"]), # list(df["prompt5"]),
    )