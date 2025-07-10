import pyLCIO
import ROOT
import os
import glob
import math
from pathlib import Path

class SLCIOAnalyzer:
    def __init__(self, base_dir, output_dir="plots", max_events=-1):
        """
        Initialize the SLCIO analyzer.
        
        Args:
            base_dir: Base directory to search for .slcio files
            output_dir: Directory to save output plots
            max_events: Maximum number of events to process (-1 for all)
        """
        self.base_dir = base_dir
        self.output_dir = output_dir
        self.max_events = max_events
        self.datasets = {}
        
        # Create output directory if it doesn't exist
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        
        # Set up ROOT style
        ROOT.gStyle.SetOptStat(0)
        ROOT.gROOT.SetBatch(True)  # Run in batch mode (no display)
    
    def find_slcio_files(self):
        """Find all .slcio files in the base directory and subdirectories."""
        pattern = os.path.join(self.base_dir, "**/*.slcio")
        files = glob.glob(pattern, recursive=True)
        
        # Group files by dataset name (extracted from path)
        for file_path in files:
            # Extract dataset name from file path
            rel_path = os.path.relpath(file_path, self.base_dir)
            dataset_name = self._extract_dataset_name(rel_path)
            
            if dataset_name not in self.datasets:
                self.datasets[dataset_name] = []
            self.datasets[dataset_name].append(file_path)
        
        return self.datasets
    
    def _extract_dataset_name(self, rel_path):
        """
        Extract a meaningful dataset name from the relative path.
        You can customize this method based on your naming convention.
        """
        # Example: use directory name as dataset name
        parts = rel_path.split(os.sep)
        if len(parts) > 1:
            # Use parent directory name
            return parts[-2]
        else:
            # Use file name without extension
            return os.path.splitext(parts[0])[0]
    
    def create_histograms(self, dataset_name):
        """Create histograms for a specific dataset."""
        hists = {}
        
        # Create different histogram types
        hist_name_base = f"MCParticle_VertexMap_R_vs_Z_{dataset_name}"
        
        # 2D histogram: R vs Z
        hists["r_vs_z"] = ROOT.TH2F(
            hist_name_base,
            f"MCParticle Vertex Map R vs Z - {dataset_name}",
            50, -2600, 2600,  # Z axis bins
            50, 0, 400        # R axis bins
        )
        
        # Additional 1D histograms
        hists["z_dist"] = ROOT.TH1F(
            f"MCParticle_Z_Distribution_{dataset_name}",
            f"MCParticle Z Distribution - {dataset_name}",
            100, -2600, 2600
        )
        
        hists["r_dist"] = ROOT.TH1F(
            f"MCParticle_R_Distribution_{dataset_name}",
            f"MCParticle R Distribution - {dataset_name}",
            100, 0, 400
        )
        
        # Energy histogram (if available)
        hists["energy"] = ROOT.TH1F(
            f"MCParticle_Energy_{dataset_name}",
            f"MCParticle Energy - {dataset_name}",
            100, 0, 100  # Adjust range as needed
        )
        
        return hists
    
    def process_dataset(self, dataset_name, file_list):
        """Process all files for a specific dataset."""
        print(f"\nProcessing dataset: {dataset_name}")
        print(f"Number of files: {len(file_list)}")
        
        # Create histograms for this dataset
        hists = self.create_histograms(dataset_name)
        
        event_count = 0
        
        for file_path in file_list:
            print(f"  Processing file: {os.path.basename(file_path)}")
            
            reader = pyLCIO.IOIMPL.LCFactory.getInstance().createLCReader()
            reader.open(file_path)
            
            for event in reader:
                if self.max_events > 0 and event_count >= self.max_events:
                    break
                
                if event_count % 1000 == 0:
                    print(f"    Processing event {event_count}...")
                
                # Process MCParticle collection
                try:
                    collection = event.getCollection("MCParticle")
                    
                    for particle in collection:
                        vertex = particle.getVertex()
                        x, y, z = vertex[0], vertex[1], vertex[2]
                        radius = math.sqrt(x**2 + y**2)
                        energy = particle.getEnergy()
                        
                        # Fill histograms
                        hists["r_vs_z"].Fill(z, radius)
                        hists["z_dist"].Fill(z)
                        hists["r_dist"].Fill(radius)
                        hists["energy"].Fill(energy)
                
                except Exception as e:
                    print(f"    Warning: Could not process MCParticle collection: {e}")
                
                event_count += 1
            
            reader.close()
            
            if self.max_events > 0 and event_count >= self.max_events:
                break
        
        print(f"  Total events processed: {event_count}")
        
        return hists, event_count
    
    def save_plots(self, dataset_name, hists, event_count):
        """Save plots for a specific dataset."""
        dataset_dir = os.path.join(self.output_dir, dataset_name)
        Path(dataset_dir).mkdir(parents=True, exist_ok=True)
        
        # Save 2D histogram
        c1 = ROOT.TCanvas(f"c_{dataset_name}_2d", f"c_{dataset_name}_2d", 1400, 1000)
        c1.SetLeftMargin(0.12)
        c1.SetRightMargin(0.15)
        c1.SetBottomMargin(0.12)
        c1.SetTopMargin(0.08)
        
        h2d = hists["r_vs_z"]
        h2d.SetXTitle("Vertex Z [mm]")
        h2d.SetYTitle("Vertex R [mm]")
        h2d.SetZTitle("Counts")
        h2d.GetXaxis().SetTitleSize(0.04)
        h2d.GetYaxis().SetTitleSize(0.04)
        h2d.GetZaxis().SetTitleSize(0.04)
        h2d.Draw("COLZ")
        c1.SetLogz()
        
        # Add statistics box
        pave = ROOT.TPaveText(0.65, 0.92, 0.85, 0.97, "NDC")
        pave.AddText(f"Entries: {int(h2d.GetEntries())}")
        pave.SetFillColor(0)
        pave.SetTextSize(0.025)
        pave.SetBorderSize(1)
        pave.Draw()
        
        c1.SaveAs(os.path.join(dataset_dir, "vertex_map_r_vs_z.png"))
        c1.SaveAs(os.path.join(dataset_dir, "vertex_map_r_vs_z.pdf"))
        
        # Save 1D histograms
        # Z distribution
        c2 = ROOT.TCanvas(f"c_{dataset_name}_z", f"c_{dataset_name}_z", 1000, 800)
        c2.SetLeftMargin(0.12)
        c2.SetBottomMargin(0.12)
        
        h_z = hists["z_dist"]
        h_z.SetLineColor(ROOT.kBlue)
        h_z.SetLineWidth(2)
        h_z.SetXTitle("Vertex Z [mm]")
        h_z.SetYTitle("Counts")
        h_z.GetXaxis().SetTitleSize(0.04)
        h_z.GetYaxis().SetTitleSize(0.04)
        h_z.Draw("HIST")
        c2.SetLogy()
        
        c2.SaveAs(os.path.join(dataset_dir, "z_distribution.png"))
        c2.SaveAs(os.path.join(dataset_dir, "z_distribution.pdf"))
        
        # R distribution
        c3 = ROOT.TCanvas(f"c_{dataset_name}_r", f"c_{dataset_name}_r", 1000, 800)
        c3.SetLeftMargin(0.12)
        c3.SetBottomMargin(0.12)
        
        h_r = hists["r_dist"]
        h_r.SetLineColor(ROOT.kRed)
        h_r.SetLineWidth(2)
        h_r.SetXTitle("Vertex R [mm]")
        h_r.SetYTitle("Counts")
        h_r.GetXaxis().SetTitleSize(0.04)
        h_r.GetYaxis().SetTitleSize(0.04)
        h_r.Draw("HIST")
        c3.SetLogy()
        
        c3.SaveAs(os.path.join(dataset_dir, "r_distribution.png"))
        c3.SaveAs(os.path.join(dataset_dir, "r_distribution.pdf"))
        
        # Energy distribution
        c4 = ROOT.TCanvas(f"c_{dataset_name}_e", f"c_{dataset_name}_e", 1000, 800)
        c4.SetLeftMargin(0.12)
        c4.SetBottomMargin(0.12)
        
        h_e = hists["energy"]
        h_e.SetLineColor(ROOT.kGreen+2)
        h_e.SetLineWidth(2)
        h_e.SetXTitle("Energy [GeV]")
        h_e.SetYTitle("Counts")
        h_e.GetXaxis().SetTitleSize(0.04)
        h_e.GetYaxis().SetTitleSize(0.04)
        h_e.Draw("HIST")
        c4.SetLogy()
        
        c4.SaveAs(os.path.join(dataset_dir, "energy_distribution.png"))
        c4.SaveAs(os.path.join(dataset_dir, "energy_distribution.pdf"))
        
        # Save summary info
        with open(os.path.join(dataset_dir, "summary.txt"), "w") as f:
            f.write(f"Dataset: {dataset_name}\n")
            f.write(f"Total events processed: {event_count}\n")
            f.write(f"Total MCParticles: {int(h2d.GetEntries())}\n")
            f.write(f"Mean Z: {h_z.GetMean():.2f} mm\n")
            f.write(f"Mean R: {h_r.GetMean():.2f} mm\n")
            f.write(f"Mean Energy: {h_e.GetMean():.2f} GeV\n")
    
    def create_comparison_plots(self):
        """Create comparison plots between different datasets."""
        if len(self.datasets) < 2:
            print("Not enough datasets for comparison plots")
            return
        
        comparison_dir = os.path.join(self.output_dir, "comparisons")
        Path(comparison_dir).mkdir(parents=True, exist_ok=True)
        
        # Create overlay plots
        c_comp = ROOT.TCanvas("c_comparison", "Comparison", 1200, 800)
        c_comp.SetLeftMargin(0.12)
        c_comp.SetBottomMargin(0.12)
        
        legend = ROOT.TLegend(0.65, 0.65, 0.88, 0.88)
        legend.SetBorderSize(0)
        legend.SetFillStyle(0)
        
        colors = [ROOT.kBlue, ROOT.kRed, ROOT.kGreen+2, ROOT.kMagenta, 
                  ROOT.kCyan, ROOT.kOrange, ROOT.kViolet, ROOT.kPink]
        
        # This is a placeholder - you would need to store histograms
        # during processing to create actual comparison plots
        print("\nComparison plots would be created here if histograms were stored")
    
    def run(self):
        """Run the complete analysis."""
        print(f"Searching for SLCIO files in: {self.base_dir}")
        
        # Find all SLCIO files
        self.find_slcio_files()
        
        if not self.datasets:
            print("No SLCIO files found!")
            return
        
        print(f"\nFound {len(self.datasets)} dataset(s):")
        for name in self.datasets:
            print(f"  - {name}: {len(self.datasets[name])} file(s)")
        
        # Process each dataset
        for dataset_name, file_list in self.datasets.items():
            hists, event_count = self.process_dataset(dataset_name, file_list)
            self.save_plots(dataset_name, hists, event_count)
        
        # Create comparison plots
        self.create_comparison_plots()
        
        print(f"\nAnalysis complete! Plots saved in: {self.output_dir}")


# Example usage
if __name__ == "__main__":
    # Set your base directory here
    base_directory = "/home/devlinjenkins/projects/NozzleSimOpti/simulation/geometries/MAIA_v0_Blackhole/nozzle_varients"
    
    # Create analyzer instance
    analyzer = SLCIOAnalyzer(
        base_dir=base_directory,
        output_dir="slcio_analysis_plots",
        max_events=-1  # Process all events, set to positive number to limit
    )
    
    # Run the analysis
    analyzer.run()