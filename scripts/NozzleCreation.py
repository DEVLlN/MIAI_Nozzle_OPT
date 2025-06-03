import os
import shutil

# Output directory
output_dir = "nozzle_killzone_scaled"
os.makedirs(output_dir, exist_ok=True)

# Geometry bounds and steps
z_start, z_end = 6.0, 600.0
r_start, r_end = 50.0, 1.78
num_steps = 100
z_step = (z_end - z_start) / (num_steps - 1)
r_step = (r_start - r_end) / (num_steps - 1)

# Template constants
beam_pipe_rmin = 0.3
nozzle_rmax = 2.59223
zplanes_all = [
    ("tip", 6.0, 2.49223),
    ("kink1", 100.0, 13.53),
    ("kink2", 100.0, 11.0),
    ("z200", 200.0, 13.0),
    ("z600", 600.0, 50.0)
]
z_rmin_defaults = {
    6.0: 0.3,
    100.0: 0.3,
    200.0: 0.596,
    600.0: 1.78
}

# XML templates
base_template = """<lccdd>
  <define>
    <constant name="Nozzle_kink_z" value="100*cm"/>
  </define>
  <display>
    <vis name="NozzleWVis" alpha="1.0" r="0.0" g="1.0" b="1.0" showDaughters="false" visible="true"/>
    <vis name="NozzleKillZoneVis" alpha="1.0" r="1.0" g="1.0" b="1.0" showDaughters="false" visible="true"/>
    <vis name="NozzleBCHVis" alpha="0.3" r="1.0" g="1.0" b="1.0" showDaughters="false" visible="false"/>
  </display>
  <detectors>
    {killzone_block}
    {nozzle_block}
    {bch_block}
  </detectors>
</lccdd>
"""

bch_block = """
<detector name="NozzleBCH_right" type="DD4hep_PolyconeSupport" vis="NozzleBCHVis" region="NozzleRegion">
  <material name="BCH2"/>
  <zplane z="Nozzle_kink_z" rmin="15*cm" rmax="17.63*cm" />
  <zplane z="200*cm" rmin="17*cm" rmax="26.104*cm" />
  <zplane z="Nozzle_zmax" rmin="50*cm" rmax="60*cm" />
</detector>
<detector name="NozzleBCH_left" type="DD4hep_PolyconeSupport" vis="NozzleBCHVis" region="NozzleRegion">
  <material name="BCH2"/>
  <zplane z="-Nozzle_kink_z" rmin="15*cm" rmax="17.63*cm" />
  <zplane z="-200*cm" rmin="17*cm" rmax="26.104*cm" />
  <zplane z="-Nozzle_zmax" rmin="50*cm" rmax="60*cm" />
</detector>
"""

def make_killzone(z_front, rmax_dict):
    def block(side):
        sign = "" if side == "right" else "-"
        lines = [f'  <detector name="NozzleKillZone_{side}" type="DD4hep_PolyconeSupport" vis="NozzleKillZoneVis" region="NozzleRegion" limits="NozzleRegionLimitSet">\n    <material name="Tungsten"/>']
        for name, z, rmax in zplanes_all:
            if z >= z_front:
                rmin = z_rmin_defaults[z]
                rmax_val = rmax_dict[name]
                lines.append(f'    <zplane z="{sign}{z:.2f}*cm" rmin="{rmin:.3f}*cm" rmax="{rmax_val:.5f}*cm"/>')
        lines.append("  </detector>")
        return "\n".join(lines)
    return block("right") + "\n" + block("left")

def make_nozzle(z, rmin):
    def block(side):
        sign = "" if side == "right" else "-"
        return f"""
<detector name="NozzleW_{side}" type="DD4hep_PolyconeSupport" vis="NozzleWVis" region="NozzleRegion">
  <material name="Tungsten"/>
  <zplane z="{sign}{z:.2f}*cm" rmin="{rmin:.5f}*cm" rmax="{nozzle_rmax}*cm"/>
  <zplane z="{sign}Nozzle_kink_z" rmin="{rmin:.5f}*cm" rmax="17.63*cm"/>
  <zplane z="{sign}Nozzle_kink_z" rmin="{rmin:.5f}*cm" rmax="15*cm"/>
  <zplane z="{sign}200*cm" rmin="{rmin:.5f}*cm" rmax="17*cm"/>
  <zplane z="{sign}600*cm" rmin="{rmin:.5f}*cm" rmax="50*cm"/>
</detector>"""
    return block("right") + block("left")

# Initial rmax per zplane
rmax_dict = {name: r for name, _, r in zplanes_all}
z = z_start
z_front = z_start

for step in range(num_steps):
    r = max(r_end, r_start - step * r_step)
    z_front = z_start + step * z_step
    killzone_block = make_killzone(z_front, rmax_dict)
    nozzle_block = make_nozzle(z, r)
    xml_content = base_template.format(
        killzone_block=killzone_block,
        nozzle_block=nozzle_block,
        bch_block=bch_block
    )

    fname = f"nozzle_rstep{step:03}_rdepth{r:.2f}_zdepth{z_front:.2f}_zstep{step:03}.xml"
    subdir = os.path.join(output_dir, os.path.splitext(fname)[0])
    os.makedirs(subdir, exist_ok=True)
    full_path = os.path.join(subdir, fname)
    with open(full_path, "w") as f:
        f.write(xml_content)

    # Copy supporting files
    static_dir = "/home/devlinjenkins/projects/NozzleSimOpti/simulation/geometries/MuColl_10TeV_v0A"
    for file in os.listdir(static_dir):
        if "MuColl_10TeV_v0A" in file:
            continue
        shutil.copy2(os.path.join(static_dir, file), subdir)

    xml_src = "/home/devlinjenkins/projects/NozzleSimOpti/simulation/geometries/MuColl_10TeV_v0A_Modded_Nozzle/MuColl_10TeV_ex.xml"
    xml_dst = os.path.join(subdir, "MuColl_10TeV_ex.xml")
    shutil.copy2(xml_src, xml_dst)

    with open(xml_dst, "r") as f:
        lines = f.readlines()
    if len(lines) >= 197:
        lines[196] = f'    <include ref="{fname}"/>\n'
    with open(xml_dst, "w") as f:
        f.writelines(lines)

    # Shrink rmax values
    for key in rmax_dict:
        min_r = z_rmin_defaults[[z for n, z, _ in zplanes_all if n == key][0]]
        rmax_dict[key] = max(min_r, rmax_dict[key] - r_step)