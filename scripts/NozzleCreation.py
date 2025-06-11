import os
import shutil
from itertools import product

# Parameters
output_dir = "generated_nozzles"
skin_depth_values = [1.0 * i for i in range(1, 3)]  # [1.0, 2.0] cm
distance_from_tip_values = [1.0 * i for i in range(1, 7)]  # [1.0, ..., 6.0] cm
template_dir = "/home/devlinjenkins/projects/NozzleSimOpti/simulation/geometries/MAIA_v0_Blackhole"
exclude_files = {"Nozzle_10deg_skindepth_1.xml", "MAIA_v0_blackhole.xml"}

# Geometry data for zplanes (z, rmin of blackhole)
zplanes = [
    (6.0, 1.0),
    (10.5176, 0.79922),
    (15.0, 0.6),
    (99.99999999, 0.3),
    (100.0, 0.3),  # Nozzle_kink_z
    (204.48824, 0.6124092832),
    (595.0, 1.78),
]

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

for sd, dt in product(skin_depth_values, distance_from_tip_values):
    tip_z = 10.5176 - dt
    subfolder_name = f"sd{sd:.2f}_dt{dt:.2f}"
    subfolder_path = os.path.join(output_dir, subfolder_name)
    os.makedirs(subfolder_path, exist_ok=True)

    # Copy all static template files
    for fname in os.listdir(template_dir):
        if fname not in exclude_files:
            shutil.copy(os.path.join(template_dir, fname), subfolder_path)

    # Build dynamic geometry XML
    def zplane_entry(z, rmin, rmax):
        return f'<zplane z="{z:.8f}*cm" rmin="{rmin:.8f}*cm" rmax="{rmax:.8f}*cm" />'

    nozzle_right = []
    nozzle_left = []
    blackhole_right = []
    blackhole_left = []

    for z, bh_rmin in zplanes:
        bh_rmax = bh_rmin
        nozzle_rmin = bh_rmax
        nozzle_rmax = nozzle_rmin + sd

        # Adjust tip_z step if it matches this z-plane
        if abs(z - tip_z) < 1e-4:
            bh_rmax = bh_rmin
            nozzle_rmin = bh_rmax
            nozzle_rmax = nozzle_rmin + sd

        blackhole_right.append(zplane_entry(z, bh_rmin, bh_rmax))
        blackhole_left.append(zplane_entry(-z, bh_rmin, bh_rmax))
        nozzle_right.append(zplane_entry(z, nozzle_rmin, nozzle_rmax))
        nozzle_left.append(zplane_entry(-z, nozzle_rmin, nozzle_rmax))

    # Static BCH and cludding
    bch = [
        '<zplane z="Nozzle_kink_z" rmin="13.48473619*cm" rmax="13.57473619*cm" />',
        '<zplane z="204.48824*cm" rmin="13.48473619*cm" rmax="21.3958448184*cm" />',
        '<zplane z="595*cm" rmin="43.01*cm" rmax="51*cm" />'
    ]

    clud = [
        '<zplane z="Nozzle_kink_z" rmin="13.57473619*cm" rmax="17.57473619*cm" />',
        '<zplane z="595*cm" rmin="51*cm" rmax="55*cm" />'
    ]

    # Construct full XML content
    geometry = f"""<lccdd>
    <define>
        <constant name="Nozzle_kink_z"  value="100*cm"/>
        <constant name="Nozzle_kink_max_r"  value="17.57473619*cm"/>
    </define>
    <display>
        <vis name="NozzleBlackHoleVis" alpha="1.0" r="0.53" g="0.12" b="0.47" showDaughters="true" visible="true"/>
        <vis name="NozzleWVis" alpha="1.0" r="0.0" g="1.0" b="1.0" showDaughters="true" visible="true"/>
        <vis name="NozzleBCHVis" alpha="1.0" r="1.0" g="0.0" b="0.0" showDaughters="true" visible="true"/>
    </display>

    <detectors>
        <detector name="NozzleBlackhole_right" type="DD4hep_PolyconeSupport" vis="NozzleBlackHoleVis" region="NozzleRegion" limits="blackhole_limit">
            <material name="Tungsten_Alloy"/>
            {'\n            '.join(blackhole_right)}
        </detector>

        <detector name="NozzleBlackhole_left" type="DD4hep_PolyconeSupport" vis="NozzleBlackHoleVis" region="NozzleRegion" limits="blackhole_limit">
            <material name="Tungsten_Alloy"/>
            {'\n            '.join(blackhole_left)}
        </detector>

        <detector name="NozzleW_right" type="DD4hep_PolyconeSupport" vis="NozzleWVis" region="NozzleRegion">
            <material name="Tungsten_Alloy"/>
            {'\n            '.join(nozzle_right)}
        </detector>

        <detector name="NozzleW_left" type="DD4hep_PolyconeSupport" vis="NozzleWVis" region="NozzleRegion">
            <material name="Tungsten_Alloy"/>
            {'\n            '.join(nozzle_left)}
        </detector>

        <detector name="NozzleBCH_right" type="DD4hep_PolyconeSupport" vis="NozzleBCHVis" region="NozzleRegion">
            <material name="BCH2"/>
            {'\n            '.join(bch)}
        </detector>

        <detector name="NozzleBCH_left" type="DD4hep_PolyconeSupport" vis="NozzleBCHVis" region="NozzleRegion">
            <material name="BCH2"/>
            {'\n            '.join(bch).replace('z="', 'z="-')}
        </detector>

        <detector name="NozzleWCludding_right" type="DD4hep_PolyconeSupport" vis="NozzleWVis" region="NozzleRegion">
            <material name="Tungsten_Alloy"/>
            {'\n            '.join(clud)}
        </detector>

        <detector name="NozzleWCludding_left" type="DD4hep_PolyconeSupport" vis="NozzleWVis" region="NozzleRegion">
            <material name="Tungsten_Alloy"/>
            {'\n            '.join(clud).replace('z="', 'z="-')}
        </detector>
    </detectors>
</lccdd>"""

    # Save the XML geometry
    xml_path = os.path.join(subfolder_path, f"nozzle_sd{sd:.2f}_dt{dt:.2f}.xml")
    with open(xml_path, "w") as f:
        f.write(geometry)

    print(f"✅ Generated: {xml_path} (skin depth: {sd} cm, distance from tip: {dt} cm)")