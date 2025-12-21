import numpy as np
import matplotlib.pyplot as plt

parameters = [
    "Chemical elements",
    "Alloy identification",
    "Number of phases",
    "Phase identification",
    "Type of research details",
    "Experimental details",
    "Theoretical details",
    "Type of solution",
]
model_results = [
    94.30894309,
    84.14634146,
    89.43089431,
    89.83739837,
    92.68292683,
    82.5203252,
    87.80487805,
    82.11382114,
]
script_results = [
    93.44262295,
    79.50819672,
    78.68852459,
    78.27868852,
    89.3442623,
    81.55737705,
    81.14754098,
    84.42622951
]

# Create a histogram with overlaid bars for model and script results
plt.figure(figsize=(12, 6), facecolor='none')  # Set figure background to transparent

x = np.arange(len(parameters))  # the label locations
width = 0.5  # the width of the bars

# Define pleasant colors
model_color =  'midnightblue' #'#1fa187'  # dark purple
script_color = 'whitesmoke'  # white

# Create bars with rounded corners
from matplotlib.patches import PathPatch
from matplotlib.path import Path

def rounded_bar(x, height, width, color, alpha=1.0, linewidth=0, radius=0.15):
    # Create the bar with rounded corners
    verts = [
        (x, 0),                      # bottom left
        (x, height - radius),        # top left (minus radius)
        (x + radius, height),        # top left with radius
        (x + width - radius, height),# top right with radius
        (x + width, height - radius),# top right (minus radius)
        (x + width, 0),              # bottom right
        (x, 0),                      # back to bottom left
    ]
    
    codes = [Path.MOVETO] + [Path.LINETO] * 5 + [Path.CLOSEPOLY]
    path = Path(verts, codes)
    patch = PathPatch(path, facecolor=color, alpha=alpha, linewidth=linewidth)
    return patch

# Add model result bars with rounded corners
bars1 = []
for i, height in enumerate(model_results):
    bar = rounded_bar(i - width/2, height, width, model_color, alpha=0.8)
    plt.gca().add_patch(bar)
    bars1.append(bar)

# Add script result bars with hatching
bars2 = []
for i, height in enumerate(script_results):
    bar = plt.bar(i, height, width, label='Script Results' if i == 0 else "", 
                  color='none', edgecolor=script_color, linewidth=1.5,
                  hatch='/', alpha=0.9)
    bars2.append(bar[0])

# Add a dummy patch for the legend
import matplotlib.patches as mpatches
model_patch = mpatches.Patch(color=model_color, alpha=0.8, label='Model Results')
script_patch = mpatches.Patch(facecolor='none', edgecolor=script_color, 
                             hatch='////', label='Script Results')

# Add labels, title and custom x-axis tick labels
plt.ylabel('Percentage (%)', fontsize=12)
plt.title('Model vs Script Results by Parameter', fontsize=14, fontweight='bold')
plt.xticks(x, parameters, rotation=45, ha='right', fontsize=10)
plt.ylim(30, 100)

# Add a legend with custom patches
plt.legend(handles=[model_patch, script_patch], loc='upper right')

# Add value labels on top of bars
for i, bar in enumerate(bars1):
    height = model_results[i]
    plt.annotate(f'{height:.1f}',
                xy=(i, height),
                xytext=(0, 3),  # 3 points vertical offset
                textcoords="offset points",
                ha='center', va='bottom', fontsize=9)

for i, bar in enumerate(bars2):
    height = script_results[i]
    plt.annotate(f'{height:.1f}',
                xy=(i, height),
                xytext=(0, -17),  # 15 points vertical offset downward
                textcoords="offset points",
                ha='center', va='bottom', color=script_color, fontweight='bold', fontsize=9)

plt.tight_layout()
plt.grid(axis='y', linestyle='--', alpha=0.3)
plt.gca().set_facecolor('none')  # Set axes background to transparent
plt.show()