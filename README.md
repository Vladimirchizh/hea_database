# High Entropy Alloys (HEA) Database Documentation

This repository contains two main datasets related to High Entropy Alloys (HEAs):

## 1. Database of HEAs (`database_of_HEAs.csv`)

This dataset contains detailed information about various High Entropy Alloys, including their composition, phase structure, and experimental/theoretical details.

### Dataset Structure:
- **id**: Unique identifier for each entry
- **Paper**: Source paper identifier
- **Name**: Name of the paper file
- **Alloy**: Chemical composition of the HEA
- **Nb of phase**: Number of phases present
- **Phase**: Phase structure (e.g., BCC, FCC, etc.)
- **Experimental or theoretical**: Classification of the study type
- **Experimental details**: Detailed experimental procedure
- **Theoretical details**: Theoretical methods used (if applicable)
- **Special conditions**: Any special conditions or notes
- **Type of solution**: Classification of the solution type

### Example Entry:

| Field | Value |
|-------|-------|
| Alloy | AlCoCrFeNi |
| Phases | BCC B2 + FCC L12 |
| Type | Experimental |
| Experimental Details | vacuum arc melting, Purity: >= 99.98 wt%, Repetition: at least 5 times |
| Special Conditions | Partially ordered structure, classified as High Entropy Intermetallic |
| Type of Solution | Mixed Solution |

## 2. Database of Raw Responses (`database_of_raw_responses.csv`)

This dataset contains the raw responses and extracted information from scientific papers about HEAs.

### Dataset Structure:
- **article**: Article identifier
- **pdf_url**: URL to the PDF file
- **prompt1-5**: Different prompts used for data extraction
- **context_missread_bug**: Any context reading issues
- **reference**: Reference information
- **source**: Source of the data
- **URL**: URL to the source
- **compound**: Compound information

## Usage

These datasets can be used for:
1. Studying the composition and properties of various HEAs
2. Analyzing experimental procedures and conditions
3. Understanding phase structures and their relationships
4. Research in materials science and metallurgy
5. Machine learning applications in materials discovery

## Data Format

Both datasets are provided in CSV format, making them easily accessible for:
- Data analysis using Python (pandas)
- Statistical analysis
- Machine learning applications
- Database integration

## File Sizes
- `database_of_HEAs.csv`: 3.4MB
- `database_of_raw_responses.csv`: 58MB
