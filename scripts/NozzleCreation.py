import xml.etree.ElementTree as ET
import os
import shutil
import numpy as np
from itertools import product
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ================================
# CONFIGURABLE PARAMETERS
# ================================

DEFAULT_INPUT_XML = "Nozzle_10deg_skindepth_1.xml"
DEFAULT_VARIANTS_DIR = "nozzle_variants_v2"  # New: where organized folders will be created
BASE_GEOMETRY_PATH = "/home/devlinjenkins/projects/NozzleSimOpti/simulation/geometries/MAIA_v0_Blackhole"

# Single test case parameters
TEST_Z_START = 50                # New blackhole start z [cm]
TEST_RMAX_REDUCTION = 10         # Absolute reduction in rmax [cm]

# Batch generation parameters
z_start_values = [10.5176, 11.5176, 12.5176, 13.5176, 14.5176, 15.5176]
rmax_steps = [0, 0.6, 0.11, 0.16, 0.21, 0.26]

# ================================
# GEOMETRY CONSTANTS AND TARGETS
# ================================

target_geometry = {
    "NozzleW_right", "NozzleW_left",
    "NozzleBlackhole_right", "NozzleBlackhole_left"
}

Nozzle_zmin = 6
Nozzle_kink_z = 100
Nozzle_kink_max_r = 17.57473619

# ================================
# VARIANT ORGANIZER CLASS
# ================================

class NozzleVariantOrganizer:
    def __init__(self, base_geometry_path, output_base_path):
        """
        Initialize the organizer with base paths.
        
        Args:
            base_geometry_path: Path to MAIA_v0_Blackhole directory
            output_base_path: Base path where variant folders will be created
        """
        self.base_geometry_path = Path(base_geometry_path)
        self.output_base_path = Path(output_base_path)
        
        # Files to exclude from copying
        self.exclude_files = {
            'Nozzle_10deg_skindepth_1.xml',
            'MAIA_v0_blackhole.xml'
        }
        
        # Verify base geometry path exists
        if not self.base_geometry_path.exists():
            raise ValueError(f"Base geometry path does not exist: {self.base_geometry_path}")
            
    def create_variant_folder(self, nozzle_xml_path, variant_name=None):
        """
        Create a folder for a nozzle variant with all necessary files.
        
        Args:
            nozzle_xml_path: Path to the generated nozzle XML file
            variant_name: Optional custom name for the variant folder
        """
        nozzle_xml_path = Path(nozzle_xml_path)
        
        if not nozzle_xml_path.exists():
            logger.error(f"Nozzle XML file not found: {nozzle_xml_path}")
            return None
            
        # Determine variant name
        if variant_name is None:
            variant_name = nozzle_xml_path.stem
            
        # Create variant folder
        variant_folder = self.output_base_path / variant_name
        variant_folder.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created variant folder: {variant_folder}")
        
        # Copy all files from base geometry folder except excluded ones
        self._copy_base_files(variant_folder)
        
        # Copy the nozzle XML file
        nozzle_dest = variant_folder / nozzle_xml_path.name
        shutil.copy2(nozzle_xml_path, nozzle_dest)
        logger.info(f"Copied nozzle file: {nozzle_xml_path.name}")
        
        # Create MAIA.xml file
        maia_xml_path = self._create_maia_xml(variant_folder, nozzle_xml_path.name)
        logger.info(f"Created MAIA.xml file: {maia_xml_path}")
        
        return variant_folder
        
    def _copy_base_files(self, destination_folder):
        """
        Copy all files from base geometry folder to destination, excluding specific files.
        
        Args:
            destination_folder: Path to the destination folder
        """
        for item in self.base_geometry_path.iterdir():
            # Skip if it's a directory or an excluded file
            if item.is_dir() or item.name in self.exclude_files:
                continue
                
            # Skip if it's a nozzle XML file (we'll copy the new one)
            if item.name.startswith('Nozzle_') and item.suffix == '.xml':
                continue
                
            # Copy the file
            dest_path = destination_folder / item.name
            shutil.copy2(item, dest_path)
            logger.debug(f"Copied: {item.name}")
            
    def _create_maia_xml(self, variant_folder, nozzle_filename):
        """
        Create a new MAIA.xml file with the updated nozzle reference.
        
        Args:
            variant_folder: Path to the variant folder
            nozzle_filename: Name of the nozzle XML file
            
        Returns:
            Path to the created MAIA.xml file
        """
        # Always use MAIA_v0_blackhole.xml as template if it exists
        maia_template = self.base_geometry_path / "MAIA_v0_blackhole.xml"
        if not maia_template.exists():
            logger.warning("MAIA_v0_blackhole.xml not found, creating basic MAIA.xml")
            maia_content = self._create_basic_maia_xml(nozzle_filename)
        else:
            maia_content = self._modify_maia_xml(maia_template, nozzle_filename)
        # Write the new MAIA.xml file
        maia_path = variant_folder / f"MAIA_{nozzle_filename.replace('.xml', '')}.xml"
        with open(maia_path, 'w', encoding='utf-8') as f:
            f.write(maia_content)
        return maia_path
        
    def _modify_maia_xml(self, template_path, nozzle_filename):
        """
        Modify an existing MAIA XML template with new nozzle reference.

        Args:
            template_path: Path to the template MAIA XML file
            nozzle_filename: Name of the new nozzle XML file

        Returns:
            Modified XML content as string
        """
        try:
            tree = ET.parse(template_path)
            root = tree.getroot()

            updated = False
            for include_elem in root.findall('.//include'):
                ref_attr = include_elem.get('ref', '')
                if 'Nozzle' in ref_attr and ref_attr.endswith('.xml'):
                    include_elem.set('ref', nozzle_filename)
                    updated = True
                    logger.info(f"Updated include ref from '{ref_attr}' to '{nozzle_filename}'")

            if not updated:
                logger.warning("No nozzle include ref found to update in MAIA template")

            ET.indent(tree, space='\t')
            return '<?xml version="1.0" encoding="utf-8"?>\n' + ET.tostring(root, encoding='unicode')

        except ET.ParseError as e:
            logger.error(f"Error parsing XML template: {e}")
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
                
    def _create_basic_maia_xml(self, nozzle_filename):
        """
        Create a basic MAIA XML file when no template is available.
        
        Args:
            nozzle_filename: Name of the nozzle XML file
            
        Returns:
            Basic XML content as string
        """
        root = ET.Element('MAIA')
        
        # Add basic structure
        geometry = ET.SubElement(root, 'geometry')
        nozzle = ET.SubElement(geometry, 'nozzle')
        nozzle.set('file', nozzle_filename)
        
        # Add other common sections
        simulation = ET.SubElement(root, 'simulation')
        ET.SubElement(simulation, 'type').text = 'CFD'
        
        # Format and return
        ET.indent(root, space='  ')
        return ET.tostring(root, encoding='unicode', xml_declaration=True)

# ================================
# UTILITY FUNCTIONS
# ================================

def parse_units(value_str, constants=None):
    if constants is None:
        constants = {
            'Nozzle_zmin': (6.0, 'cm'),
            'Nozzle_kink_z': (100.0, 'cm'),
            'Nozzle_kink_max_r': (17.57473619, 'cm')
        }

    value_str = value_str.strip()

    if value_str in constants:
        return constants[value_str]

    if value_str.startswith('-') and value_str[1:] in constants:
        val, unit = constants[value_str[1:]]
        return -val, unit

    if '*' in value_str:
        num_part, unit = value_str.split('*', 1)
        num_part = num_part.strip()
        unit = unit.strip()
        if num_part in constants:
            val, _ = constants[num_part]
            return val, unit
        elif num_part.startswith('-') and num_part[1:] in constants:
            val, _ = constants[num_part[1:]]
            return -val, unit
        else:
            return float(num_part), unit

    try:
        return float(value_str), ''
    except ValueError:
        print(f"Warning: Could not parse value '{value_str}', using 0.0")
        return 0.0, ''

def format_units(value, unit):
    value = round(value, 8)
    return f"{value}*{unit}" if unit else str(value)

# ================================
# BASE GEOMETRIES
# ================================

def get_blackhole_base_geometry():
    return {
        ('NozzleBlackhole_right', 10.5176): (0.79922, 0.79922),
        ('NozzleBlackhole_right', 15): (0.6, 1.58694),
        ('NozzleBlackhole_right', 99.99999999): (0.3, 16.57473619),
        ('NozzleBlackhole_right', 100): (0.3, 12.47473619),
        ('NozzleBlackhole_right', 204.48824): (0.6124092832, 12.47473619),
        ('NozzleBlackhole_right', 595): (1.78, 42),

        ('NozzleBlackhole_left', -10.5176): (0.79922, 0.79922),
        ('NozzleBlackhole_left', -15): (0.6, 1.58694),
        ('NozzleBlackhole_left', -99.99999999): (0.3, 16.57473619),
        ('NozzleBlackhole_left', -100): (0.3, 12.47473619),
        ('NozzleBlackhole_left', -204.48824): (0.6124092832, 12.47473619),
        ('NozzleBlackhole_left', -595): (1.78, 42),
    }

def get_nozzle_base_geometry():
    return {
        ('NozzleW_right', 6): (1.0, 1.0),
        ('NozzleW_right', 10.5176): (0.79922, 1.79923),
        ('NozzleW_right', 15): (1.58694, 2.58694),
        ('NozzleW_right', 99.99999999): (16.57473619, 17.57473619),
        ('NozzleW_right', 100): (12.47473619, 13.47473619),
        ('NozzleW_right', 204.48824): (12.47473619, 13.47473619),
        ('NozzleW_right', 595): (42, 43),

        ('NozzleW_left', -6): (1.0, 1.0),
        ('NozzleW_left', -10.5176): (0.79922, 1.79923),
        ('NozzleW_left', -15): (1.58694, 2.58694),
        ('NozzleW_left', -99.99999999): (16.57473619, 17.57473619),
        ('NozzleW_left', -100): (12.47473619, 13.47473619),
        ('NozzleW_left', -204.48824): (12.47473619, 13.47473619),
        ('NozzleW_left', -595): (42, 43),
    }

# ================================
# MODIFICATION FUNCTIONS
# ================================

def modify_blackhole_geometry_absolute(base_geometry, z_start, rmax_reduction_absolute):
    modified = {}
    blackhole_rmax_changes = {}

    min_z_blackhole = min(abs(z) for (name, z) in base_geometry if "Blackhole" in name)
    max_rmax = max(rmax for (name, z), (_, rmax) in base_geometry.items() if "Blackhole" in name)

    print(f"Maximum blackhole rmax found: {max_rmax} cm")
    print(f"Original blackhole start z: ±{min_z_blackhole} cm")
    print(f"New blackhole start z: ±{z_start} cm")

    for (name, z), (rmin, rmax) in base_geometry.items():
        if "Blackhole" not in name:
            modified[(name, z)] = (rmin, rmax)
            continue

        abs_z = abs(z)

        if min_z_blackhole < abs_z < z_start:
            continue

        if abs_z == min_z_blackhole:
            sign = 1 if z > 0 else -1
            new_z = sign * z_start
            new_rmax = max(rmin, rmax - rmax_reduction_absolute)
            modified[(name, new_z)] = (rmin, new_rmax)
            blackhole_rmax_changes[new_z] = new_rmax
            if new_rmax == rmin:
                print(f"  Warning: {name} at z={new_z} hit minimum thickness (rmax=rmin={rmin})")
        else:
            new_rmax = max(rmin, rmax - rmax_reduction_absolute)
            modified[(name, z)] = (rmin, new_rmax)
            blackhole_rmax_changes[z] = new_rmax
            if new_rmax == rmin:
                print(f"  Warning: {name} at z={z} hit minimum thickness (rmax=rmin={rmin})")

    return modified, blackhole_rmax_changes

def modify_geometry_file(input_path, output_path, modifications):
    tree = ET.parse(input_path)
    root = tree.getroot()

    found = {det.get("name", "") for det in root.findall(".//detector")}
    missing = target_geometry - found
    if missing:
        print(f"Warning: Missing detectors in XML: {missing}")

    for detector in root.findall(".//detector"):
        name = detector.get("name", "")
        if name not in target_geometry:
            continue

        print(f"Processing detector: {name}")
        zplanes = detector.findall("zplane")

        new_zplane_data = []
        for (mod_name, mod_z), (new_rmin, new_rmax) in modifications.items():
            if mod_name == name:
                new_zplane_data.append((mod_z, new_rmin, new_rmax))

        if new_zplane_data:
            for z in zplanes:
                detector.remove(z)

            new_zplane_data_sorted = sorted(new_zplane_data, key=lambda item: (item[0] if item[0] >= 0 else -item[0]))
            for mod_z, new_rmin, new_rmax in new_zplane_data_sorted:
                new_zplane = ET.Element("zplane")
                new_zplane.set("z", format_units(mod_z, "cm"))
                new_zplane.set("rmin", format_units(new_rmin, "cm"))
                new_zplane.set("rmax", format_units(new_rmax, "cm"))
                detector.append(new_zplane)

        else:
            for zplane in zplanes:
                z_value_str = zplane.get("z")
                if z_value_str is None:
                    continue
                z_value, _ = parse_units(z_value_str)
                key = (name, z_value)
                if key in modifications:
                    new_rmin, new_rmax = modifications[key]
                    old_rmin, unit_rmin = parse_units(zplane.get("rmin"))
                    old_rmax, unit_rmax = parse_units(zplane.get("rmax"))
                    zplane.set("rmin", format_units(new_rmin, unit_rmin))
                    zplane.set("rmax", format_units(new_rmax, unit_rmax))
                    print(f"Updated {name} z={z_value}: rmin {old_rmin}->{new_rmin}, rmax {old_rmax}->{new_rmax}")

    ET.indent(tree, space="    ")
    tree.write(output_path, encoding='utf-8', xml_declaration=True)
    print(f"Saved modified XML to {output_path}")

def adjust_nozzle_for_blackhole(nozzle_geometry, blackhole_rmax_changes, z_start):
    adjusted = {}
    min_z_blackhole = 10.5176

    for (name, z), (rmin, rmax) in nozzle_geometry.items():
        if 'NozzleW' in name:
            abs_z = abs(z)

            if abs_z >= 6 and abs_z < z_start:
                if abs_z < min_z_blackhole:
                    adjusted[(name, z)] = (rmin, rmax)
                else:
                    matching_blackhole = z if z in blackhole_rmax_changes else (z_start if z > 0 else -z_start)
                    new_rmin = blackhole_rmax_changes.get(matching_blackhole, rmin)
                    adjusted[(name, z)] = (new_rmin, rmax)
            elif abs_z == min_z_blackhole and z_start > min_z_blackhole:
                new_z = z_start if z > 0 else -z_start
                new_rmin = blackhole_rmax_changes.get(new_z, rmin)
                adjusted[(name, new_z)] = (new_rmin, rmax)
            else:
                new_rmin = blackhole_rmax_changes.get(z, rmin)
                adjusted[(name, z)] = (new_rmin, rmax)
        else:
            adjusted[(name, z)] = (rmin, rmax)

    # Ensure a z-plane at the blackhole start (z_start) for all NozzleW geometries
    for name in set(n for (n, _) in nozzle_geometry if 'NozzleW' in n):
        existing_zs = [round(abs(z), 6) for (n, z) in adjusted if n == name]
        if round(z_start, 6) not in existing_zs:
            new_z = z_start if 'right' in name else -z_start
            # Use blackhole rmax at this z if available, else use original rmin
            orig_rmin = None
            for (n, z), (rmin, rmax) in nozzle_geometry.items():
                if n == name and abs(z) == min_z_blackhole:
                    orig_rmin = rmin
                    break
            new_rmin = blackhole_rmax_changes.get(new_z, orig_rmin if orig_rmin is not None else 1.0)
            # Extrapolate rmax linearly from z=6 to z=99.99999999
            zmin, zmax = 6.0, 99.99999999
            rmin_val, rmax_val = 1.0, 17.57473619
            slope = (rmax_val - rmin_val) / (zmax - zmin)
            extrapolated_rmax = rmin_val + slope * (z_start - zmin)
            new_rmax = round(extrapolated_rmax, 8)
            adjusted[(name, new_z)] = (new_rmin, new_rmax)

    return adjusted

def generate_geometry_iterations_absolute(input_xml, variants_dir, z_start_values, rmax_steps, organize_variants=True):
    """
    Generate geometry iterations and optionally organize them into folders.
    
    Args:
        input_xml: Input XML file path
        output_dir: Directory for initial nozzle XML files
        variants_dir: Directory for organized variant folders
        z_start_values: List of z start values
        rmax_steps: List of rmax reduction values
        organize_variants: Whether to organize variants into folders (default: True)
    """
    blackhole_base = get_blackhole_base_geometry()
    nozzle_base = get_nozzle_base_geometry()
    
    # Initialize organizer if needed
    organizer = None
    if organize_variants:
        try:
            organizer = NozzleVariantOrganizer(BASE_GEOMETRY_PATH, variants_dir)
            logger.info(f"Initialized variant organizer with base path: {BASE_GEOMETRY_PATH}")
        except Exception as e:
            logger.error(f"Failed to initialize variant organizer: {e}")
            logger.warning("Continuing without variant organization")
            organize_variants = False

    iteration = 0
    for z_start, rmax_reduction in product(z_start_values, rmax_steps):
        print(f"\n=== Iteration {iteration}: z_start={z_start}, rmax_reduction={rmax_reduction} cm ===")
        all_modifications = {}

        modified_blackhole, blackhole_rmax_changes = modify_blackhole_geometry_absolute(
            blackhole_base, z_start, rmax_reduction)
        adjusted_nozzle = adjust_nozzle_for_blackhole(nozzle_base, blackhole_rmax_changes, z_start)

        all_modifications.update(modified_blackhole)
        all_modifications.update(adjusted_nozzle)

        filename = f"nozzle_z{str(z_start).replace('.', 'p')}_rmaxMinus{str(rmax_reduction).replace('.', 'p')}.xml"
        output_path = Path(variants_dir) / filename

        modify_geometry_file(input_xml, output_path, all_modifications)
        
        # Organize into variant folder if enabled
        if organize_variants and organizer:
            try:
                variant_folder = organizer.create_variant_folder(output_path)
                if variant_folder:
                    logger.info(f"Organized variant into: {variant_folder}")
                    # Clean up top-level nozzle file once copied into variant folder
                    try:
                        os.remove(output_path)
                        logger.info(f"Removed top-level nozzle file: {output_path}")
                    except Exception as e:
                        logger.warning(f"Failed to remove top-level nozzle file {output_path}: {e}")
            except Exception as e:
                logger.error(f"Failed to organize variant {filename}: {e}")
        
        iteration += 1

    print(f"\nGenerated {iteration} geometry files in {variants_dir}")
    if organize_variants:
        print(f"Organized variants in {variants_dir}")

# ================================
# ENTRY POINT
# ================================

if __name__ == "__main__":
    input_xml = DEFAULT_INPUT_XML
    variants_dir = DEFAULT_VARIANTS_DIR
    
    # Create directories
    os.makedirs(variants_dir, exist_ok=True)
    
    print(f"Variants directory: {variants_dir}")
    print(f"Base geometry path: {BASE_GEOMETRY_PATH}")

    # Full iteration set with automatic organization
    print("\n--- Generating All Combinations ---")
    generate_geometry_iterations_absolute(
        input_xml, 
        variants_dir,
        z_start_values, 
        rmax_steps,
        organize_variants=True  # Enable automatic organization
    )


# ================================
# OPTIONAL: Auto-run simulation on each generated MAIA.xml
# ================================

def run_simulations_for_variants(variant_dir, steering_template_path):
    import shutil
    from pathlib import Path

    variant_paths = sorted(Path(variant_dir).glob("*/MAIA_*.xml"))

    for maia_path in variant_paths:
        variant_folder = maia_path.parent
        print(f"\n[INFO] Processing variant: {maia_path}")

        # Convert to ROOT using geoConverter
        print("[INFO] Running geoConverter...")
        cmd_convert = f"geoConverter -compact2tgeo -input {maia_path} -output {maia_path}.root"
        conversion_result = os.system(cmd_convert)
        if conversion_result != 0:
            print(f"[ERROR] geoConverter failed for {maia_path}")
            continue

        # Prepare the steering file
        steer_copy_path = variant_folder / "steer_sim.py"
        shutil.copy(steering_template_path, steer_copy_path)

        with open(steer_copy_path, 'r') as f:
            content = f.read()

        # Replace file paths
        content = content.replace(
            "/home/devlinjenkins/projects/NozzleSimOpti/simulation/geometries/MAIA_v0_Blackhole/MAIA_v0_blackhole.xml",
            str(maia_path)
        )
        output_name = f"mumu_H_bb_100E_{maia_path.stem}.slcio"
        content = content.replace("mumu_H_bb_100E_MAIA_blackhole.slcio", output_name)

        with open(steer_copy_path, 'w') as f:
            f.write(content)

        # Run ddsim
        print(f"[INFO] Running ddsim for {steer_copy_path}...")
        sim_result = os.system(f"ddsim --steeringFile {steer_copy_path} > {variant_folder}/sim.log 2>&1")
        if sim_result != 0:
            print(f"[ERROR] ddsim failed for {steer_copy_path}")
        else:
            print(f"[SUCCESS] Simulation complete: {output_name}")

# Example usage:
run_simulations_for_variants(DEFAULT_VARIANTS_DIR, "/home/devlinjenkins/projects/NozzleSimOpti/simulation/steeringFiles/steer_sim_Hbb_MAIA_blackhole_starter.py")