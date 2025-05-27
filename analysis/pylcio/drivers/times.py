import matplotlib.pyplot as plt

# Sample data
simulation_versions = ["Default", "2cm depth", "4cm depth", "6cm depth", "8cm depth", "10cm depth", "Blackhole Nozzle"]
render_times = [800.95, 682.67, 572.66, 688.98, 724.24, 713.45, 547.21]  # times in seconds

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

bars = ax.bar(simulation_versions, render_times, color=colors)
# Set axis titles
ax.set_xlabel("Blackhole Depth from Surface", fontsize=14)
ax.set_ylabel("Rendering Time (seconds)", fontsize=14)
ax.set_title("Rendering Time for Each Simulation Version", fontsize=16)

# Display the values on top of the bars
for bar in bars:
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2.0, yval, f'{yval:.2f}', va='bottom', fontsize=12, ha='center')

# Save the figure as a PNG
plt.tight_layout()
plt.savefig("render_times.png")
plt.show()
