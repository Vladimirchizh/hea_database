import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib as mpl
import numpy as np
import re


plt.style.use('default')
mpl.rcParams['font.family'] = 'Arial'
mpl.rcParams['font.size'] = 10

df = pd.read_csv('merged_data_unnested.csv')

dictionary = {
    "Melting Methods": {
        "Arc Melting": {
            "Arc Melting": "Arc Melting",
            "Vacuum Arc Melting": "Vacuum Arc Melting",
            "VAM": "Vacuum Arc Melting",
            "Non-consumable Arc Melting": "Arc Melting",
            "Tungsten Arc Melting": "Arc Melting",
            "Plasma Arc Melting": "Plasma Arc Melting",
            "PAM": "Plasma Arc Melting",
        },
        "Induction Melting": {
            "Induction Melting": "Induction Melting",
            "Vacuum Induction Melting": "Vacuum Induction Melting",
            "VIM": "Vacuum Induction Melting",
            "High Frequency Induction Melting": "Induction Melting",
            "Levitation Melting": "Levitation Melting",
            "Electromagnetic Levitation": "Levitation Melting",
            "EML": "Levitation Melting",
        },
        "Electron Beam Melting": {
            "Electron Beam Melting": "Electron Beam Melting",
            "EBM": "Electron Beam Melting",
            "Electron Beam Remelting": "Electron Beam Melting",
        },
        "Casting Methods": {
            "Investment Casting": "Investment Casting",
            "Sand Casting": "Sand Casting",
            "Die Casting": "Die Casting",
            "Vacuum Casting": "Vacuum Casting",
            "Centrifugal Casting": "Centrifugal Casting",
            "Directional Solidification": "Directional Solidification",
            "DS": "Directional Solidification",
            "Bridgman Method": "Bridgman Method",
            "Czochralski Method": "Czochralski Method",
            "CZ": "Czochralski Method",
        },
        "Rapid Solidification": {
            "Melt Spinning": "Melt Spinning",
            "MS": "Melt Spinning",
            "Rapid Solidification": "Rapid Solidification",
            "RS": "Rapid Solidification",
            "Splat Quenching": "Splat Quenching",
            "Copper Mold Casting": "Copper Mold Casting",
            "Strip Casting": "Strip Casting",
            "Planar Flow Casting": "Planar Flow Casting",
        },
    },
    
    "Sputtering Techniques": {
        "Magnetron Sputtering": {
            "Magnetron Sputtering": "Magnetron Sputtering",
            "Magnetron Co-sputtering": "Magnetron Co-sputtering",
            "Magnetron Co sputtering": "Magnetron Co-sputtering",
            "DC Magnetron Sputtering": "DC Magnetron Sputtering",
            "RF Magnetron Sputtering": "RF Magnetron Sputtering",
            "Reactive Magnetron Sputtering": "Reactive Magnetron Sputtering",
            "High Power Impulse Magnetron Sputtering": "HiPIMS",
            "HiPIMS Magnetron Sputtering": "HiPIMS",
            "HiPIMS": "HiPIMS",
            "HIPIMS": "HiPIMS",
            "Pulsed DC Magnetron Sputtering": "Pulsed DC Magnetron Sputtering",
			"DC Sputtering": "DC Sputtering",
            "RF Sputtering": "RF Sputtering",
            "Reactive Sputtering": "Reactive Sputtering",
            "Bias Sputtering": "Bias Sputtering",
        },
        "Ion Beam Sputtering": {
            "Ion Beam Sputtering": "Ion Beam Sputtering",
            "Ion Beam Sputter-deposition": "Ion Beam Sputter-deposition",
            "Ion Beam Sputter deposition": "Ion Beam Sputter-deposition",
            "IBSD": "Ion Beam Sputter-deposition",
            "Ion Beam Deposition": "Ion Beam Deposition",
            "IBD": "Ion Beam Deposition",
        },
        "Other PVD Methods": {
            "Physical Vapor Deposition": "Physical Vapor Deposition",
            "PVD": "Physical Vapor Deposition",
            "Thermal Evaporation": "Thermal Evaporation",
            "Ion Plating": "Ion Plating",
            "Cathodic Arc Deposition": "Cathodic Arc Deposition",
            "CAD": "Cathodic Arc Deposition",
            "Filtered Cathodic Arc Deposition": "Filtered Cathodic Arc Deposition",
            "Electron Beam Physical Vapor Deposition": "Electron Beam PVD",
            "EB-PVD": "Electron Beam PVD",
            "Pulsed Laser Deposition": "Pulsed Laser Deposition",
            "PLD": "Pulsed Laser Deposition",
        },
    },
    
    "Laser-based Methods": {
        "Powder Bed Fusion": {
            "Selective Laser Melting": "Selective Laser Melting",
            "SLM": "Selective Laser Melting",
            "Laser Powder Bed Fusion": "Laser Powder Bed Fusion",
            "LPBF": "Laser Powder Bed Fusion",
            "L-PBF": "Laser Powder Bed Fusion",
            "Direct Metal Laser Sintering": "Direct Metal Laser Sintering",
            "DMLS": "Direct Metal Laser Sintering",
        },
        "Direct Energy Deposition": {
            "Laser Metal Deposition": "Laser Metal Deposition",
            "LMD": "Laser Metal Deposition",
            "Direct Energy Deposition": "Direct Energy Deposition",
            "DED": "Direct Energy Deposition",
            "Laser Engineered Net Shaping": "Laser Engineered Net Shaping",
            "LENS": "Laser Engineered Net Shaping",
            "Direct Metal Deposition": "Direct Metal Deposition",
            "DMD": "Direct Metal Deposition",
        },
        "Laser Surface Processing": {
            "Laser Cladding": "Laser Cladding",
            "Laser Surface Alloying": "Laser Surface Alloying",
            "LSA": "Laser Surface Alloying",
            "Laser Melting": "Laser Melting",
            "Laser Remelting": "Laser Remelting",
            "Laser Surface Melting": "Laser Surface Melting",
            "LSM": "Laser Surface Melting",
            "Laser Welding": "Laser Welding",
        },
        "Other Additive Manufacturing": {
            "Laser Additive Manufacturing": "Laser Additive Manufacturing",
            "LAM": "Laser Additive Manufacturing",
            "Electron Beam Additive Manufacturing": "Electron Beam Additive Manufacturing",
            "EBAM": "Electron Beam Additive Manufacturing",
            "Electron Beam Freeform Fabrication": "Electron Beam Freeform Fabrication",
            "EBF3": "Electron Beam Freeform Fabrication",
            "Wire Arc Additive Manufacturing": "Wire Arc Additive Manufacturing",
            "WAAM": "Wire Arc Additive Manufacturing",
        },
    },
    
    "Mechanical Processing": {
        "Ball Milling": {
            "High-energy Ball Milling": "High-energy Ball Milling",
            "High energy Ball Milling": "High-energy Ball Milling",
            "High-energy Ball-milling": "High-energy Ball Milling",
            "High energy Ball-milling": "High-energy Ball Milling",
            "HEBM": "High-energy Ball Milling",
            "Mechanical Alloying": "Mechanical Alloying",
            "MA": "Mechanical Alloying",
            "Planetary Ball Milling": "Planetary Ball Milling",
            "Attritor Milling": "Attritor Milling",
            "Cryogenic Ball Milling": "Cryogenic Ball Milling",
        },
        "Severe Plastic Deformation": {
            "Equal Channel Angular Pressing": "Equal Channel Angular Pressing",
            "ECAP": "Equal Channel Angular Pressing",
            "ECAE": "Equal Channel Angular Pressing",
            "High Pressure Torsion": "High Pressure Torsion",
            "HPT": "High Pressure Torsion",
            "Accumulative Roll Bonding": "Accumulative Roll Bonding",
            "ARB": "Accumulative Roll Bonding",
            "Multi-directional Forging": "Multi-directional Forging",
            "MDF": "Multi-directional Forging",
            "Twist Extrusion": "Twist Extrusion",
            "Surface Mechanical Attrition Treatment": "Surface Mechanical Attrition Treatment",
            "SMAT": "Surface Mechanical Attrition Treatment",
        },
        "Conventional Deformation": {
            "Rolling": "Rolling",
            "Cold Rolling": "Cold Rolling",
            "Hot Rolling": "Hot Rolling",
            "Forging": "Forging",
            "Cold Forging": "Cold Forging",
            "Hot Forging": "Hot Forging",
            "Extrusion": "Extrusion",
            "Hot Extrusion": "Hot Extrusion",
            "Drawing": "Drawing",
            "Wire Drawing": "Wire Drawing",
            "Swaging": "Swaging",
        },
        "Pressing Methods": {
            "Hot Pressing": "Hot Pressing",
            "HP": "Hot Pressing",
            "Cold Pressing": "Cold Pressing",
            "Cold Isostatic Pressing": "Cold Isostatic Pressing",
            "CIP": "Cold Isostatic Pressing",
            "Hot Isostatic Pressing": "Hot Isostatic Pressing",
            "HIP": "Hot Isostatic Pressing",
            "Uniaxial Pressing": "Uniaxial Pressing",
            "Quasi-isostatic Pressing": "Quasi-isostatic Pressing",
        },
        "Joining Methods": {
            "Friction Stir Welding": "Friction Stir Welding",
            "FSW": "Friction Stir Welding",
            "Friction Stir Processing": "Friction Stir Processing",
            "FSP": "Friction Stir Processing",
            "Diffusion Bonding": "Diffusion Bonding",
            "Electron Beam Welding": "Electron Beam Welding",
            "Transient Liquid Phase Bonding": "Transient Liquid Phase Bonding",
            "TLPB": "Transient Liquid Phase Bonding",
        },
    },
    
    "Thermal Spray Methods": {
        "Plasma Spraying": {
            "Air Plasma Spraying": "Air Plasma Spraying",
            "APS": "Air Plasma Spraying",
            "Atmospheric Plasma Spraying": "Air Plasma Spraying",
            "Vacuum Plasma Spraying": "Vacuum Plasma Spraying",
            "VPS": "Vacuum Plasma Spraying",
            "Plasma Spraying": "Plasma Spraying",
        },
        "High Velocity Methods": {
            "High Velocity Oxy-Fuel": "High Velocity Oxy-Fuel",
            "HVOF": "High Velocity Oxy-Fuel",
            "High Velocity Air-Fuel": "High Velocity Air-Fuel",
            "HVAF": "High Velocity Air-Fuel",
            "Cold Spray": "Cold Spray",
            "CS": "Cold Spray",
            "Kinetic Spray": "Cold Spray",
        },
        "Flame Spraying": {
            "Flame Spraying": "Flame Spraying",
            "Wire Flame Spraying": "Wire Flame Spraying",
            "Powder Flame Spraying": "Powder Flame Spraying",
        },
        "Detonation Methods": {
            "Detonation Gun": "Detonation Gun",
            "D-Gun": "Detonation Gun",
        },
        "Powder Production": {
            "Gas Atomization": "Gas Atomization",
            "GA": "Gas Atomization",
            "Water Atomization": "Water Atomization",
            "Plasma Atomization": "Plasma Atomization",
            "EIGA": "EIGA",
            "VIGA": "VIGA",
            "Centrifugal Atomization": "Centrifugal Atomization",
        },
    },
    
    "Special Processing": {
        "Sintering Methods": {
            "Spark Plasma Sintering": "Spark Plasma Sintering",
            "SPS": "Spark Plasma Sintering",
            "Field Assisted Sintering Technology": "Spark Plasma Sintering",
            "FAST": "Spark Plasma Sintering",
            "PECS": "Spark Plasma Sintering",
            "Microwave Sintering": "Microwave Sintering",
            "Conventional Sintering": "Conventional Sintering",
            "Pressureless Sintering": "Pressureless Sintering",
            "Vacuum Sintering": "Vacuum Sintering",
            "Liquid Phase Sintering": "Liquid Phase Sintering",
            "Two-step Sintering": "Two-step Sintering",
        },
        "Chemical Vapor Deposition": {
            "Chemical Vapor Deposition": "Chemical Vapor Deposition",
            "CVD": "Chemical Vapor Deposition",
            "Plasma Enhanced CVD": "Plasma Enhanced CVD",
            "PECVD": "Plasma Enhanced CVD",
            "Metal Organic CVD": "Metal Organic CVD",
            "MOCVD": "Metal Organic CVD",
            "Low Pressure CVD": "Low Pressure CVD",
            "LPCVD": "Low Pressure CVD",
        },
        "Electrochemical Methods": {
            "Electrodeposition": "Electrodeposition",
            "Electroplating": "Electroplating",
            "Pulse Electrodeposition": "Pulse Electrodeposition",
            "Electroless Deposition": "Electroless Deposition",
            "Electroless Plating": "Electroless Plating",
            "Electrophoretic Deposition": "Electrophoretic Deposition",
            "EPD": "Electrophoretic Deposition",
        },
        "Solution-based Methods": {
            "Sol-gel": "Sol-gel",
            "Sol-gel Method": "Sol-gel",
            "Hydrothermal Synthesis": "Hydrothermal Synthesis",
            "Solvothermal Synthesis": "Solvothermal Synthesis",
            "Co-precipitation": "Co-precipitation",
            "Combustion Synthesis": "Combustion Synthesis",
            "Self-propagating High-temperature Synthesis": "Self-propagating High-temperature Synthesis",
            "SHS": "Self-propagating High-temperature Synthesis",
        },
        "Gas Condensation": {
            "Inert Gas Condensation": "Inert Gas Condensation",
            "IGC": "Inert Gas Condensation",
            "Gas Evaporation": "Gas Evaporation",
            "Spray Drying": "Spray Drying",
            "Freeze Drying": "Freeze Drying",
        },
        "Surface Treatment": {
            "Ion Implantation": "Ion Implantation",
            "Plasma Immersion Ion Implantation": "Plasma Immersion Ion Implantation",
            "PIII": "Plasma Immersion Ion Implantation",
            "Shot Peening": "Shot Peening",
            "Laser Shock Peening": "Laser Shock Peening",
            "Nitriding": "Nitriding",
            "Plasma Nitriding": "Plasma Nitriding",
            "Gas Nitriding": "Gas Nitriding",
            "Carburizing": "Carburizing",
            "Pack Cementation": "Pack Cementation",
        },
        "General Processing": {
            "Powder Metallurgy": "Powder Metallurgy",
            "PM": "Powder Metallurgy",
            "Additive Manufacturing": "Additive Manufacturing",
            "AM": "Additive Manufacturing",
            "3D Printing": "3D Printing",
            "Heat Treatment": "Heat Treatment",
            "Annealing": "Annealing",
            "Homogenization": "Homogenization",
            "Solution Treatment": "Solution Treatment",
            "Aging": "Aging",
            "Tempering": "Tempering",
        },
    },
}


category_counts = {category: 0 for category in dictionary.keys()}
method_group_counts = {category: {mg: 0 for mg in methods.keys()} for category, methods in dictionary.items()}
method_counts = {category: {mg: {} for mg in methods.keys()} for category, methods in dictionary.items()}
other_count = 0
other_details = []

def normalize_text(text):
    text = text.lower()
    text = re.sub(r'[-\s]+', ' ', text)
    return text.strip()


for details in df['Experimental details']:
    if pd.isna(details):
        continue

    found_method = False
    normalized_details = normalize_text(str(details))

    for category, method_groups in dictionary.items():
        for method_group, methods in method_groups.items():
            for method_key, method_value in methods.items():
                normalized_key = normalize_text(method_key)
                if normalized_key in normalized_details:
                    category_counts[category] += 1
                    method_group_counts[category][method_group] += 1
                    if method_value not in method_counts[category][method_group]:
                        method_counts[category][method_group][method_value] = 0
                    method_counts[category][method_group][method_value] += 1
                    found_method = True
    if not found_method:
        other_count += 1
        other_details.append(details)


ordered_categories = list(dictionary.keys())
if "Special Processing" in ordered_categories:
    ordered_categories.remove("Special Processing")
    ordered_categories.append("Special Processing")


main_labels = []
main_sizes = []
main_category_angles = []
total = sum(category_counts[c] for c in ordered_categories) + other_count
startangle = 90
current_angle = startangle

for category in ordered_categories:
    count = category_counts[category]
    if count > 0:
        main_labels.append(category)
        main_sizes.append(count)
        angle_span = (count / total) * 360
        angle_center = current_angle + angle_span / 2
        main_category_angles.append(angle_center)
        current_angle += angle_span

if other_count > 0:
    main_labels.append("Other")
    main_sizes.append(other_count)
    angle_span = (other_count / total) * 360
    angle_center = current_angle + angle_span / 2
    main_category_angles.append(angle_center)


colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f']

fig = plt.figure(figsize=(16, 12))

# Main pie chart
ax_main = plt.subplot2grid((3, 3), (0, 0), colspan=2, rowspan=2)

# Custom autopct function
def autopct_func(pct):
    return f'{pct:.1f}%' if pct >= 3.0 else ''

wedges, texts, autotexts = ax_main.pie(
    main_sizes,
    labels=main_labels,
    autopct=autopct_func,
    startangle=90,
    colors=colors[:len(main_sizes)],
    wedgeprops=dict(edgecolor='white', linewidth=2),
    textprops={'fontsize': 12, 'fontweight': 'bold'},
    labeldistance=1.1,
    pctdistance=0.85
)

# Style the percentage labels
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontweight('bold')
    autotext.set_fontsize(11)

ax_main.set_title('Distribution of Processing Methods with Detailed Breakdown', fontsize=16, fontweight='bold', pad=20)

# Create detailed breakdown charts for top categories
top_categories = sorted([(count, cat) for cat, count in category_counts.items() if count > 0], reverse=True)[:6]

# Create subplot positions for detailed breakdowns
subplot_positions = [(0, 2), (1, 2), (2, 0), (2, 1), (2, 2)]

for i, (count, category) in enumerate(top_categories[:5]):
    if i >= len(subplot_positions):
        break
        
    row, col = subplot_positions[i]
    ax_sub = plt.subplot2grid((3, 3), (row, col))
    
    # Get method group data
    mg_counts = method_group_counts[category]
    mg_labels = []
    mg_sizes = []
    mg_total = sum(mg_counts.values())
    
    for mg, cnt in mg_counts.items():
        if cnt > 0:
            # Truncate long labels
            label = mg if len(mg) <= 20 else mg[:17] + "..."
            mg_labels.append(label)
            mg_sizes.append(cnt)
    
    if not mg_sizes:
        continue

    # Get color for this category from main pie
    main_idx = main_labels.index(category) if category in main_labels else 0
    base_color = colors[main_idx % len(colors)]
    
    # Generate color variations
    base_rgb = mpl.colors.to_rgb(base_color)
    subcolors = []
    for j in range(len(mg_sizes)):
        factor = 0.4 + 0.6 * (j / max(len(mg_sizes)-1, 1))  # Vary brightness
        varied_color = tuple(min(1.0, c + (1-c) * (1-factor)) for c in base_rgb)
        subcolors.append(varied_color)
    
    # Create sub-pie with better formatting
    def sub_autopct(pct):
        absolute = int(round(pct/100. * sum(mg_sizes)))
        if pct >= 10:
            return f'{absolute}\n({pct:.0f}%)'
        elif pct >= 5:
            return f'{absolute}'
        else:
            return ''

    def subpie_label(label, pct):
        return label if pct >= 4.0 else ''

    wedges_sub, texts_sub, autotexts_sub = ax_sub.pie(
        mg_sizes,
        labels=[subpie_label(l, p) for l, p in zip(mg_labels, (np.array(mg_sizes)/mg_total)*100)],
        colors=subcolors,
        startangle=90,
        autopct=sub_autopct,
        textprops={'fontsize': 8, 'fontweight': 'bold', 'color': 'white'},
        wedgeprops=dict(edgecolor='white', linewidth=1),
        labeldistance=1.1,
        pctdistance=0.7
    )
    
    # Style the labels
    for text in texts_sub:
        text.set_fontsize(8)
        text.set_color('black')
        text.set_fontweight('bold')
    
    for autotext in autotexts_sub:
        autotext.set_color('white')
        autotext.set_fontsize(7)
        autotext.set_fontweight('bold')

    # Add category title
    ax_sub.set_title(f'{category}\n(n={count})', fontsize=10, fontweight='bold', pad=10)

    main_wedge_index = main_labels.index(category)
    main_wedge = wedges[main_wedge_index]
    main_wedge_center = main_wedge.center
    main_wedge_angle = (main_wedge.theta1 + main_wedge.theta2) / 2
    main_edge_x = main_wedge_center[0] + main_wedge.r * np.cos(np.deg2rad(main_wedge_angle))
    main_edge_y = main_wedge_center[1] + main_wedge.r * np.sin(np.deg2rad(main_wedge_angle))
    
    sub_center = ax_sub.transAxes.transform((0.5, 0.5))
    sub_center_display = fig.transFigure.inverted().transform(sub_center)

# Add summary statistics as text
summary_text = "Summary Statistics:\n"
summary_text += "="*25 + "\n"
for category in ordered_categories:
    if category_counts[category] > 0:
        pct = (category_counts[category] / total) * 100
        summary_text += f"{category}: {category_counts[category]} ({pct:.1f}%)\n"

if other_count > 0:
    pct = (other_count / total) * 100
    summary_text += f"Other: {other_count} ({pct:.1f}%)\n"
summary_text += f"\nTotal Samples: {total}"

# Add text box with summary
fig.text(0.02, 0.02, summary_text, fontsize=9, family='monospace',
         bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray", alpha=0.8))

plt.tight_layout()
plt.subplots_adjust(bottom=0.25)
plt.show()

# Print detailed summary
print("\nDetailed Processing Methods Distribution:")
print("="*60)
for category in ordered_categories:
    if category_counts[category] > 0:
        pct = (category_counts[category] / total) * 100
        print(f"\n{category}: {category_counts[category]} ({pct:.1f}%)")
        
        # Print method groups for this category
        mg_counts = method_group_counts[category]
        for mg, count in mg_counts.items():
            if count > 0:
                mg_pct = (count / category_counts[category]) * 100
                print(f"  └─ {mg}: {count} ({mg_pct:.1f}%)")

if other_count > 0:
    pct = (other_count / total) * 100
    print(f"\nOther: {other_count} ({pct:.1f}%)")

print(f"\nGrand Total: {total} samples")