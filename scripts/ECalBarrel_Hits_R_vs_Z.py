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
hists["ECalBarrel_Hits_R_vs_Z"] = ROOT.TH2F("ECalBarrel_Hits_R_vs_Z", "ECalBarrel_Hits_R_vs_Z", 150, 1450, 1900, 150, 0, 2500)
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
            collection = event.getCollection("ECalBarrelCollection")

        # Loop over the hits and fill histograms
        for hit in collection:                                                  #loop
            energy = hit.getEnergy()                                            #get data we care about from collection
            position = hit.getPosition()                                               
            x, y, z = position[0], position[1], position[2]                     #given coords
            radius = math.sqrt(x**2 + y**2)                                      
            hists["ECalBarrel_Hits_R_vs_Z"].Fill(radius, z, energy)             #fill (x, y, weight)

        i+= 1

# Make your plots
for i, h in enumerate(hists):
    c = ROOT.TCanvas("c%i"%i, "c%i"%i)
    hists[h].SetXTitle("R [cm]")                                                     #x axis label
    hists[h].SetYTitle("Z [cm]")                                                     #y axis label
    hists[h].Draw("COLZ")                                                    
    c.SaveAs("%s.png"%h)