import pyLCIO
import ROOT
import glob
import math

# Set up some options
max_events = -1

# Gather input files
fnames = glob.glob("/home/devlinjenkins/projects/NozzleSimOpti/simulation/mumu_H_bb_100Events/NoBlackhole/mumu_H_bb_100E.slcio")

# Set up histograms
hists = {}
hists["MCParticle_VertexMap_R_vs_Z_NoBlackHole"] = ROOT.TH2F("MCParticle_VertexMap_R_vs_Z_NoBlackHole", "MCParticle Vertex Map R vs Z No Black Hole", 50, -2600, 2600, 50, 0, 400)

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
            vertex = p.getVertex()
            x, y, z = vertex[0], vertex[1], vertex[2]
            radius = math.sqrt(x**2 + y**2)
            hists["MCParticle_VertexMap_R_vs_Z_NoBlackHole"].Fill(z, radius)

        event_count += 1

    reader.close()

# Make your plots
ROOT.gStyle.SetOptStat(0)
for i, h in enumerate(hists):
    c = ROOT.TCanvas("c%i" % i, "c%i" % i, 2800, 1600)  # Wider canvas

    # Set margins to leave space for axis titles
    c.SetLeftMargin(0.2)  # % of the canvas width
    c.SetRightMargin(0.2)  # % of the canvas width
    c.SetBottomMargin(0.15)  # Increased margin to fit x-axis title
    c.SetTopMargin(0.1)  # % of the canvas height

    # Hist formatting
    entries = hists[h].GetEntries()
    hists[h].SetXTitle("Vertex Z [mm]")  # x-axis label
    hists[h].SetYTitle("Vertex R [mm]")  # y-axis label
    hists[h].SetZTitle("Counts")  # z-axis label
    hists[h].SetMaximum(1652537)
    hists[h].Draw("COLZ")
    c.SetLogz()  # log scale z-axis

    # Add total entries text box
    pave_text = ROOT.TPaveText(0.68, 0.865, 0.78, 0.885, "NDC")
    pave_text.AddText(f"Entries: {int(entries)}")
    pave_text.SetFillColor(0)
    pave_text.SetTextColor(ROOT.kBlack)
    pave_text.SetTextSize(0.02)
    pave_text.SetBorderSize(1)
    pave_text.Draw()

    c.SaveAs("%s.png" % h)
