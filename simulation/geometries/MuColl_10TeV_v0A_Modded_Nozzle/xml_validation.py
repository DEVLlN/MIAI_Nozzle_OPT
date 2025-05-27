import xml.etree.ElementTree as ET

def validate_xml(file_path):
    try:
        tree = ET.parse(file_path)
        print("XML is well-formed.")
    except ET.ParseError as e:
        print(f"XML is not well-formed: {e}")

validate_xml('/scratch/devlinjenkins/work/simulation/geometries/MuColl_10TeV_v0A_mod/materials.xml')
