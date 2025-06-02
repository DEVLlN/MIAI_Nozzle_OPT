import ROOT
import os

# Open the ROOT file
f = ROOT.TFile.Open("/home/devlinjenkins/projects/NozzleSimOpti/simulation/geometries/MuColl_10TeV_v0A_Modded_Nozzle/MuColl_10TeV_Hammer_V1.xml.root")

# Try to extract the TGeoManager object
geo_manager = None
for key in f.GetListOfKeys():
    obj = key.ReadObj()
    if obj.InheritsFrom("TGeoManager"):
        geo_manager = obj
        break

if geo_manager is None:
    raise RuntimeError("TGeoManager not found in the ROOT file.")

# Set it globally so ROOT knows it's the current geometry
ROOT.gGeoManager = geo_manager

# Draw the geometry using OpenGL
geo_manager.GetTopVolume().Draw("ogl")

# Create a canvas for rendering
c = ROOT.TCanvas("c", "Spinning Geometry", 800, 800)
c.cd()

# Output directory for frames
output_dir = "frames"
os.makedirs(output_dir, exist_ok=True)

# Rotate and export frames every 5 degrees
for angle in range(0, 360, 5):
    c.SetPhi(angle)     # Rotate horizontally
    c.SetTheta(30)      # Fixed vertical angle (you can adjust)
    c.Update()
    filename = f"{output_dir}/frame_{angle:03d}.png"
    c.SaveAs(filename)

print("✅ Frame export complete.")
