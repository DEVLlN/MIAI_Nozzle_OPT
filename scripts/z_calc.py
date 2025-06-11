## This script finds the z-position between two defined z-planes
## where the difference between rmax and rmin (i.e. thickness)
## equals a specified delta. Assumes linear change in both rmin and rmax.

def interpolate_z_for_thickness(z1, rmin1, rmax1, z2, rmin2, rmax2, delta_r):
    # Compute thickness at each z
    thickness1 = rmax1 - rmin1
    thickness2 = rmax2 - rmin2
    
    if thickness1 == thickness2:
        if thickness1 == delta_r:
            return f"All z between {z1} and {z2} have thickness = {delta_r} cm"
        else:
            raise ValueError("Thickness does not change and does not match target delta.")
    
    # Linear interpolation to find z
    z = z1 + (z2 - z1) * (delta_r - thickness1) / (thickness2 - thickness1)
    return z

# ---- INPUT SECTION ----
# Define the two z-planes and their rmin/rmax values
z1 = 6         # cm
rmin1 = 1.0     # cm
rmax1 = 1.0     # cm

z2 = 15        # cm
rmin2 = 0.6     # cm
rmax2 = 2.59223 # cm

# Desired thickness (delta_r = rmax - rmin)
target_delta_r = 1.0  # cm

# ---- COMPUTE AND OUTPUT ----
try:
    result_z = interpolate_z_for_thickness(z1, rmin1, rmax1, z2, rmin2, rmax2, target_delta_r)
    print(f"At z = {result_z:.5f} cm, the thickness is {target_delta_r} cm.")
except ValueError as e:
    print("Error:", e)