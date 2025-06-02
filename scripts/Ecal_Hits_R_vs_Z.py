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
hists["ECal Hits Z vs Radius"] = ROOT.TH2F("ECal Hits Z vs Radius", "ECal Hits Z vs Radius", 150, -3500, 3500, 150, 0, 2500)
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
        ECalbarrel_collection = event.getCollection("ECalBarrelCollection")
        ECalEndcap_collection = event.getCollection("ECalEndcapCollection")
            

        # Loop over the hits and fill histograms
        for hit in ECalbarrel_collection:                                       #loop
            energy = hit.getEnergy()                                            #get data we care about from collection
            position = hit.getPosition()                                               
            x, y, z = position[0], position[1], position[2]                     #given coords
            radius = math.sqrt(x**2 + y**2)                                     #calc radius     
            hists["ECal Hits Z vs Radius"].Fill(z, radius, energy)              #fill (x, y, weight)

        i+= 1

        for hit in ECalEndcap_collection:                                       #loop
            energy = hit.getEnergy()                                            #get data we care about from collection
            position = hit.getPosition()                                               
            x, y, z = position[0], position[1], position[2]                     #given coords
            radius = math.sqrt(x**2 + y**2)                                     #calc radius
            hists["ECal Hits Z vs Radius"].Fill(z, radius, energy)              #fill (x, y, weight)

        i+= 1

# Make your plots
ROOT.gStyle.SetOptStat(0)

for i, h in enumerate(hists):
    c = ROOT.TCanvas("c%i"%i, "c%i"%i)
    c.SetRightMargin(0.15)                                                      #Increase the right margin
    hists[h].SetXTitle("Z (mm)")                                                #y axis label
    hists[h].SetYTitle("R (mm)")                                                #y axis label
    hists[h].SetZTitle("Energy (GeV)")                                          #z axis label
    hists[h].Draw("COLZ")                                                       #"COLZ" gives color *must use*
    c.SaveAs("%s.png"%h)