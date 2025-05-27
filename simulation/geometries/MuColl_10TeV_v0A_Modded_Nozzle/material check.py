import xml.etree.ElementTree as ET

def load_materials(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    materials = {}
    for material in root.findall('material'):
        name = material.get('name')
        materials[name] = material
    return materials

materials = load_materials('/scratch/devlinjenkins/work/simulation/geometries/MuColl_10TeV_v0A_mod/materials.xml')
print(f"Loaded materials: {list(materials.keys())}")

material_name = 'CustomMat'
if material_name in materials:
    bch2_material = materials[material_name]
    print(f"Material {material_name} found with density {bch2_material.find('D').get('value')} g/cm3")
else:
    print(f"Material {material_name} not found")
