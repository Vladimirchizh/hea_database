system_prompt = """
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
"""

single_prompt = """
Identify each high entropy alloys discussed within the paper. For each high entropy alloy, determine the number of elements present and provide its chemical formula. Alphabetically sort the elements within the formula. When the formula uses variables like x and x - 1 to represent element proportions, ensure the model extracts the following clearly: Extract  values of x and link to formulas: for each value of x, generate the full chemical formula.
Example: For CoCrFeNiNbx alloys (x = 0, 0.103, 0.155, 0.206, 0.309, 0.412), list each formula as:
CoCrFeNiNb₀ (x = 0)
CoCrFeNiNb₀.₁₀₃ (x = 0.103), and so on.
For each high entropy alloy  identified, determine the crystallographic phases present. Describe the nature of each phase (e.g., amorphous, solid solution, intermetallic compound). Include chemical formula, crystallographic state, structure, and space group if available. Note any precipitates that may not be visible in X-Ray diffraction but are evident in micrography.
Determine whether the material was predicted theoretically, synthesized experimentally, or through a combination of both approaches. If theoretically predicted, specify the prediction method (e.g., Density Functional Theory, Phase Field modeling) and significant parameters used. If experimentally synthesized, provide details about the synthesis method (e.g., arc melting, spark plasma sintering) and relevant parameters such as temperature, pressure, time, etc. If both approaches were used, detail the theoretical prediction method first, followed by the experimental synthesis method. Also, specify any thermo-mechanical post-processing performed (e.g., annealing, quenching, rolling etc) and relevant parameters  (temperature, duration, cooling rate, reduction ratio etc), and whether all samples or only a subset underwent this treatment. For each stage (theoretical prediction, experimental synthesis, and post-processing), define the phases or structures obtained, highlighting changes across different stages of processing.
Identify if any alloy forms a partially ordered structure (classify as High Entropy Intermetallic). For studies focusing on the oxidation process, concentrate on the initial state of the alloy before oxidation.
Construct a response as a comprehensive JSON dictionary where each key represents a distinct alloy identified in the study.
For each key, create a nested dictionary that includes the fields:
Chemical_Formula: Alphabetically sorted chemical formula of the alloy.
Phases: List of dictionaries for each phase detailing type, formula, crystallographic state, structure, and space group.
Synthesis_Details: Method and parameters if synthesized experimentally.
Theoretical_Details: Calculation method and parameters if predicted theoretically.
Special_Conditions: Notable conditions like partial ordering or initial state before oxidation.
Phase_Classification: After extracting all information about the alloy's phases, classify the alloy as either:
"Single Solid Solution": If only one phase (FCC, BCC, or HCP) is present.
"Mixed Solution": If multiple phases are present (including any combination of solid solutions, precipitates, intermetallics, or other phases).
Ensure that each entry in the dictionary is filled with accurate and comprehensively extracted data based on the analysis of the text and figures.
Your task is to interpret and organize the information meticulously, ensuring clarity and accuracy in the data structure, to facilitate further analysis and research applications.
Example of dictionary:
{
"Alloy A": {
"chemical_formula": "AlCoCrFeNi",
"composition": {
"Al": 20,
"Co": 20,
"Cr": 20,
"Fe": 20,
"Ni": 20
},
"number_of_elements": 5,
"crystallographic_phases": [
{
"phase_type": "solid solution",
"chemical_formula": "AlCoCrFeNi",
"crystallographic_state": "crystalline",
"structure": "body-centered cubic",
"space_group": "Im-3m",
"detection_method": "XRD",
"details": "Single BCC phase observed"
}
],
"precipitates": [],
"synthesis_or_calculation": {
"type": "experimental",
"method": "arc melting",
"parameters": {
"temperature": 1600,
"time": "30 minutes"
}
},
"special_conditions": "None",
"phase_classification": "Single Solid Solution"
},
"Alloy B": {
"chemical_formula": "AlCoCrCuFeNi",
"composition": {
"Al": 16.67,
"Co": 16.67,
"Cr": 16.67,
"Cu": 16.67,
"Fe": 16.67,
"Ni": 16.67
},
"number_of_elements": 6,
"crystallographic_phases": [
{
"phase_type": "solid solution",
"chemical_formula": "AlCoCrFeNi",
"crystallographic_state": "crystalline",
"structure": "body-centered cubic",
"space_group": "Im-3m",
"detection_method": "XRD",
"details": "Primary BCC phase observed"
},
{
"phase_type": "solid solution",
"chemical_formula": "CuNi",
"crystallographic_state": "crystalline",
"structure": "face-centered cubic",
"space_group": "Fm-3m",
"detection_method": "XRD",
"details": "Secondary FCC phase rich in Cu and Ni"
}
],
"precipitates": [
{
"chemical_formula": "Ni3Al",
"detection_method": "TEM",
"details": "Nano-sized Ni3Al precipitates observed"
}
],
"synthesis_or_calculation": {
"type": "experimental",
"method": "arc melting",
"parameters": {
"temperature": 1550,
"time": "45 minutes"
}
},
"special_conditions": "None",
"phase_classification": "Mixed Solution"
}
}
"""
multiple_prompts = [
     """
Identify each high entropy alloys discussed within the paper (exclude alloys discussed in introduction or was cited as references). For each high entropy alloy, determine the number of elements present and provide its chemical formula. Alphabetically sort the elements within the formula. When the formula uses variables like x and x - 1 to represent element proportions, ensure the model extracts the following clearly: Extract values of x and link to formulas: for each value of x, generate the full chemical formula.
Example: For CoCrFeNiNbx alloys (x = 0, 0.103, 0.155, 0.206, 0.309, 0.412), list each formula as:
CoCrFeNiNb₀ (x = 0)
CoCrFeNiNb₀.₁₀₃ (x = 0.103), and so on.
Give the results for 1 to 12 most essential alloys you find in the paper, you're a language model with a maximum of output 4096 tokens, so you won't be able to generate more than 12 keys dictionary.
     """,
    "For each high entropy alloy identified earlier, determine the crystallographic phases present. Describe the nature of each phase (e.g., amorphous, solid solution, intermetallic compound). Include chemical formula, crystallographic state, structure, and space group if available. Note any precipitates that may not be visible in X-Ray diffraction but are evident in micrography.",
    "Determine whether the material was predicted theoretically, synthesized experimentally, or through a combination of both approaches. If theoretically predicted, specify the prediction method (e.g., Density Functional Theory, Phase Field modeling) and significant parameters used. If experimentally synthesized, provide details about the synthesis method (e.g., arc melting, spark plasma sintering) and relevant parameters such as temperature, pressure, time, etc. If both approaches were used, detail the theoretical prediction method first, followed by the experimental synthesis method. Also, specify any thermo-mechanical post-processing performed (e.g., annealing, quenching, rolling etc) and relevant parameters (temperature, duration, cooling rate, reduction ratio etc), and whether all samples or only a subset underwent this treatment. For each stage (theoretical prediction, experimental synthesis, and post-processing), define the phases or structures obtained, highlighting changes across different stages of processing.",
    "Identify if any alloy forms a partially ordered structure (classify as High Entropy Intermetallic). For studies focusing on the oxidation process, concentrate on the initial state of the alloy before oxidation (don’t take in consideration any alloys after oxidation).",
    '''
    Construct a comprehensive JSON dictionary where each key represents a distinct alloy identified in the study.
Give the results for 1 to 12 most essential alloys you find in the paper, you're a language model with a maximum of output 4096 tokens, so you won't be able to generate more than 12 keys dictionary.
For each key, create a nested dictionary that includes:
Chemical_Formula: Alphabetically sorted chemical formula of the alloy.
Phases: List of dictionaries for each phase detailing type, formula, crystallographic state, structure, and space group.
Synthesis_Details: Method and parameters if synthesized experimentally.
Theoretical_Details: Calculation method and parameters if predicted theoretically.
Special_Conditions: Notable conditions like partial ordering or initial state before oxidation.
Phase_Classification: After extracting all information about the alloy's phases, classify the alloy as either:
"Single Solid Solution": If only one phase (FCC, BCC, or HCP) is present.
"Mixed Solution": If multiple phases are present (including any combination of solid solutions, precipitates, intermetallics, or other phases).
Ensure that each entry in the dictionary is filled with accurate and comprehensively extracted data based on the analysis of the text and figures.
Your task is to interpret and organize the information meticulously, ensuring clarity and accuracy in the data structure, to facilitate further analysis and research applications.

Example of dictionary: 
```json
            {
            "Alloy A": {
            "chemical_formula": "AlCoCrFeNi",
            "composition": {
            "Al": 20,
            "Co": 20,
            "Cr": 20,
            "Fe": 20,
            "Ni": 20
            },
            "number_of_elements": 5,
            "crystallographic_phases": [
            {
            "phase_type": "solid solution",
            "chemical_formula": "AlCoCrFeNi",
            "crystallographic_state": "crystalline",
            "structure": "body-centered cubic",
            "space_group": "Im-3m",
            "detection_method": "XRD",
            "details": "Single BCC phase observed"
            }
            ],
            "precipitates": [],
            "synthesis_or_calculation": {
            "type": "experimental",
            "method": "arc melting",
            "parameters": {
            "temperature": 1600,
            "time": "30 minutes"
            }
            },
            "special_conditions": "None",
            "phase_classification": "Single Solid Solution"
            },
            "Alloy B": {
            "chemical_formula": "AlCoCrCuFeNi",
            "composition": {
            "Al": 16.67,
            "Co": 16.67,
            "Cr": 16.67,
            "Cu": 16.67,
            "Fe": 16.67,
            "Ni": 16.67
            },
            "number_of_elements": 6,
            "crystallographic_phases": [
            {
            "phase_type": "solid solution",
            "chemical_formula": "AlCoCrFeNi",
            "crystallographic_state": "crystalline",
            "structure": "body-centered cubic",
            "space_group": "Im-3m",
            "detection_method": "XRD",
            "details": "Primary BCC phase observed"
            },
            {
            "phase_type": "solid solution",
            "chemical_formula": "CuNi",
            "crystallographic_state": "crystalline",
            "structure": "face-centered cubic",
            "space_group": "Fm-3m",
            "detection_method": "XRD",
            "details": "Secondary FCC phase rich in Cu and Ni"
            }
            ],
            "precipitates": [
            {
            "chemical_formula": "Ni3Al",
            "detection_method": "TEM",
            "details": "Nano-sized Ni3Al precipitates observed"
            }
            ],
            "synthesis_or_calculation": {
            "type": "experimental",
            "method": "arc melting",
            "parameters": {
            "temperature": 1550,
            "time": "45 minutes"
            }
            },
            "special_conditions": "None",
            "phase_classification": "Mixed Solution"
            }
            }
            ```
    '''
]