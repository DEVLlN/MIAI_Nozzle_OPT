import pyLCIO
import ROOT
import glob
import math

# Set up some options
max_events = -1

# Gather input files
fnames = glob.glob("/scratch/devlinjenkins/work/simulation/mumu_H_bb_100Events/noTrackLimit/mumu_H_bb_100E.slcio")

# Set up histograms
hists = {}  # change according to data
hists["MCParticle_VertexMap_Z_default_geo"] = ROOT.TH1F("MCParticle_VertexMap_Z_default_geo", "MCParticle Vertex Map Z", 50, -1000, 1000)

# Loop over events
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
            z = vertex[2]  # Z coordinate
            hists["MCParticle_VertexMap_Z_default_geo"].Fill(z)

        event_count += 1

    reader.close()

# Make your plots
ROOT.gStyle.SetOptStat(0)
for i, h in enumerate(hists):
    c = ROOT.TCanvas("c%i" % i, "c%i" % i, 2000, 1600)  # 1x1 pixels canvas

    # Set margins to leave space for axis titles
    c.SetLeftMargin(0.2)  # % of the canvas width
    c.SetRightMargin(0.2)  # % of the canvas width
    c.SetBottomMargin(0.1)  # % of the canvas height
    c.SetTopMargin(0.1)  # % of the canvas height

    # Hists formatting
    entries = hists[h].GetEntries()
    hists[h].SetXTitle("Vertex Z [mm]")  # x-axis label
    hists[h].SetYTitle("Counts")  # y-axis label
    #hists[h].SetMaximum(1652537)
    hists[h].Draw("HIST")  # Draw histogram
    
    # Add total entries text box
    pave_text = ROOT.TPaveText(0.68, 0.865, 0.78, 0.885, "NDC")
    pave_text.AddText(f"Entries: {int(entries)}")
    pave_text.SetFillColor(0)
    pave_text.SetTextColor(ROOT.kBlack)
    pave_text.SetTextSize(0.02)
    pave_text.SetBorderSize(1)
    pave_text.Draw()

    c.SaveAs("%s.png" % h)
