import ROOT

def highlight_overlaps(filename="detector.xml.root", tolerance=0.001):
    ROOT.TGeoManager.Import(filename)

    geom = ROOT.gGeoManager
    geom.CheckOverlaps(tolerance)
    overlaps = geom.GetListOfOverlaps()

    if not overlaps or overlaps.GetEntries() == 0:
        print("No overlaps found.")
        return

    print(f"Overlaps found: {overlaps.GetEntries()}")

    for i in range(overlaps.GetEntries()):
        ov = overlaps.At(i)
        vol1 = ov.GetVolume1()
        vol2 = ov.GetVolume2()

        if vol1:
            vol1.SetLineColor(ROOT.kRed + 2)
            vol1.SetTransparency(50)
        if vol2:
            vol2.SetLineColor(ROOT.kMagenta + 1)
            vol2.SetTransparency(50)

        name1 = vol1.GetName() if vol1 else "null"
        name2 = vol2.GetName() if vol2 else "null"
        print(f"Overlap between: {name1} and {name2}")

    # Optional: draw top volume
    # geom.GetTopVolume().Draw("ogl")

    # Save updated geometry
    geom.Export("highlighted.root")
    print("Saved highlighted geometry to 'highlighted.root'.")

# Run if called as a script
if __name__ == "__main__":
    highlight_overlaps("detector.xml.root")
