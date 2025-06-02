import pyLCIO
import ROOT
import glob
import math

# Set up some options
max_events = -1

# Z and radius ranges for the nozzle region to exclude with a 5mm buffer zone
buffer = 5  # 5mm buffer

# Define nozzle segments with a 5mm buffer zone for both positive and negative Z
nozzle_segments = [
    (60 - buffer, 150 + buffer, 18.238 + buffer),
    (150 - buffer, 193 + buffer, 19.465 + buffer),
    (193 - buffer, 215 + buffer, 21.50 + buffer),
    (215 - buffer, 219 + buffer, 21.50 + buffer),
    (219 - buffer, 219 + buffer, 21.50 + buffer),
    (-219 - buffer, -219 + buffer, 21.50 + buffer),
    (-215 - buffer, -193 + buffer, 21.50 + buffer),
    (-193 - buffer, -150 + buffer, 19.465 + buffer),
    (-150 - buffer, -60 + buffer, 18.238 + buffer)
]

z_nozzle_min = min(segment[0] for segment in nozzle_segments)
z_nozzle_max = max(segment[1] for segment in nozzle_segments)

# Radius function based on the linear relationship for multiple segments
def radius_at_z(z):
    for z_start, z_end, r_max in nozzle_segments:
        if z_start <= z <= z_end:
            return r_max
    return float('inf')

def gather_files(patterns):
    files = []
    for pattern in patterns:
        files.extend(glob.glob(pattern))
    return files

def create_histograms(geo_versions):
    hists = {}
    for version in geo_versions:
        hists[f"MCParticle_VertexMap_Z_{version}_noNozzle"] = ROOT.TH1F(f"MCParticle_VertexMap_Z_{version}_noNozzle", f"{version} Geo MCParticle Vertex Map Z w/ Nozzle Excluded", 50, -2600, 2600)
        hists[f"MCParticle_VertexMap_Z_{version}_withNozzle"] = ROOT.TH1F(f"MCParticle_VertexMap_Z_{version}_withNozzle", f"{version} Geo MCParticle Vertex Map Z w/ Nozzle Included", 50, -2600, 2600)
    return hists

def process_files(fnames, with_nozzle_hist, without_nozzle_hist):
    event_count = 0
    for f in fnames:
        reader = pyLCIO.IOIMPL.LCFactory.getInstance().createLCReader()
        reader.open(f)

        for event in reader:
            if max_events > 0 and event_count >= max_events:
                break
            if event_count % 100 == 0:
                print("Processing event %i." % event_count)

            # Get the collections we care about
            collection = event.getCollection("MCParticle")

            # Loop over the hits and fill histograms
            for p in collection:
                vertex = p.getVertex()  # vertex position in mm
                x, y, z = vertex[0], vertex[1], vertex[2]
                r = math.sqrt(x**2 + y**2)  # Calculate the cylindrical radius

                # Fill histogram with nozzle included
                hists[with_nozzle_hist].Fill(z)

                # Exclude vertices within the nozzle region based on Z and variable radius
                if radius_at_z(z) >= r:
                    continue

                # Fill histogram with nozzle excluded
                hists[without_nozzle_hist].Fill(z)

            event_count += 1

        reader.close()

def set_max_scale(hists, max_scale):
    for hist in hists.values():
        hist.SetMaximum(max_scale)

def save_histograms(hists, filename):
    output_file = ROOT.TFile(filename, "RECREATE")
    for h in hists.values():
        h.Write()
    output_file.Close()
    print(f"Histograms have been saved to {filename}")

def plot_histograms(hists, versions, filename_with, filename_without):
    ROOT.gStyle.SetOptStat(0)
    legend_text_size = 0.02

    # Canvas for with nozzle
    c1 = ROOT.TCanvas("c1", "Canvas with Nozzle Included", 800, 600)
    colors = [ROOT.kBlue, ROOT.kRed, ROOT.kGreen, ROOT.kOrange, ROOT.kMagenta+3, ROOT.kPink+10]
    
    for i, version in enumerate(versions):
        hists[f"MCParticle_VertexMap_Z_{version}_withNozzle"].SetLineColor(colors[i % len(colors)])
        if i == 0:
            hists[f"MCParticle_VertexMap_Z_{version}_withNozzle"].GetXaxis().SetTitle("Z position (mm)")
            hists[f"MCParticle_VertexMap_Z_{version}_withNozzle"].Draw("HIST")
        else:
            hists[f"MCParticle_VertexMap_Z_{version}_withNozzle"].Draw("HIST SAME")

    c1.SetLogy()
    legend1 = c1.BuildLegend(0.15, 0.78, 0.45, 0.88)
    legend1.SetTextSize(legend_text_size)
    legend1.SetBorderSize(0)  # Remove the border around the legend
    c1.SaveAs(filename_with)

    # Canvas for without nozzle
    c2 = ROOT.TCanvas("c2", "Canvas with Nozzle Excluded", 800, 600)
    for i, version in enumerate(versions):
        hists[f"MCParticle_VertexMap_Z_{version}_noNozzle"].SetLineColor(colors[i % len(colors)])
        if i == 0:
            hists[f"MCParticle_VertexMap_Z_{version}_noNozzle"].GetXaxis().SetTitle("Z position (mm)")
            hists[f"MCParticle_VertexMap_Z_{version}_noNozzle"].Draw("HIST")
        else:
            hists[f"MCParticle_VertexMap_Z_{version}_noNozzle"].Draw("HIST SAME")

    c2.SetLogy()
    legend2 = c2.BuildLegend(0.15, 0.78, 0.45, 0.88)
    legend2.SetTextSize(legend_text_size)
    legend2.SetBorderSize(0)  # Remove the border around the legend
    c2.SaveAs(filename_without)

# Define geometry versions and corresponding file patterns
geo_versions = {
    "default": ["/scratch/devlinjenkins/work/simulation/mumu_H_bb_100Events/noTrackLimit/mumu_H_bb_100E.slcio"],
    "v1": ["/scratch/devlinjenkins/work/simulation/mumu_H_bb_100Events/full_KZ_v1_0/mumu_H_bb_100E_TIP_KZv1_0_FULL.slcio"],
    #"v1.1": ["/scratch/devlinjenkins/work/simulation/mumu_H_bb_100Events/full_KZ_v1_1/mumu_H_bb_100E_TIP_KZv1_1_FULL.slcio"],
    #"v1.2": ["/scratch/devlinjenkins/work/simulation/mumu_H_bb_100Events/full_KZ_v1_2/mumu_H_bb_100E_TIP_KZv1_2_FULL.slcio"],
    #"v1.3": ["/scratch/devlinjenkins/work/simulation/mumu_H_bb_100Events/full_KZ_v1_3/mumu_H_bb_100E_TIP_KZv1_3_FULL.slcio"],
    "v1.6": ["/scratch/devlinjenkins/work/simulation/mumu_H_bb_100Events/full_KZ_v1_6/mumu_H_bb_100E_TIP_KZv1_6_FULL.slcio"],
    "v1.8": ["/scratch/devlinjenkins/work/simulation/mumu_H_bb_100Events/full_KZ_v1_8/mumu_H_bb_100E_TIP_KZv1_8_FULL.slcio"]

}

# Gather input files
input_files = {version: gather_files(patterns) for version, patterns in geo_versions.items()}

# Create histograms
hists = create_histograms(geo_versions.keys())

# Process files and fill histograms
for version in geo_versions.keys():
    process_files(input_files[version], f"MCParticle_VertexMap_Z_{version}_withNozzle", f"MCParticle_VertexMap_Z_{version}_noNozzle")

# Set maximum scale for all histograms
set_max_scale(hists, 1e6)

# Save histograms to a ROOT file
save_histograms(hists, "MCParticle_VertexMap_Z_comparison.root")

# Plot the histograms for visual inspection
plot_histograms(hists, geo_versions.keys(), "MCParticle_VertexMap_Z_withNozzle_overlay.png", "MCParticle_VertexMap_Z_noNozzle_overlay.png")
