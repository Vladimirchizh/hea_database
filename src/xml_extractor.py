
from os import listdir
from os.path import isfile, join

import lxml.etree as ET

def extract_namespaces(xml_file):
    """
    Extract all namespaces from the XML file and create a prefix-to-namespace mapping.
    """
    events = ("start", "start-ns")
    ns_map = {}
    for event, elem in ET.iterparse(xml_file, events):
        if event == "start-ns":
            prefix, uri = elem
            ns_map[prefix] = uri
        else:
            break  # Only need to parse the root element for namespaces
    return ns_map

def extract_text(element):
    """
    Recursively extract text content from an XML element, including tail texts.
    """
    texts = []
    if element.text:
        texts.append(element.text)
    for child in element:
        texts.append(extract_text(child))
        if child.tail:
            texts.append(child.tail)
    return ''.join(texts)

def extract_article_content(xml_file):
    # Parse the namespaces dynamically
    namespaces = extract_namespaces(xml_file)

    # Re-parse the XML file to get the root element
    parser = ET.XMLParser(remove_blank_text=True)
    tree = ET.parse(xml_file, parser)
    root = tree.getroot()

    # Update namespaces with default namespace (if any)
    default_ns = root.nsmap.get(None)
    if default_ns:
        namespaces['default'] = default_ns

    # Extract core data
    coredata = root.find('.//{%s}coredata' % namespaces.get('default', ''), namespaces)
    if coredata is None:
        print("No coredata found in the XML.")
        return None

    title = coredata.find('.//{%s}title' % namespaces.get('dc', ''), namespaces)
    doi = coredata.find('.//{%s}doi' % namespaces.get('prism', ''), namespaces)
    publication_name = coredata.find('.//{%s}publicationName' % namespaces.get('prism', ''), namespaces)
    publication_date = coredata.find('.//{%s}coverDate' % namespaces.get('prism', ''), namespaces)
    description_element = coredata.find('.//{%s}description' % namespaces.get('dc', ''), namespaces)
    description = extract_text(description_element).strip() if description_element is not None else ''

    # Extract the article body
    original_text = root.find('.//{%s}originalText' % namespaces.get('default', ''), namespaces)
    if original_text is None:
        print("No originalText found in the XML.")
        return None

    doc = original_text.find('.//{%s}doc' % namespaces.get('xocs', ''), namespaces)
    if doc is None:
        print("No doc found in originalText.")
        return None

    serial_item = doc.find('.//{%s}serial-item' % namespaces.get('xocs', ''), namespaces)
    if serial_item is None:
        print("No serial-item found in doc.")
        return None

    article = serial_item.find('.//{%s}article' % namespaces.get('ja', ''), namespaces)
    if article is None:
        print("No article found in serial-item.")
        return None

    body = article.find('.//{%s}body' % namespaces.get('ja', ''), namespaces)
    if body is None:
        print("No body found in article.")
        return None

    # Initialize content
    article_content = ""

    # Iterate over sections and paragraphs
    for section in body.findall('.//{%s}section' % namespaces.get('ce', ''), namespaces):
        # Extract section title
        section_title_element = section.find('.//{%s}section-title' % namespaces.get('ce', ''), namespaces)
        if section_title_element is not None:
            section_title = extract_text(section_title_element).strip()
            if section_title:
                article_content += f"\n\n{section_title}\n"

        # Extract paragraphs within the section
        for para in section.findall('.//{%s}para' % namespaces.get('ce', ''), namespaces):
            # Collect all text within the paragraph, including nested tags
            para_text = extract_text(para).strip()
            if para_text:
                article_content += f"\n{para_text}"

    # Compile all extracted information
    article_data = {
        'title': title.text.strip() if title is not None else '',
        'doi': doi.text.strip() if doi is not None else '',
        'publication_name': publication_name.text.strip() if publication_name is not None else '',
        'publication_date': publication_date.text.strip() if publication_date is not None else '',
        'abstract': description,
        'content': article_content.strip()
    }

    return article_data

# Usage example
if __name__ == "__main__":
    # xml_file_path = 'elsevier/10.1016-j.wear.2020.203583.xml'  # Replace with your actual file path
    mypath = "elsevier"
    yes, no = 0, 0
    for xml_file_path in [f for f in listdir(mypath) if isfile(join(mypath, f))]:

        article_data = extract_article_content(join(mypath, xml_file_path))

        if article_data:
            # Print the extracted content
            print("Title:", article_data['title'])
            print("DOI:", article_data['doi'])
            print("Publication Name:", article_data['publication_name'])
            print("Publication Date:", article_data['publication_date'])
            print("\nAbstract:", article_data['abstract'])
            # print("\nArticle Content:", article_data['content'])

            # Save the article content to a text file
            output_file_path = xml_file_path.replace(".xml", ".txt")
            with open(join("elsevier_txts" ,output_file_path), 'w', encoding='utf-8') as f:
                f.write(f"Title: {article_data['title']}\n")
                f.write(f"DOI: {article_data['doi']}\n")
                f.write(f"Publication Name: {article_data['publication_name']}\n")
                f.write(f"Publication Date: {article_data['publication_date']}\n\n")
                f.write(f"Abstract:\n{article_data['abstract']}\n\n")
                f.write(f"Article Content:\n{article_data['content']}\n")
            yes+=1
            print(f"\nArticle content has been saved to '{output_file_path}'.")
        else:
            print("Failed to extract article data.")
            print(xml_file_path)
            no+=1
    print(f"converted: {yes}") # converted: 4626
    print(f"failed {no}") # failed 94
