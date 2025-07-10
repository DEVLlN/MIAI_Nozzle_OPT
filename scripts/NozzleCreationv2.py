import xml.etree.ElementTree as ET
import os
import sys
import shutil
from pathlib import Path
import logging
import subprocess
import stat

## $ python script.py --test for single test case
## $ python script.py --batch --organize for batch generation with organized folders

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ================================
# CONFIGURABLE PARAMETERS
# ================================

DEFAULT_INPUT_XML = "Nozzle_10deg_skindepth_1.xml"
DEFAULT_VARIANTS_DIR = "nozzle_variants_v3"  # where folders will be created
BASE_GEOMETRY_PATH = "/home/devlinjenkins/projects/NozzleSimOpti/simulation/geometries/MAIA_v0_Blackhole"

# HTCondor submission control
SUBMIT_JOBS_AUTOMATICALLY = False  # Set to True if you want automatic submission

# Single test case parameters
TEST_Z_START = 0.001                # Blackhole start z [cm] (relative to tip)
TEST_RMAX_REDUCTION = 0.05          # Absolute reduction in rmax [cm]

# Batch generation parameters - RELATIVE TO TIP (z=0)
# z_start_values: where the blackhole starts (cm from tip)
z_start_values = [0.0001, 0.001, 0.01, 0.1, 1.0, 5.0]  # From 1 micron to 5 cm from tip

# Absolute radius reductions in cm (not fractions)
# These are the actual reductions that will be applied
rmax_reduction_values = [0.0001, 0.0005, 0.001, 0.005, 0.01, 0.05, 0.1, 0.5]  # From 1 micron to 5 mm

# Steering file template path (constructed from BASE_GEOMETRY_PATH)
STEERING_TEMPLATE_FILENAME = "steer_sim_Hbb_MAIA_blackhole_starter.py"

# ================================
# GEOMETRY CONSTANTS AND TARGETS
# ================================

target_geometry = {
    "NozzleW_right", "NozzleW_left",
    "NozzleBlackhole_right", "NozzleBlackhole_left"
}

# Original coordinates (will be offset)
NOZZLE_TIP_ORIGINAL_Z = 6  # The original z-coordinate of the nozzle tip
Nozzle_zmin = 0  # After offset, tip will be at z=0
Nozzle_kink_z = 94  # 100 - 6 = 94 (relative to tip)
Nozzle_kink_max_r = 17.57473619

# Minimum allowed blackhole start position (relative to tip)
MIN_BLACKHOLE_START = 0.00001  # 0.1 micron from tip

# Maximum allowed reduction factors
MAX_REDUCTION_FACTOR = 0.9  # Don't reduce more than 90% of available space
MIN_THICKNESS_PRESERVATION = 0.0001  # Preserve at least 1 micron of thickness

# ================================
# COORDINATE OFFSET FUNCTIONS
# ================================

def apply_z_offset(z_coord, offset=-NOZZLE_TIP_ORIGINAL_Z):
    """Apply offset to make coordinates relative to nozzle tip."""
    return z_coord + offset

def offset_geometry_dict(geometry_dict, offset=-NOZZLE_TIP_ORIGINAL_Z):
    """Apply z-offset to an entire geometry dictionary."""
    offset_dict = {}
    for (name, z), (rmin, rmax) in geometry_dict.items():
        new_z = apply_z_offset(z, offset)
        offset_dict[(name, new_z)] = (rmin, rmax)
    return offset_dict

# ================================
# VALIDATION FUNCTIONS
# ================================

def get_nozzle_radius_at_z(z_pos):
    """
    Get the approximate nozzle outer radius at a given z position.
    Uses linear interpolation between known points.
    """
    # Key points for nozzle outer radius (tip-relative coordinates)
    # At z=0 (tip): r ≈ 1.0 cm
    # At z=94 (kink): r ≈ 17.57 cm
    # Linear approximation between these points
    if z_pos <= 0:
        return 1.0
    elif z_pos >= 94:
        return 17.57473619
    else:
        # Linear interpolation
        slope = (17.57473619 - 1.0) / 94.0
        return 1.0 + slope * z_pos

def validate_reduction_at_position(z_pos, rmax_reduction, geometry_dict, component_prefix='NozzleW'):
    """
    Validate if the reduction is reasonable at the given z position.
    
    Returns:
        (is_valid, message, suggested_reduction)
    """
    # Find the closest geometry points for interpolation
    relevant_points = []
    for (name, z), (rmin, rmax) in geometry_dict.items():
        if component_prefix in name and z > 0:  # Only use positive z values
            relevant_points.append((z, rmin, rmax))
    
    if not relevant_points:
        return False, f"No {component_prefix} geometry found", 0
    
    relevant_points.sort(key=lambda x: x[0])
    
    # Find or interpolate values at z_pos
    rmin_at_pos = None
    rmax_at_pos = None
    
    # Check if z_pos matches an existing point
    for z, rmin, rmax in relevant_points:
        if abs(z - z_pos) < 1e-6:
            rmin_at_pos = rmin
            rmax_at_pos = rmax
            break
    
    # If not found, interpolate
    if rmin_at_pos is None:
        for i in range(len(relevant_points) - 1):
            z1, rmin1, rmax1 = relevant_points[i]
            z2, rmin2, rmax2 = relevant_points[i + 1]
            
            if z1 <= z_pos <= z2:
                # Linear interpolation
                t = (z_pos - z1) / (z2 - z1)
                rmin_at_pos = rmin1 + t * (rmin2 - rmin1)
                rmax_at_pos = rmax1 + t * (rmax2 - rmax1)
                break
        
        # If still not found, extrapolate from nearest points
        if rmin_at_pos is None:
            if z_pos < relevant_points[0][0]:
                # Near the tip - use approximate values
                rmax_at_pos = get_nozzle_radius_at_z(z_pos)
                # Nozzle thickness is approximately 1 cm throughout
                rmin_at_pos = max(0, rmax_at_pos - 1.0)
            else:
                # Use last point
                _, rmin_at_pos, rmax_at_pos = relevant_points[-1]
    
    # Validate the reduction
    available_space = rmax_at_pos - rmin_at_pos
    
    # Check if reduction exceeds total radius
    if rmax_reduction >= rmax_at_pos:
        suggested = min(rmax_at_pos * MAX_REDUCTION_FACTOR, available_space - MIN_THICKNESS_PRESERVATION)
        return False, f"Reduction {rmax_reduction:.4f} cm exceeds radius {rmax_at_pos:.4f} cm at z={z_pos:.4f} cm", max(0, suggested)
    
    # Check if reduction leaves enough thickness
    if rmax_reduction >= available_space - MIN_THICKNESS_PRESERVATION:
        suggested = available_space * MAX_REDUCTION_FACTOR
        return False, f"Reduction {rmax_reduction:.4f} cm would leave insufficient thickness at z={z_pos:.4f} cm (available: {available_space:.4f} cm)", max(0, suggested)
    
    # Check if reduction is more than MAX_REDUCTION_FACTOR of available space
    if rmax_reduction > available_space * MAX_REDUCTION_FACTOR:
        suggested = available_space * MAX_REDUCTION_FACTOR
        return False, f"Reduction {rmax_reduction:.4f} cm exceeds {MAX_REDUCTION_FACTOR*100}% of available space at z={z_pos:.4f} cm", max(0, suggested)
    
    return True, "Reduction is valid", rmax_reduction

def validate_configuration(z_start, rmax_reduction, geometry_dict):
    """
    Validate an entire configuration before processing.
    
    Returns:
        (is_valid, messages, suggested_reduction)
    """
    messages = []
    is_valid = True
    suggested_reductions = []

    # Only validate the single z_start position
    actual_z_start = z_start
    z_positions = [z_start]

    # Validate each position
    for z_pos in z_positions:
        valid, msg, suggested = validate_reduction_at_position(z_pos, rmax_reduction, geometry_dict)
        if not valid:
            is_valid = False
            messages.append(msg)
            suggested_reductions.append(suggested)

    # Return the minimum suggested reduction if invalid
    final_suggested = min(suggested_reductions) if suggested_reductions else 0

    return is_valid, messages, final_suggested

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
        target_path = variant_folder / nozzle_xml_path.name
        if nozzle_xml_path.resolve() != target_path.resolve():
            shutil.copy2(nozzle_xml_path, target_path)
        else:
            logger.info(f"Skipping copy: source and target are the same file: {target_path}")
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
        try:
            with open(maia_path, 'w', encoding='utf-8') as f:
                f.write(maia_content)
            logger.info(f"Wrote MAIA.xml to: {maia_path}")
        except Exception as e:
            logger.error(f"Failed to write MAIA.xml to {maia_path}: {e}")
        # Insert safety check before returning
        if not maia_path.exists():
            logger.error(f"MAIA.xml file does not exist at expected path: {maia_path}")
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
        # Updated constants to use tip-relative coordinates
        constants = {
            'Nozzle_zmin': (0.0, 'cm'),  # Tip is now at z=0
            'Nozzle_kink_z': (94.0, 'cm'),  # 100 - 6 = 94
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

def interpolate_geometry_values(z_pos, z1, z2, rmin1, rmax1, rmin2, rmax2):
    """
    Linearly interpolate rmin and rmax values at z_pos between two known points.
    """
    if abs(z2 - z1) < 1e-10:  # Avoid division by zero
        return rmin1, rmax1
    
    t = (z_pos - z1) / (z2 - z1)
    rmin_interp = rmin1 + t * (rmin2 - rmin1)
    rmax_interp = rmax1 + t * (rmax2 - rmax1)
    
    return rmin_interp, rmax_interp

# ================================
# BASE GEOMETRIES (WITH TIP-RELATIVE COORDINATES)
# ================================

def get_blackhole_base_geometry():
    """Returns blackhole geometry with tip-relative coordinates (z=0 at tip)."""
    original = {
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
    return offset_geometry_dict(original)

def get_nozzle_base_geometry():
    """Returns nozzle geometry with tip-relative coordinates (z=0 at tip)."""
    original = {
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
    return offset_geometry_dict(original)

# ================================
# MODIFICATION FUNCTIONS
# ================================

def modify_blackhole_geometry_absolute(base_geometry, z_start, rmax_reduction_absolute):
    """
    Modify blackhole geometry.
    Can now start blackhole at any position >= MIN_BLACKHOLE_START from tip.
    Now includes comprehensive validation.
    
    Args:
        base_geometry: Base geometry dictionary
        z_start: Starting z position for blackhole
        rmax_reduction_absolute: Total reduction in rmax
    """
    modified = {}
    blackhole_rmax_changes = {}

    # Get the original minimum z from base geometry
    original_min_z = min(abs(z) for (name, z) in base_geometry if "Blackhole" in name)

    actual_z_start = z_start
    print(f"Original blackhole start z: ±{original_min_z} cm (relative to tip)")
    print(f"New blackhole start z: ±{actual_z_start} cm (relative to tip)")

    # Validate z_start
    if actual_z_start < MIN_BLACKHOLE_START:
        print(f"Warning: z_start {actual_z_start} is less than minimum {MIN_BLACKHOLE_START}, using minimum")
        actual_z_start = MIN_BLACKHOLE_START

    # Sort all z-positions for each component
    sorted_positions = {}
    for (name, z), (rmin, rmax) in base_geometry.items():
        if name not in sorted_positions:
            sorted_positions[name] = []
        sorted_positions[name].append((abs(z), z, rmin, rmax))
    
    for name in sorted_positions:
        sorted_positions[name].sort(key=lambda x: x[0])

    # Track the actual reduction being applied
    actual_reduction = rmax_reduction_absolute

    for (name, z), (rmin, rmax) in base_geometry.items():
        if "Blackhole" not in name:
            modified[(name, z)] = (rmin, rmax)
            continue

        abs_z = abs(z)
        sign = 1 if z > 0 else -1

        # Skip points before the new start position
        if abs_z < actual_z_start and abs_z != original_min_z:
            continue

        # Handle the creation of new start point
        if abs_z == original_min_z:
            # If we need to start before the original minimum, interpolate
            if actual_z_start < original_min_z:
                # Find the two points to interpolate between
                positions = sorted_positions[name]
                
                # Since we want to extrapolate backwards from the tip
                # We'll use the nozzle geometry at the tip to get appropriate values
                nozzle_name = name.replace("Blackhole", "W")
                nozzle_positions = sorted_positions.get(nozzle_name, [])
                
                if nozzle_positions and len(nozzle_positions) >= 2:
                    # Get nozzle values at tip and next point
                    z0, _, rmin0, rmax0 = nozzle_positions[0]
                    z1, _, rmin1, rmax1 = nozzle_positions[1]
                    
                    # Interpolate/extrapolate to get blackhole start values
                    # For blackhole, rmin = rmax (it's the thickness)
                    _, rmax_at_start = interpolate_geometry_values(
                        actual_z_start, z0, z1, rmin0, rmax0, rmin1, rmax1
                    )
                    # Set a thin initial blackhole
                    rmin_at_start = rmax_at_start - 0.001  # 10 micron thickness
                    rmin_at_start = max(0.0001, rmin_at_start)  # Ensure positive
                else:
                    # Fallback: use a very small value
                    rmin_at_start = 0.0001
                    rmax_at_start = 0.001

                # Validate and adjust reduction at this position
                available_space = rmax_at_start - rmin_at_start
                if rmax_reduction_absolute >= available_space - MIN_THICKNESS_PRESERVATION:
                    actual_reduction = max(0, available_space - MIN_THICKNESS_PRESERVATION)
                    print(f"Warning: Requested reduction ({rmax_reduction_absolute} cm) "
                          f"exceeds safe limit at z={actual_z_start} cm. "
                          f"Using reduced value: {actual_reduction} cm")
                
                # Create the new start point
                new_z = sign * actual_z_start
                new_rmax = max(rmin_at_start + MIN_THICKNESS_PRESERVATION, rmax_at_start - actual_reduction)
                modified[(name, new_z)] = (rmin_at_start, new_rmax)
                blackhole_rmax_changes[new_z] = new_rmax
            elif actual_z_start >= original_min_z:
                # Original behavior for positions at or after original minimum
                # Validate reduction
                available_space = rmax - rmin
                if actual_reduction >= available_space - MIN_THICKNESS_PRESERVATION:
                    actual_reduction = max(0, available_space - MIN_THICKNESS_PRESERVATION)
                    print(f"Warning: Capping reduction to {actual_reduction} cm at z={actual_z_start}")
                
                new_z = sign * actual_z_start
                new_rmax = max(rmin + MIN_THICKNESS_PRESERVATION, rmax - actual_reduction)
                modified[(name, new_z)] = (rmin, new_rmax)
                blackhole_rmax_changes[new_z] = new_rmax
        else:
            # For existing points beyond the start, apply reduction with validation
            available_space = rmax - rmin
            point_reduction = actual_reduction
            
            if point_reduction >= available_space - MIN_THICKNESS_PRESERVATION:
                point_reduction = max(0, available_space - MIN_THICKNESS_PRESERVATION)
                if point_reduction < actual_reduction:
                    print(f"Warning: Capping reduction to {point_reduction} cm at z={z}")
            
            new_rmax = max(rmin + MIN_THICKNESS_PRESERVATION, rmax - point_reduction)
            modified[(name, z)] = (rmin, new_rmax)
            blackhole_rmax_changes[z] = new_rmax

    return modified, blackhole_rmax_changes

def get_interpolated_values(component_name, z_pos, sorted_positions):
    """
    Get interpolated rmin and rmax values at a given z position.
    """
    positions = sorted_positions.get(component_name, [])
    
    # Find the two points to interpolate between
    for i in range(len(positions) - 1):
        z1, _, rmin1, rmax1 = positions[i]
        z2, _, rmin2, rmax2 = positions[i + 1]
        
        if z1 <= z_pos <= z2:
            return interpolate_geometry_values(z_pos, z1, z2, rmin1, rmax1, rmin2, rmax2)
    
    # If we're before the first point, use the first point's values
    if positions and z_pos < positions[0][0]:
        return positions[0][2], positions[0][3]
    
    # If we're after the last point, use the last point's values
    if positions and z_pos > positions[-1][0]:
        return positions[-1][2], positions[-1][3]
    
    # Fallback
    return 0.1, 0.2

def modify_geometry_file(input_path, output_path, modifications):
    """
    Modify geometry file, converting tip-relative coordinates back to original format.
    """
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
                # Convert back to original coordinate system for XML output
                original_z = mod_z - (-NOZZLE_TIP_ORIGINAL_Z)  # Reverse the offset
                new_zplane_data.append((original_z, new_rmin, new_rmax))

        if new_zplane_data:
            for z in zplanes:
                detector.remove(z)

            new_zplane_data_sorted = sorted(new_zplane_data, key=lambda item: (item[0] if item[0] >= 0 else -item[0]))
            for original_z, new_rmin, new_rmax in new_zplane_data_sorted:
                new_zplane = ET.Element("zplane")
                new_zplane.set("z", format_units(original_z, "cm"))
                new_zplane.set("rmin", format_units(new_rmin, "cm"))
                new_zplane.set("rmax", format_units(new_rmax, "cm"))
                detector.append(new_zplane)

        else:
            for zplane in zplanes:
                z_value_str = zplane.get("z")
                if z_value_str is None:
                    continue
                z_value, _ = parse_units(z_value_str)
                # Convert to tip-relative for lookup
                tip_relative_z = apply_z_offset(z_value)
                key = (name, tip_relative_z)
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
    """
    Adjust nozzle geometry to match blackhole changes.
    Simplified to avoid redundant mirroring.
    """
    adjusted = {}
    original_min_z = 4.5176  # 10.5176 - 6 = 4.5176 (relative to tip)
    
    step_z_start = max(MIN_BLACKHOLE_START, z_start)
    
    # Process all components
    for (name, z), (rmin, rmax) in nozzle_geometry.items():
        if 'NozzleW' not in name:
            # Copy non-nozzle components as-is
            adjusted[(name, z)] = (rmin, rmax)
            continue
            
        abs_z = abs(z)
        
        # Determine new rmin based on blackhole changes
        if abs_z < step_z_start:
            # Before blackhole start - keep original
            new_rmin = rmin
        else:
            # At or after blackhole start - match blackhole
            new_rmin = blackhole_rmax_changes.get(z, rmin)
            
        # Validate that new_rmin doesn't exceed rmax
        if new_rmin >= rmax - MIN_THICKNESS_PRESERVATION:
            new_rmin = max(rmin, rmax - MIN_THICKNESS_PRESERVATION)
            print(f"Warning: Adjusted nozzle rmin at z={z} to maintain minimum thickness")
            
        adjusted[(name, z)] = (new_rmin, rmax)
    
    # Ensure we have z-planes at the blackhole start position
    for side in ['right', 'left']:
        name = f'NozzleW_{side}'
        z = step_z_start if side == 'right' else -step_z_start
        
        # Check if this z already exists
        existing = any((n, z_val) for (n, z_val) in adjusted if n == name and abs(abs(z_val) - step_z_start) < 1e-6)
        
        if not existing and z in blackhole_rmax_changes:
            new_rmin = blackhole_rmax_changes[z]
            # Extrapolate rmax for this position
            new_rmax = get_nozzle_radius_at_z(step_z_start)
            
            # Validate
            if new_rmin >= new_rmax - MIN_THICKNESS_PRESERVATION:
                new_rmin = max(0, new_rmax - MIN_THICKNESS_PRESERVATION)
                
            adjusted[(name, z)] = (new_rmin, new_rmax)
    
    return adjusted

# ================================
# MAIN EXECUTION WITH VALIDATION
# ================================

def generate_variant_with_validation(z_start, rmax_reduction, input_xml_path, output_dir, 
                                   organizer, variant_name=None):
    """
    Generate a nozzle variant with full validation.
    
    Returns:
        (success, output_path, message)
    """
    # Load base geometries
    nozzle_base = get_nozzle_base_geometry()
    blackhole_base = get_blackhole_base_geometry()
    combined_base = {**nozzle_base, **blackhole_base}

    # Validate configuration
    is_valid, validation_messages, suggested_reduction = validate_configuration(
        z_start, rmax_reduction, combined_base
    )

    effective_reduction = rmax_reduction
    if not is_valid:
        error_msg = f"Invalid configuration for z_start={z_start}, reduction={rmax_reduction}:\n"
        error_msg += "\n".join(validation_messages)
        error_msg += f"\nSuggested maximum reduction: {suggested_reduction:.4f} cm"
        logger.error(error_msg)
        # Optionally, try with suggested reduction
        if suggested_reduction > 0:
            logger.info(f"Attempting with suggested reduction: {suggested_reduction:.4f} cm")
            effective_reduction = suggested_reduction
        else:
            return False, None, error_msg

    # Generate output filename using the final applied reduction
    if variant_name is None:
        variant_name = f"Nozzle_zstart_{z_start:.4f}_reduction_{effective_reduction:.4f}"

    filename = f"Nozzle_zstart_{z_start:.4f}_reduction_{effective_reduction:.4f}.xml"
    variant_folder = output_dir / variant_name
    variant_folder.mkdir(parents=True, exist_ok=True)
    output_path = variant_folder / filename

    try:
        # Modify blackhole geometry
        modified_blackhole, blackhole_changes = modify_blackhole_geometry_absolute(
            blackhole_base, z_start, effective_reduction
        )

        # Adjust nozzle geometry
        adjusted_nozzle = adjust_nozzle_for_blackhole(
            nozzle_base, blackhole_changes, z_start
        )

        # Combine modifications
        all_modifications = {**modified_blackhole, **adjusted_nozzle}

        # Write modified XML
        modify_geometry_file(input_xml_path, output_path, all_modifications)

        if not output_path.exists():
            raise FileNotFoundError(f"Expected output XML not found: {output_path}")

        # Create organized folder now that the output file is guaranteed to exist
        variant_folder_path = organizer.create_variant_folder(output_path, variant_name)
        logger.info(f"Created variant folder: {variant_folder_path}")

        return True, output_path, "Successfully generated variant"
        
    except Exception as e:
        error_msg = f"Error generating variant: {str(e)}"
        logger.error(error_msg)
        return False, None, error_msg

# ================================
# HTCondor Submission File Generation
# ================================
def generate_condor_submit_files(variants_dir, steering_template_path):
    """
    Generate HTCondor submission scripts for each nozzle variant.
    """
    from pathlib import Path
    variants_dir = Path(variants_dir)
    
    if not steering_template_path.exists():
        logger.error(f"Steering template not found: {steering_template_path}")
        logger.error("Please update the steering template path in the script")
        return
        
    for variant_folder in variants_dir.iterdir():
        if not variant_folder.is_dir():
            continue
        maia_path = None
        for f in variant_folder.iterdir():
            if f.name.startswith("MAIA_") and f.suffix == ".xml":
                maia_path = f
                break
        if not maia_path:
            logger.warning(f"No MAIA xml found in {variant_folder}")
            continue

        steering_dest = variant_folder / "steer_sim.py"
        with open(steering_template_path, "r", encoding="utf-8") as f:
            content = f.read()
        content = content.replace(
            str(Path(BASE_GEOMETRY_PATH) / "MAIA_v0_blackhole.xml"),
            str(maia_path)
        )
        with open(steering_dest, "w", encoding="utf-8") as f:
            f.write(content)

        # Write the submit file using RELATIVE paths
        submit_file = variant_folder / "nozzle_sim.submit"
        with open(submit_file, "w", encoding="utf-8") as f:
            f.write(
                "initialdir = .\n"
                "executable = ./run_sim.sh\n"
                "arguments = .\n"
                f"transfer_input_files = {maia_path.name}, steer_sim.py\n"
                "output = ./condor.out\n"
                "error = ./condor.err\n"
                "log = ./condor.log\n"
                "request_cpus = 1\n"
                "request_memory = 2GB\n"
                "request_disk = 2GB\n"
                "should_transfer_files = YES\n"
                "when_to_transfer_output = ON_EXIT\n"
                "+HasSingularity = true\nrequirements = (HasSingularity == true || HasApptainer == true)\n"
                "queue\n"
            )
        logger.info(f"Generated Condor submit file: {submit_file}")

        # Ensure run_sim.sh is present in each variant directory
        run_script_source = Path("run_sim.sh")  # Look in current directory
        run_script_dest = variant_folder / "run_sim.sh"
        if run_script_source.exists():
            shutil.copy(run_script_source, run_script_dest)
            run_script_dest.chmod(run_script_dest.stat().st_mode | 0o111)  # Ensure it's executable
        else:
            logging.warning(f"run_sim.sh not found at {run_script_source}")

# ================================
# MAIN EXECUTION
# ================================

if __name__ == "__main__":
    import argparse
    
    # Create run_sim.sh FIRST, before anything else needs it
    run_sim_path = Path("run_sim.sh")
    if not run_sim_path.exists():
        with open(run_sim_path, "w", encoding="utf-8") as f:
            f.write("""#!/bin/bash
apptainer exec /cvmfs/sw.hsf.org/key4hep/releases/nightly/20240118/key4hep-spack.key4hep.r16/x86_64-centos7-gcc11.2.0-opt/view/bin/dd4hep-geant4 --convert MAIA_*.xml -o geometry.root
apptainer exec /cvmfs/sw.hsf.org/key4hep/releases/nightly/20240118/key4hep-spack.key4hep.r16/x86_64-centos7-gcc11.2.0-opt/view/bin/ddsim --steeringFile steer_sim.py
""")
        logger.info("Created run_sim.sh in project root.")
    # Ensure run_sim.sh is executable
    run_sim_path.chmod(run_sim_path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    
    parser = argparse.ArgumentParser(description='Generate nozzle geometry variants')
    parser.add_argument('--test', action='store_true', help='Run single test case')
    parser.add_argument('--batch', action='store_true', help='Run batch generation (default)')
    
    args = parser.parse_args()
    
    # Default to batch if no arguments
    if not args.test and not args.batch:
        args.batch = True
    
    output_dir = Path(DEFAULT_VARIANTS_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)
    organizer = NozzleVariantOrganizer(BASE_GEOMETRY_PATH, output_dir)
    
    if args.test:
        # Run single test case
        logger.info(f"Running test case: z_start={TEST_Z_START}, reduction={TEST_RMAX_REDUCTION}")
        success, path, msg = generate_variant_with_validation(
            TEST_Z_START, TEST_RMAX_REDUCTION, DEFAULT_INPUT_XML, output_dir, 
            organizer=organizer
        )
        if success:
            logger.info(f"Test successful: {path}")
        else:
            logger.error(f"Test failed: {msg}")
    
    else:  # batch mode
        logger.info("Running batch generation with validation...")
        logger.info(f"Z-start values: {z_start_values}")
        logger.info(f"Reduction values: {rmax_reduction_values}")
        
        successful = 0
        failed = 0
        skipped_configs = []

        for z_start in z_start_values:
            for rmax_reduction in rmax_reduction_values:
                logger.info(f"\nProcessing: z_start={z_start} cm, reduction={rmax_reduction} cm")

                success, path, msg = generate_variant_with_validation(
                    z_start, rmax_reduction, DEFAULT_INPUT_XML, output_dir,
                    organizer=organizer
                )

                if success:
                    successful += 1
                    logger.info(f"✓ Generated: {path}")
                else:
                    failed += 1
                    skipped_configs.append((z_start, rmax_reduction, msg))
                    logger.warning(f"✗ Skipped: {msg}")

        # Print summary
        logger.info(f"\n{'='*60}")
        logger.info(f"BATCH GENERATION SUMMARY")
        logger.info(f"{'='*60}")
        logger.info(f"Total configurations attempted: {len(z_start_values) * len(rmax_reduction_values)}")
        logger.info(f"Successful: {successful}")
        logger.info(f"Failed/Skipped: {failed}")
        if successful + failed > 0:
            logger.info(f"Success rate: {successful/(successful+failed)*100:.1f}%")
        logger.info(f"Output directory: {output_dir}")
        
        if skipped_configs:
            logger.info(f"\nSkipped configurations:")
            for z_start, reduction, reason in skipped_configs[:5]:  # Show first 5
                logger.info(f"  z={z_start}, r={reduction}: {reason.split(':')[0]}")
            if len(skipped_configs) > 5:
                logger.info(f"  ... and {len(skipped_configs)-5} more")
        
        logger.info(f"{'='*60}")

        # Handle steering template path
        steering_template_path = Path(BASE_GEOMETRY_PATH).parent.parent / "steeringFiles" / STEERING_TEMPLATE_FILENAME
        
        if steering_template_path.exists():
            # Generate HTCondor submission files
            logger.info("\nGenerating HTCondor submission files...")
            generate_condor_submit_files(output_dir, steering_template_path)
            
            # Submit jobs if requested
            if SUBMIT_JOBS_AUTOMATICALLY:
                logger.info("\nSubmitting HTCondor jobs...")
                for variant_folder in output_dir.iterdir():
                    if not variant_folder.is_dir():
                        continue
                    submit_file = variant_folder / "nozzle_sim.submit"
                    if submit_file.exists():
                        logger.info(f"Submitting job: {submit_file}")
                        subprocess.run(["condor_submit", str(submit_file)])
            else:
                logger.info("\nHTCondor submit files generated. To submit all jobs, run:")
                logger.info(f"for dir in {output_dir}/*/; do condor_submit $dir/nozzle_sim.submit; done")
        else:
            logger.warning(f"\nSteering template not found: {steering_template_path}")
            logger.warning("HTCondor submission files not generated")
    
    logger.info("\nScript execution complete.")