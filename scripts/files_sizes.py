import matplotlib.pyplot as plt

# Sample data
simulation_versions = ["Default", "2cm depth", "4cm depth", "6cm depth", "8cm depth", "10cm depth", "Blackhole Nozzle"]
file_sizes = [258.08, 251.74, 243.21, 255.06, 257.21, 252.87, 242.03]  # time in mb

# Colors for each bar
colors = [
    "#ffa500",  # ROOT.kOrange
    "#ff8040",  # ROOT.kOrange-3
    "#00ff00",  # ROOT.kGreen+2
    "#008080",  # ROOT.kTeal
    "#007fff",  # ROOT.kAzure+7
    "#0000ee",  # ROOT.kBlue+1
    "#a9a9a9"   # ROOT.kGray+3
]

# Create the bar chart
fig, ax = plt.subplots(figsize=(12, 6))

bars = ax.bar(simulation_versions, file_sizes, color=colors)

# Set axis titles
ax.set_xlabel("Blackhole Depth from Surface", fontsize=14)
ax.set_ylabel("File Size (MB)", fontsize=14)
ax.set_title("File Size for Each Simulation Version", fontsize=16)

# Display the values on top of the bars
for bar in bars:
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2.0, yval, f'{yval:.2f}', va='bottom', fontsize=12, ha='center')

# Save the figure as a PNG
plt.tight_layout()
plt.savefig("file_sizes.png")
plt.show()
