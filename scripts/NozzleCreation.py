import os
import xml.etree.ElementTree as ET

# Configuration
template_file = "/home/devlinjenkins/projects/NozzleSimOpti/simulation/geometries/MuColl_10TeV_v0A_Modded_Nozzle/Nozzle_10deg_STEP.xml"
output_dir = "generated_nozzles"
os.makedirs(output_dir, exist_ok=True)

# Step settings
initial_r = 17.63  # starting at outer radius in cm
r_step = -0.1      # inward radius step in cm
z_right_start = 6.0  # right-side nozzle killzone starts at z=6 cm
z_left_start = -6.0  # left-side nozzle killzone starts at z=-6 cm
z_step = 1.0         # step back in z each iteration (1 cm more away from tip)

num_steps = 50

for i in range(num_steps):
    r_bh = initial_r + i * r_step
    z_right = z_right_start + i * z_step
    z_left = z_left_start - i * z_step

    # Parse the XML
    tree = ET.parse(template_file)
    root = tree.getroot()

    # Iterate over detectors
    for det in root.findall(".//detector"):
        name = det.attrib.get("name", "")
        for zp in det.findall("zplane"):
            z_val = zp.attrib["z"]
            # Match the kink zplanes
            if "Nozzle_kink_z" in z_val or z_val == "100*cm":
                if "KillZone_right" in name:
                    zp.set("rmax", f"{r_bh:.5f}")
                    zp.set("z", f"{z_right:.5f}*cm")
                elif "KillZone_left" in name:
                    zp.set("rmax", f"{r_bh:.5f}")
                    zp.set("z", f"{z_left:.5f}*cm")
                elif "NozzleW_right" in name:
                    zp.set("rmin", f"{r_bh:.5f}")
                    zp.set("z", f"{z_right:.5f}*cm")
                elif "NozzleW_left" in name:
                    zp.set("rmin", f"{r_bh:.5f}")
                    zp.set("z", f"{z_left:.5f}*cm")

    # Save the modified XML
    filename = f"nozzle_r{r_bh:.2f}_z{z_right:.2f}.xml"
    output_path = os.path.join(output_dir, filename)
    tree.write(output_path)
    print(f"Generated: {output_path}")