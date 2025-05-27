import pyLCIO
import ROOT
import glob
import math

# Set up some options
max_events = -1

# Gather input files
fnames = glob.glob("/scratch/devlinjenkins/work/reconstruction/Output_REC.000.slcio")

# Set up histograms
hists = {}                                                                          
hists["Reconstructed BJet Locations from Momentum"] = ROOT.TH2F("Reconstructed BJet Locations from Momentum", "Reconstructed BJet Locations from Momentum", 50, 0, math.pi, 50, -math.pi, math.pi)
                                                                                         #change according to data

# Loop over events
i = 0
for f in fnames:
    reader = pyLCIO.IOIMPL.LCFactory.getInstance().createLCReader()
    reader.open(f)

    for event in reader:
        if max_events > 0 and i >= max_events:
            break
        if i % 100 == 0:
            print("Processing event %i."%i)

        # Get the collections we care about
        JetOut_collection = event.getCollection("JetOut")

        # Loop over the hits and fill histograms
        for jet in JetOut_collection:                                           #loop
            energy = jet.getEnergy()                                            #get data we care about from collection
            momentum = jet.getMomentum()                                        
            px, py, pz = momentum[0], momentum[1], momentum[2]                 
            radius = math.sqrt(px**2 + py**2 + pz**2)        
            theta = math.acos(pz/radius)                                        #calc theta
            phi = math.atan2(py,px)                                             #calc phi
            hists["Reconstructed BJet Locations from Momentum"].Fill(theta, phi, energy)      #fill (x, y, weight)

        i+= 1
    reader.close()

# Make your plots
ROOT.gStyle.SetOptStat(0)
for i, h in enumerate(hists):
    c = ROOT.TCanvas("c%i"%i, "c%i"%i)
    c.SetRightMargin(0.15)                                                      #Increase the right margin
    hists[h].SetXTitle("Theta [rads]")                                          #y axis label
    hists[h].SetYTitle("Phi [rads]")                                            #y axis label
    hists[h].SetZTitle("Energy [GeV*?]")
    hists[h].Draw("COLZ")                                                       #"COLZ" gives color *must use*
    c.SaveAs("%s.png"%h)

output_file = ROOT.TFile("ECalHistograms.root", "RECREATE")
for h in hists.values():
    h.Write()
output_file.Close()