import pyLCIO
import ROOT
import glob
import math

# Set up some options
max_events = -1

# Gather input files
fnames = [
    "/scratch/devlinjenkins/work/simulation/mumu_H_bb_100Events/noTrackLimit/mumu_H_bb_100E.slcio",
    "/scratch/devlinjenkins/work/simulation/mumu_H_bb_100Events/full_KZ_v1_1/mumu_H_bb_100E_TIP_KZv1_1.slcio",
    "/scratch/devlinjenkins/work/simulation/mumu_H_bb_100Events/full_KZ_v1_3/mumu_H_bb_100E_FULL_KZv1_3_FULL.slcio",
    "/scratch/devlinjenkins/work/simulation/mumu_H_bb_100Events/full_KZ_v1_5/mumu_H_bb_100E_FULL_KZv1_5_FULL.slcio",
    "/scratch/devlinjenkins/work/simulation/mumu_H_bb_100Events/full_KZ_v1_7/mumu_H_bb_100E_full_KZv1_7_FULL.slcio",
    "/scratch/devlinjenkins/work/simulation/mumu_H_bb_100Events/full_KZ_v1_9/mumu_H_bb_100E_FULL_KZv1_9_FULL.slcio",
    "/scratch/devlinjenkins/work/simulation/mumu_H_bb_100Events/full_KZ_v1_10/mumu_H_bb_100E_BLACKHOLE_NOZZLE.slcio"
]

# Descriptive names for each file
descriptive_names = [
    "Default Geometry",
    "Blackhole 2cm deep",
    "Blackhole 4cm deep",
    "Blackhole 6cm deep",
    "Blackhole 8cm deep",
    "Blackhole 10cm deep",
    "Full Nozzle Blackhole"
]

# Set up histograms
hists = {}
colors = [ROOT.kOrange, ROOT.kOrange-3, ROOT.kGreen+2, ROOT.kTeal, ROOT.kAzure+7, ROOT.kBlue+1, ROOT.kGray+3]

# Loop over files to create histograms
for idx, f in enumerate(fnames):
    hist_name = f"MCParticle_Pos_Theta_{idx}"
    hists[hist_name] = ROOT.TH1F(hist_name, "", 50, 0, math.pi)  # No title here

# Loop over events
event_count = 0
for idx, f in enumerate(fnames):
    reader = pyLCIO.IOIMPL.LCFactory.getInstance().createLCReader()
    reader.open(f)

    for event in reader:
        if max_events > 0 and event_count >= max_events:
            break
        if event_count % 100 == 0:
            print(f"Processing event {event_count} for {descriptive_names[idx]}.")

        # Get the collections we care about
        collection = event.getCollection("MCParticle")

        # Loop over the hits and fill histograms
        for p in collection:
            vertex = p.getVertex()
            x, y, z = vertex[0], vertex[1], vertex[2]
            radius = math.sqrt(x**2 + y**2 + z**2)

            # Check if radius is not zero to avoid division by zero
            if radius != 0:
                theta = math.acos(z / radius)
                hist_name = f"MCParticle_Pos_Theta_{idx}"
                hists[hist_name].Fill(theta)

        event_count += 1

    reader.close()

# Make your plots
ROOT.gStyle.SetOptStat(0)
c = ROOT.TCanvas("c", "c", 2000, 1600)  # 1x1 pixels canvas

# Set margins to leave space for axis titles
c.SetLeftMargin(0.2)  # % of the canvas width
c.SetRightMargin(0.2)  # % of the canvas width
c.SetBottomMargin(0.1)  # % of the canvas height
c.SetTopMargin(0.1)  # % of the canvas height

# Set log scale for y-axis
c.SetLogy()

# Draw histograms with different colors
legend = ROOT.TLegend(0.7, 0.7, 0.9, 0.9)
for idx, hist_name in enumerate(hists):
    hists[hist_name].SetLineColor(colors[idx % len(colors)])
    hists[hist_name].SetMinimum(1)    # Set minimum value for y-axis
    hists[hist_name].SetMaximum(1e8)  # Set maximum value for y-axis
    hists[hist_name].SetLineWidth(2)  # Set line width
    hists[hist_name].SetXTitle("MCParticle Prod Pos #theta [rad]")  # x-axis title

    if idx == 0:
        hists[hist_name].Draw()
    else:
        hists[hist_name].Draw("SAME")
    legend.AddEntry(hists[hist_name], descriptive_names[idx], "l")

legend.Draw()

# Add title to the canvas
title = ROOT.TPaveText(0.2, 0.92, 0.8, 0.98, "NDC")
title.AddText("MCParticle Position Theta at Different Nozzle Blackhole Radii")
title.SetFillColor(0)
title.SetBorderSize(0)
title.SetFillColor(0)
title.SetTextAlign(22)  # Center alignment
title.SetTextSize(0.04)
title.Draw()

c.SaveAs("MCParticle_Pos_Theta.png")
