## The radius of the nozzle is not constant and varies with z. This script is used to calculate the radius at a given z point by linearly interpolating between two known points.
## IMPORTANT! Does not work outside of 2 already defined Z points! Only use between 2 originally defined points! The Nozzle is not a straight line -- it has flat areas, and kinks. 
## Be careful of disrupting original geometry and always double check the calculated radii to the original geometry radii.

def interpolate_radius(z1, r1, z2, r2, z):
    if z1 == z2:
        raise ValueError("z1 and z2 cannot be the same value")
    return r1 + (r2 - r1) * (z - z1) / (z2 - z1)

# Values for z1, r1, z2, r2, and z

z1 = 6  # Example starting z point in cm
r1 = 1  # Radius at z1 in cm

z2 = 100  # Example ending z point in cm
r2 = 17.63 # Radius at z2 in cm

z = 75  # Intermediate z point where we want to calculate the radius

radius = interpolate_radius(z1, r1, z2, r2, z)
radius_at_z_minus_0_4 = interpolate_radius(z1, r1, z2, r2, z) - 0.4
# Print the results
print(f"Radius at z = {z} cm is {radius} cm")
print(f"Radius-0.4 at z = {z} cm is {radius_at_z_minus_0_4} cm")
