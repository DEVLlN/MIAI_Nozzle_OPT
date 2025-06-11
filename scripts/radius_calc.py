## The radius of the nozzle is not constant and varies with z. This script is used to calculate rmin or rmax at a given z point by linearly interpolating between two known z positions.
## If both rmin and rmax are provided, it also calculates the delta radius (rmax - rmin).
## IMPORTANT! Only valid between two known z values. The nozzle may include flat segments or non-linear transitions. Always verify against the original geometry.

def interpolate_radius(z1, r1, z2, r2, z):
    if z1 == z2:
        raise ValueError("z1 and z2 cannot be the same value")
    return r1 + (r2 - r1) * (z - z1) / (z2 - z1)

# ---- INPUT SECTION ----
# Use 'na' for the one you do NOT want to calculate

z1 = 6
rmin1 = 1
rmax1 = 1

z2 = 15
rmin2 = 0.6
rmax2 = 2.59223

# Desired z position to calculate radius at
z = 10.5176

# ------------------------

radius_results = {}

# Interpolate rmin if provided
if rmin1 != 'na' and rmin2 != 'na':
    rmin_z = interpolate_radius(z1, float(rmin1), z2, float(rmin2), z)
    radius_results['rmin'] = rmin_z
    print(f"rmin at z = {z} cm is {rmin_z:.5f} cm")

# Interpolate rmax if provided
if rmax1 != 'na' and rmax2 != 'na':
    rmax_z = interpolate_radius(z1, float(rmax1), z2, float(rmax2), z)
    radius_results['rmax'] = rmax_z
    print(f"rmax at z = {z} cm is {rmax_z:.5f} cm")

# Compute delta R if both are present
if 'rmin' in radius_results and 'rmax' in radius_results:
    delta_r = radius_results['rmax'] - radius_results['rmin']
    print(f"Delta R (rmax - rmin) at z = {z} cm is {delta_r:.5f} cm")