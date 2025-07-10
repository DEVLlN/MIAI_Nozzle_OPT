import pyLCIO
import ROOT
import glob
import math
import os

# Set up some options
max_events = -1

# Gather input files
fnames = [
    "/home/devlinjenkins/projects/NozzleSimOpti/simulation/geometries/MAIA_v0/mumu_H_bb_100E_MAIA.slcio",
    "/home/devlinjenkins/projects/NozzleSimOpti/simulation/geometries/MAIA_v0_Blackhole/nozzle_variants_v2/nozzle_z10p5176_rmaxMinus0/mumu_H_bb_100E_MAIA_nozzle_z10p5176_rmaxMinus0.slcio",
    "/home/devlinjenkins/projects/NozzleSimOpti/simulation/geometries/MAIA_v0_Blackhole/nozzle_variants_v2/nozzle_z10p5176_rmaxMinus0p6/mumu_H_bb_100E_MAIA_nozzle_z10p5176_rmaxMinus0p6.slcio",
    "/home/devlinjenkins/projects/NozzleSimOpti/simulation/geometries/MAIA_v0_Blackhole/nozzle_variants_v2/nozzle_z10p5176_rmaxMinus0p11/mumu_H_bb_100E_MAIA_nozzle_z10p5176_rmaxMinus0p11.slcio",
    "/home/devlinjenkins/projects/NozzleSimOpti/simulation/geometries/MAIA_v0_Blackhole/nozzle_variants_v2/nozzle_z10p5176_rmaxMinus0p16/mumu_H_bb_100E_MAIA_nozzle_z10p5176_rmaxMinus0p16.slcio",
    "/home/devlinjenkins/projects/NozzleSimOpti/simulation/geometries/MAIA_v0_Blackhole/nozzle_variants_v2/nozzle_z10p5176_rmaxMinus0p21/mumu_H_bb_100E_MAIA_nozzle_z10p5176_rmaxMinus0p21.slcio",
]

# Short labels for legend
short_labels = [
    "No BH",
    "SD=1cm",
    "SD=6cm",
    "SD=11cm",
    "SD=16cm",
    "SD=21cm",
]

# Define improved colors for higher contrast and distinguishability
colors = [
    ROOT.kBlack,        # No BH
    ROOT.kBlue+1,       # Light blue
    ROOT.kRed+1,        # Light red
    ROOT.kGreen+2,      # Green
    ROOT.kOrange+7,     # Orange
    ROOT.kMagenta+1,    # Magenta
]

# Set up histograms
hists = {}

# Loop over files to create histograms
for idx, f in enumerate(fnames):
    hist_name = f"MCParticle_Pos_Theta_{idx}"
    hists[hist_name] = ROOT.TH1F(hist_name, "", 50, 0, math.pi)

# Check which files exist
print("\nChecking file existence:")
existing_files = []
for idx, f in enumerate(fnames):
    if os.path.exists(f):
        print(f"✓ File {idx}: {short_labels[idx]}")
        existing_files.append(idx)
    else:
        print(f"✗ File {idx}: {short_labels[idx]} - NOT FOUND")

# Loop over events
for idx in existing_files:
    f = fnames[idx]
    event_count = 0
    try:
        reader = pyLCIO.IOIMPL.LCFactory.getInstance().createLCReader()
        reader.open(f)
        
        print(f"\nProcessing: {short_labels[idx]}")

        for event in reader:
            if max_events > 0 and event_count >= max_events:
                break
            if event_count % 1000 == 0 and event_count > 0:
                print(f"  Event {event_count}...")

            # Get the collections we care about
            try:
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

            except Exception as e:
                if event_count == 0:  # Only print once
                    print(f"  Warning: Could not process MCParticle collection: {e}")

            event_count += 1

        reader.close()
        print(f"  Processed {event_count} events, {int(hists[f'MCParticle_Pos_Theta_{idx}'].GetEntries())} particles")
        
    except Exception as e:
        print(f"Error processing file {short_labels[idx]}: {e}")
        continue

# Make your plots
ROOT.gStyle.SetOptStat(0)

c1 = ROOT.TCanvas("c1", "c1", 3200, 1600)
c1.SetLeftMargin(0.10)
c1.SetRightMargin(0.25)  # Large right margin for legend
c1.SetBottomMargin(0.10)
c1.SetTopMargin(0.08)
c1.SetLogy()

# Draw histograms
first_drawn = False
for idx in existing_files:
    hist_name = f"MCParticle_Pos_Theta_{idx}"
    
    # Skip empty histograms
    if hists[hist_name].GetEntries() == 0:
        print(f"Skipping empty histogram: {short_labels[idx]}")
        continue
    
    # Set color
    hists[hist_name].SetLineColor(colors[idx])
    
    # Set solid line style for all
    hists[hist_name].SetLineStyle(1)
    hists[hist_name].SetLineWidth(3 if idx == 0 else 2)
    
    # Set axis properties
    hists[hist_name].SetMinimum(1)
    hists[hist_name].SetMaximum(1e8)
    hists[hist_name].SetXTitle("MCParticle Prod Pos #theta [rad]")
    hists[hist_name].GetXaxis().SetTitleSize(0.04)
    hists[hist_name].GetXaxis().SetLabelSize(0.035)
    hists[hist_name].GetYaxis().SetTitle("Counts")
    hists[hist_name].GetYaxis().SetTitleSize(0.04)
    hists[hist_name].GetYaxis().SetLabelSize(0.035)
    
    if not first_drawn:
        hists[hist_name].Draw("HIST")
        first_drawn = True
    else:
        hists[hist_name].Draw("HIST SAME")

legend = ROOT.TLegend(0.75, 0.15, 0.985, 0.88)
legend.SetBorderSize(1)
legend.SetFillStyle(0)
legend.SetTextSize(0.016)
legend.SetNColumns(1)

# Add header
legend.SetHeader("Configuration", "C")

# Add entries for existing files with data
for idx in existing_files:
    hist_name = f"MCParticle_Pos_Theta_{idx}"
    if hists[hist_name].GetEntries() > 0:
        legend.AddEntry(hists[hist_name], short_labels[idx], "l")

legend.Draw()

title = ROOT.TPaveText(0.10, 0.94, 0.80, 0.98, "NDC")
title.AddText("MCParticle Position Theta at Different Nozzle Blackholes, Nozzle Cutoff at 10.5176cm")
title.SetFillColor(0)
title.SetBorderSize(0)
title.SetTextAlign(12)
title.SetTextSize(0.035)
title.Draw()


c1.SaveAs("MCParticle_Pos_Theta_Z10p5176.png")

print("\nPlots saved as:")
print("  - MCParticle_Pos_Theta_colors.png (11 different colors + line styles)")
print(f"\nProcessed {len(existing_files)} files successfully")