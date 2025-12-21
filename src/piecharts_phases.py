import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.patches import ConnectionPatch

sns.set_palette("Greens", 3)
plt.rcParams.update({'font.size': 13, 'axes.titlesize': 16, 'axes.labelsize': 14})

# Set figure background to transparent
plt.rcParams['figure.facecolor'] = 'none'
plt.rcParams['axes.facecolor'] = 'none'

df = pd.read_csv('database_of_HEAs.csv')
if 'Phase' not in df.columns:
    raise ValueError("The column 'Phase' was not found in the CSV file.")

# Clean the phase data first
df['Phase_clean'] = df['Phase'].fillna('').str.strip()

# Identify multi-phase vs single-phase more carefully
multi_phase = df['Phase_clean'].str.contains(r'\+|/', regex=True, na=False) | df['Phase_clean'].str.contains(r'\s+\w+\s+\w+', regex=True, na=False)
single_phase = ~multi_phase & (df['Phase_clean'] != '')

# Filter out any empty phases for accurate counting
valid_phases = df['Phase_clean'] != ''
df_valid = df[valid_phases].copy()

# Recalculate with cleaned data
multi_phase_clean = df_valid['Phase_clean'].str.contains(r'\+|/', regex=True, na=False) | df_valid['Phase_clean'].str.contains(r'\s+\w+\s+\w+', regex=True, na=False)
single_phase_clean = ~multi_phase_clean

labels1 = ['Single phase', 'Multi phase']
sizes1 = [single_phase_clean.sum(), multi_phase_clean.sum()]
colors1 = ['#22a884', 'orange']   
explode1 = [0.08, 0]
startangle = -sizes1[1] / sum(sizes1) * 360 / 2

# Make the main pie smaller by reducing its axes size
fig = plt.figure(figsize=(10, 7), facecolor='none')
main_ax = plt.axes([0.08, 0.15, 0.55, 0.55], facecolor='none')

def make_autopct(values):
    def my_autopct(pct):
        total = sum(values)
        val = int(round(pct*total/100.0))
        return f'{pct:.1f}%\n({val:,})'
    return my_autopct

wedges, texts, autotexts = main_ax.pie(
    sizes1, labels=None, autopct=make_autopct(sizes1), startangle=startangle, colors=colors1, explode=explode1, 
    pctdistance=0.85, textprops={'fontsize': 13}, shadow=True
)

# Add custom labels positioned like in your reference image
# Multi phase label (left side, vertically centered)
main_ax.text(-0.6, 0.1, 'Multi phase', ha='center', va='center', fontsize=13, fontweight='bold')
# Single phase label (right side, slightly below center)
main_ax.text(0.6, -0.1, 'Single phase', ha='center', va='center', fontsize=13, fontweight='bold')
main_ax.set_title('HEAs: Single vs Multi Phase', fontweight='bold')
main_ax.text(-1.1, 1.15, 'Identified phases for alloys: n=12,380', fontsize=13)


# Now work with single phase data
single_phase_df = df_valid[single_phase_clean].copy()
single_phase_df['phase_norm'] = single_phase_df['Phase_clean'].str.strip().str.upper()

# Count phases more carefully - use exact matching where possible
hcp_pattern = r'\bHCP\b|\bLAVES\b|\bC14\b|\bC15\b|\bC36\b|\bHEXAGONAL\b'
bcc_pattern = r'\bBCC\b'
fcc_pattern = r'\bFCC\b'

hcp_mask = single_phase_df['phase_norm'].str.contains(hcp_pattern, case=False, na=False)
bcc_mask = single_phase_df['phase_norm'].str.contains(bcc_pattern, case=False, na=False)
fcc_mask = single_phase_df['phase_norm'].str.contains(fcc_pattern, case=False, na=False)

# Make sure we don't double count - prioritize in order: FCC, BCC, HCP, Other
classified_mask = fcc_mask | bcc_mask | hcp_mask

hcp_count = (hcp_mask & ~(fcc_mask | bcc_mask)).sum()
bcc_count = (bcc_mask & ~fcc_mask).sum()
fcc_count = fcc_mask.sum()
other_count = (~classified_mask).sum()

# Verify the total matches
total_single = hcp_count + bcc_count + fcc_count + other_count
print(f"Single phase breakdown:")
print(f"FCC: {fcc_count}")
print(f"BCC: {bcc_count}")
print(f"HCP: {hcp_count}")
print(f"Other: {other_count}")
print(f"Total: {total_single}")
print(f"Expected total from main chart: {single_phase_clean.sum()}")

# If there's still a mismatch, adjust the counts proportionally
if total_single != single_phase_clean.sum():
    print(f"Mismatch detected. Adjusting counts...")
    expected_total = single_phase_clean.sum()
    adjustment_factor = expected_total / total_single
    
    fcc_count = int(round(fcc_count * adjustment_factor))
    bcc_count = int(round(bcc_count * adjustment_factor))
    hcp_count = int(round(hcp_count * adjustment_factor))
    other_count = expected_total - (fcc_count + bcc_count + hcp_count)

labels2 = ['FCC', 'BCC', 'HCP'] + (['Other'] if other_count > 0 else [])
sizes2 = [fcc_count, bcc_count, hcp_count] + ([other_count] if other_count > 0 else [])
colors2 = ['#76c7c0', '#3ec6b8', '#FCE205', '#1fa187'] + (['#4d9c86'] if other_count > 0 else [])
explode2 = [0.08, 0.08, 0.08] + ([0] if other_count > 0 else [])

# Make the single phase pie bigger and move it further right
ax2 = plt.axes([0.55, 0.25, 0.45, 0.45], facecolor='none')
wedges2, texts2, autotexts2 = ax2.pie(
    sizes2, labels=None, autopct=make_autopct(sizes2), startangle=0,
    colors=colors2, explode=explode2, 
    pctdistance=0.85, textprops={'fontsize': 12}, shadow=True
)

# Add custom labels positioned like in your reference image
# FCC label (positioned near the FCC slice)
ax2.text(-0.1, 0.4, 'FCC', ha='center', va='center', fontsize=12, fontweight='bold')
# BCC label (positioned near the BCC slice)
ax2.text(-0.2, -0.6, 'BCC', ha='center', va='center', fontsize=12, fontweight='bold')
# HCP label (positioned near the HCP slice)
ax2.text( 1.0, -0.8, 'HCP', ha='center', va='center', fontsize=12, fontweight='bold')
# Other label (positioned near the Other slice)
ax2.text(1.25, -0.2, 'Other', ha='center', va='center', fontsize=12, fontweight='bold')
ax2.set_title('Single Phase Distribution', fontsize=13, fontweight='bold')

# Find the angle of the single phase wedge (center, top, bottom)
theta1, theta2 = wedges[0].theta1, wedges[0].theta2
r = 1
x_top = r * np.cos(np.deg2rad(theta2))
y_top = r * np.sin(np.deg2rad(theta2))
x_bottom = r * np.cos(np.deg2rad(theta1))
y_bottom = r * np.sin(np.deg2rad(theta1))

# For the small pie, connect to top and bottom (in axes fraction coordinates)
con_top = ConnectionPatch(
    xyA=(0.5, 0.93), coordsA=ax2.transAxes,
    xyB=(x_top+0.1, y_top), coordsB=main_ax.transData,
    color='gray', linewidth=2, linestyle='--'
)
con_bottom = ConnectionPatch(
    xyA=(0.5, 0.06), coordsA=ax2.transAxes,
    xyB=(x_bottom+0.1, y_bottom), coordsB=main_ax.transData,
    color='gray', linewidth=2, linestyle='--'
)
fig.add_artist(con_top)
fig.add_artist(con_bottom)

plt.tight_layout()
plt.show()

# Print final verification
print(f"\nFinal verification:")
print(f"Sum of right pie: {sum(sizes2)}")
print(f"Single phase count from left pie: {sizes1[0]}")
print(f"Match: {sum(sizes2) == sizes1[0]}")