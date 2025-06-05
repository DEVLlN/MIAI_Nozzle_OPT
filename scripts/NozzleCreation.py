import xml.etree.ElementTree as ET
import copy
import os
import shutil

# Initial XML structure
initial_xml = '''<lccdd>
    <!--  Definition of global dictionary constants          -->
    <define>
        <constant name="Nozzle_kink_z"  value="100*cm"/>
    </define>
    
    <!--  Definition of the used visualization attributes    -->
    <display>
        <vis name="NozzleWVis" alpha="1.0" r="0.0" g="1.0" b="1.0" showDaughters="false" visible="true"/>
        <vis name="NozzleBCHVis" alpha="1.0" r="0.3" g="1.0" b="1.0" showDaughters="false" visible="true"/>
    </display>
    
    
    <detectors>
        <comment>Nozzle</comment>
        
        <detector name="NozzleW_right" type="DD4hep_PolyconeSupport" vis="NozzleWVis" region="NozzleRegion">
            <comment>Internal part of the nozzle: Tungsten</comment>
            <material name="Tungsten"/>
            <zplane z="Nozzle_zmin" rmin="1*cm" rmax="1*cm" />
            <zplane z="15*cm" rmin="0.6*cm" rmax="2.59223*cm" />
            <zplane z="Nozzle_kink_z" rmin="0.3*cm" rmax="17.63*cm" />
            <zplane z="Nozzle_kink_z" rmin="0.3*cm" rmax="15*cm" />
            <zplane z="200*cm" rmin="0.596*cm" rmax="17*cm" />
            <zplane z="600*cm" rmin="1.78*cm" rmax="50*cm" />
        </detector>


        <detector name="NozzleW_left" type="DD4hep_PolyconeSupport" vis="NozzleWVis" region="NozzleRegion">
            <comment>Internal part of the nozzle: Tungsten</comment>
            <material name="Tungsten"/>
            <zplane z="-Nozzle_zmin" rmin="1*cm" rmax="1*cm" />
            <zplane z="-15*cm" rmin="0.6*cm" rmax="2.59223*cm" />
            <zplane z="-Nozzle_kink_z" rmin="0.3*cm" rmax="17.63*cm" />
            <zplane z="-Nozzle_kink_z" rmin="0.3*cm" rmax="15*cm" />
            <zplane z="-200*cm" rmin="0.596*cm" rmax="17*cm" />
            <zplane z="-Nozzle_zmax" rmin="1.78*cm" rmax="50*cm" />
        </detector>


        <detector name="NozzleBCH_right" type="DD4hep_PolyconeSupport" vis="NozzleBCHVis" region="NozzleRegion">
            <comment>Outer part of the nozzle: Borated Polyehtylene</comment>
            <material name="BCH2"/>
            <zplane z="Nozzle_kink_z" rmin="15*cm" rmax="17.63*cm" />
            <zplane z="200*cm" rmin="17*cm" rmax="26.104*cm" />
            <zplane z="Nozzle_zmax" rmin="50*cm" rmax="60*cm" />
        </detector>


        <detector name="NozzleBCH_left" type="DD4hep_PolyconeSupport" vis="NozzleBCHVis" region="NozzleRegion">
            <comment>Outer part of the nozzle: Borated Polyehtylene</comment>
            <material name="BCH2"/>
            <zplane z="-Nozzle_kink_z" rmin="15*cm" rmax="17.63*cm" />
            <zplane z="-200*cm" rmin="17*cm" rmax="26.104*cm" />
            <zplane z="-Nozzle_zmax" rmin="50*cm" rmax="60*cm" />
        </detector>


    </detectors>
</lccdd>'''

# Parse the initial XML
root = ET.fromstring(initial_xml)

# Helper: get zplanes as dicts for nozzle and killzone
def get_zplane_dict(detector_elem, attr):
    return { float(zp.attrib['z']): float(zp.attrib[attr]) for zp in detector_elem.findall('zplane') }

nozzle_elem = root.find('nozzle')
killzone_elem = root.find('killzone')

# Dictionaries for each zplane
nozzle_rmin_dict = get_zplane_dict(nozzle_elem, 'rmin')
killzone_rmax_dict = get_zplane_dict(killzone_elem, 'rmax')
killzone_rmin_dict = get_zplane_dict(killzone_elem, 'rmin')

# Use sorted z values for consistent order
zvals = sorted(nozzle_rmin_dict.keys())

# For each zplane, track current values and targets
current_nozzle_rmin = nozzle_rmin_dict.copy()
current_killzone_rmax = killzone_rmax_dict.copy()
target_killzone_rmax = killzone_rmin_dict.copy()

# Determine max number of iterations for any zplane
def steps_for_z(z):
    return int(round(killzone_rmax_dict[z] - killzone_rmin_dict[z]))
max_steps = max([steps_for_z(z) for z in zvals])

# Output directory (optional)
output_dir = '.'
os.makedirs(output_dir, exist_ok=True)

for step in range(max_steps + 1):
    # Deepcopy the root to modify for this iteration
    new_root = copy.deepcopy(root)
    # Update nozzle and killzone zplanes
    for volume in ['nozzle', 'killzone']:
        det_elem = new_root.find(volume)
        for zp in det_elem.findall('zplane'):
            z = float(zp.attrib['z'])
            # Only update for nozzle and killzone
            if volume == 'nozzle':
                target_rmin = killzone_rmin_dict[z]
                current_rmin = nozzle_rmin_dict[z] + step
                if current_rmin > target_rmin:
                    current_rmin = target_rmin  # freeze at target
                zp.set('rmin', f"{current_rmin:.1f}")
            elif volume == 'killzone':
                target_rmax = killzone_rmin_dict[z]
                current_rmax = killzone_rmax_dict[z] - step
                if current_rmax < target_rmax:
                    current_rmax = target_rmax  # freeze at target
                zp.set('rmax', f"{current_rmax:.1f}")
    # BCH left unchanged
    # Create a subdirectory for each step
    step_dir = os.path.join(output_dir, f"step_{step:03d}")
    os.makedirs(step_dir, exist_ok=True)
    fname = os.path.join(step_dir, f"NozzleIter_{step:03d}.xml")
    # Path to base geometry directory
    base_geom_dir = "/home/devlinjenkins/projects/NozzleSimOpti/simulation/geometries/MuColl_10TeV_v0A"
    for file in os.listdir(base_geom_dir):
        if file not in {"Nozzle_10deg_v0.xml", "MuColl_10TeV_v0A.xml"}:
            shutil.copy(os.path.join(base_geom_dir, file), step_dir)
    tree = ET.ElementTree(new_root)
    tree.write(fname, encoding="utf-8", xml_declaration=True)

    # Write modified MuColl file to the same step directory
    original_mucoll_path = os.path.join(base_geom_dir, "MuColl_10TeV_v0A.xml")
    mucoll_path = os.path.join(step_dir, "MuColl_10TeV_v0A.xml")

    with open(original_mucoll_path, "r") as f:
        mucoll_contents = f.read()

    # Replace the Nozzle include line with the current iteration's nozzle
    updated_mucoll = mucoll_contents.replace(
        '<include ref=""/>  <!-- Nozzle.xml, replace with current version before sim-->',
        f'<include ref="NozzleIter_{step:03d}.xml"/>'
    )

    with open(mucoll_path, "w") as f:
        f.write(updated_mucoll)