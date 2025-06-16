import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib as mpl
import numpy as np
import re
import matplotlib.patches as patches
from matplotlib.path import Path
from collections import Counter, defaultdict
import networkx as nx


plt.style.use('default')
mpl.rcParams['font.family'] = 'Arial'
mpl.rcParams['font.size'] = 10

df = pd.read_csv('database_of_HEAs.csv')

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
category_alloy_counts = {category: 0 for category in dictionary.keys()}
method_group_alloy_counts = {category: {mg: 0 for mg in methods.keys()} for category, methods in dictionary.items()}
method_alloy_counts = {category: {mg: {} for mg in methods.keys()} for category, methods in dictionary.items()}
other_alloy_count = 0
other_details = []

def normalize_text(text):
    text = text.lower()
    text = re.sub(r'[-\s]+', ' ', text)
    return text.strip()

ordered_categories = list(dictionary.keys())
if "Special Processing" in ordered_categories:
    ordered_categories.remove("Special Processing")
    ordered_categories.append("Special Processing")

# Process data - count each category only once per alloy row
total_alloys = len(df)
article_categories = []

for idx, details in enumerate(df['Experimental details']):
    if pd.isna(details):
        continue

    normalized_details = normalize_text(str(details))
    alloy = df['Alloy'].iloc[idx] if 'Alloy' in df.columns else None
    
    # Track which categories are found for this alloy (to avoid double counting)
    found_categories = set()
    found_method_groups = {category: set() for category in dictionary.keys()}
    found_methods = {category: {mg: set() for mg in methods.keys()} for category, methods in dictionary.items()}
    
    # Check all methods for this alloy
    for category, method_groups in dictionary.items():
        for method_group, methods in method_groups.items():
            for method_key, method_value in methods.items():
                normalized_key = normalize_text(method_key)
                if normalized_key in normalized_details:
                    found_categories.add(category)
                    found_method_groups[category].add(method_group)
                    found_methods[category][method_group].add(method_value)
    
    # Count each category/method group/method only once per alloy
    for category in found_categories:
        category_alloy_counts[category] += 1
        
        for method_group in found_method_groups[category]:
            method_group_alloy_counts[category][method_group] += 1
            
            for method_value in found_methods[category][method_group]:
                if method_value not in method_alloy_counts[category][method_group]:
                    method_alloy_counts[category][method_group][method_value] = 0
                method_alloy_counts[category][method_group][method_value] += 1
    
    # Track categories for co-occurrence analysis
    article_categories.append(found_categories)
    
    # Count as "other" if no methods found
    if not found_categories:
        other_alloy_count += 1
        other_details.append(details)

# Calculate co-occurrence data for network chart
co_occurrence = Counter()
for found_categories in article_categories:
    # Count all pairs
    for cat1 in found_categories:
        for cat2 in found_categories:
            if cat1 < cat2:
                co_occurrence[(cat1, cat2)] += 1

# Create networkx graph
G = nx.Graph()
node_sizes = {cat: category_alloy_counts[cat] for cat in ordered_categories}
for cat in ordered_categories:
    if node_sizes[cat] > 0:  # Only add nodes with data
        G.add_node(cat, size=node_sizes[cat])

for (cat1, cat2), weight in co_occurrence.items():
    if cat1 in G.nodes and cat2 in G.nodes:  # Only add edges between existing nodes
        G.add_edge(cat1, cat2, weight=weight)

colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f']

def draw_curved_edge(ax, pos1, pos2, color, width, alpha, curve_factor=0.3):
    """Draw a curved edge between two positions"""
    x1, y1 = pos1
    x2, y2 = pos2
    
    # Calculate control point for curve
    mid_x = (x1 + x2) / 2
    mid_y = (y1 + y2) / 2
    
    # Calculate perpendicular offset for curve
    dx = x2 - x1
    dy = y2 - y1
    
    # Perpendicular vector
    perp_x = -dy * curve_factor
    perp_y = dx * curve_factor
    
    # Control point
    ctrl_x = mid_x + perp_x
    ctrl_y = mid_y + perp_y
    
    # Create curved path
    verts = [(x1, y1), (ctrl_x, ctrl_y), (x2, y2)]
    codes = [Path.MOVETO, Path.CURVE3, Path.CURVE3]
    
    path = Path(verts, codes)
    patch = patches.PathPatch(path, facecolor='none', edgecolor=color, 
                             linewidth=width, alpha=alpha, capstyle='round')
    ax.add_patch(patch)

# Create the main figure with network chart as primary visualization
fig = plt.figure(figsize=(18, 12))

# Network chart takes the main space (left 2/3 of the figure)
ax_network = plt.subplot2grid((3, 4), (0, 0), colspan=3, rowspan=3)

if G.number_of_nodes() > 0:
    # Use circular layout
    pos = nx.circular_layout(G, scale=2)
    
    # Calculate edge weights for coloring
    edge_list = list(G.edges(data=True))
    if edge_list:
        weights = [d['weight'] for u, v, d in edge_list]
        max_weight = max(weights)
        min_weight = min(weights)
        total_weight = sum(weights)
        
        # Sort weights to find quartiles for better color separation
        sorted_weights = sorted(weights)
        q75 = sorted_weights[int(0.75 * len(sorted_weights))] if len(sorted_weights) > 0 else max_weight
        
        # Draw curved edges with improved label positioning
        for i, (u, v, d) in enumerate(edge_list):
            pos1 = pos[u]
            pos2 = pos[v]
            
            # Alternate curve direction for visual appeal
            curve_factor = 0.4 if i % 2 == 0 else -0.4
            
            # Normalize weight for scaling (0 to 1)
            normalized_weight = (d['weight'] - min_weight) / (max_weight - min_weight) if max_weight > min_weight else 0.5
            
            # Color and width based on weight
            if d['weight'] >= q75:  # Top 25% get red
                edge_color = '#d62728'  # Red for strong connections
                alpha = 0.9
                width = 3 + 5 * (normalized_weight ** 1.5)
            else:
                edge_color = '#1f77b4'  # Blue for weaker connections
                alpha = 0.7
                width = 1 + 3 * normalized_weight
            
            # Draw the curved edge
            draw_curved_edge(ax_network, pos1, pos2, edge_color, width, alpha, curve_factor)
            
            # Add percentage label with better positioning
            edge_percentage = (d['weight'] / total_weight * 100) if total_weight > 0 else 0
            
            # Calculate label position along the curve
            t = 0.5  # Midpoint of curve
            # Quadratic Bezier curve point calculation
            ctrl_x = (pos1[0] + pos2[0]) / 2 + (-((pos2[1] - pos1[1]) * curve_factor))
            ctrl_y = (pos1[1] + pos2[1]) / 2 + (((pos2[0] - pos1[0]) * curve_factor))
            
            label_x = (1-t)**2 * pos1[0] + 2*(1-t)*t * ctrl_x + t**2 * pos2[0]
            label_y = (1-t)**2 * pos1[1] + 2*(1-t)*t * ctrl_y + t**2 * pos2[1]
            
            # Only show percentages for significant connections
            if d['weight'] >= q75 or edge_percentage >= 3.0:
                # Add background box for better readability
                bbox_props = dict(boxstyle='round,pad=0.25', facecolor='white', 
                                alpha=0.9, edgecolor=edge_color, linewidth=1)
                ax_network.text(label_x, label_y, f'{edge_percentage:.1f}%', 
                               fontsize=9, fontweight='bold', color=edge_color,
                               bbox=bbox_props, ha='center', va='center', zorder=10)
    
    # Draw nodes with size based on alloy counts
    if node_sizes:
        max_size = max(node_sizes.values())
        min_size = min(node_sizes.values())
        
        # Use exponential scaling for more dramatic size differences
        base_size = 800
        max_node_size = 2500
        
        # Highlight the largest node in red
        special_node = max(node_sizes, key=node_sizes.get)
        node_colors = []
        node_sizes_list = []
        
        for node in G.nodes:
            # Normalize to 0-1 range
            normalized_size = (node_sizes[node] - min_size) / (max_size - min_size) if max_size > min_size else 0.5
            # Apply square root for more dramatic differences
            scaled_size = base_size + (max_node_size - base_size) * (normalized_size ** 0.5)
            node_sizes_list.append(scaled_size)
            
            if node == special_node:
                node_colors.append('#d62728')  # Red highlight
            else:
                node_colors.append('#2ca02c')  # Green
        
        # Draw nodes
        nx.draw_networkx_nodes(
            G, pos,
            node_size=node_sizes_list,
            node_color=node_colors,
            edgecolors='white',
            linewidths=3,
            ax=ax_network,
            alpha=0.95
        )
        
        # Draw labels with percentages based on total alloys
        labels_with_percentages = {}
        for node in G.nodes:
            percentage = (node_sizes[node] / total_alloys * 100) if total_alloys > 0 else 0
            labels_with_percentages[node] = f"{node}\n({percentage:.1f}%)"
        
        nx.draw_networkx_labels(
            G, pos,
            labels=labels_with_percentages,
            font_size=10,
            font_weight='bold',
            font_color='black',
            ax=ax_network
        )

# Style the network plot
ax_network.set_title('Processing Methods Co-occurrence Network\n(Node size = alloy count, Edge thickness = co-occurrence frequency)', 
                    fontsize=16, fontweight='bold', pad=20)
ax_network.set_aspect('equal')
ax_network.axis('off')
ax_network.set_xlim(-2.8, 2.8)
ax_network.set_ylim(-2.8, 2.8)

# Create detailed breakdown charts for top categories (right side)
categories_with_data = [(category_alloy_counts[cat], cat) for cat in ordered_categories if category_alloy_counts[cat] > 0]
top_categories = sorted(categories_with_data, reverse=True)[:4]

# Create subplot positions for detailed breakdowns
subplot_positions = [(0, 3), (1, 3), (2, 3)]

for i, (alloy_count, category) in enumerate(top_categories[:3]):
    if i >= len(subplot_positions):
        break
        
    row, col = subplot_positions[i]
    ax_sub = plt.subplot2grid((3, 4), (row, col))
    
    # Get method group data (using alloy counts)
    mg_counts = method_group_alloy_counts[category]
    mg_labels = []
    mg_sizes = []
    
    for mg, cnt in mg_counts.items():
        if cnt > 0:
            # Truncate long labels
            label = mg if len(mg) <= 15 else mg[:12] + "..."
            mg_labels.append(label)
            mg_sizes.append(cnt)
    
    if not mg_sizes:
        continue

    # Get color for this category
    if category in [cat for _, cat in top_categories]:
        cat_idx = [cat for _, cat in top_categories].index(category)
        base_color = colors[cat_idx % len(colors)]
    else:
        base_color = colors[0]
    
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
        return label if pct >= 8.0 else ''

    mg_total = sum(mg_sizes)
    wedges_sub, texts_sub, autotexts_sub = ax_sub.pie(
        mg_sizes,
        labels=[subpie_label(l, p) for l, p in zip(mg_labels, (np.array(mg_sizes)/mg_total)*100)],
        colors=subcolors,
        startangle=90,
        autopct=sub_autopct,
        textprops={'fontsize': 8, 'fontweight': 'bold'},
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

    # Add category title with alloy count
    percentage = (alloy_count / total_alloys) * 100 if total_alloys > 0 else 0
    ax_sub.set_title(f'{category}\n{alloy_count} alloys ({percentage:.1f}%)', 
                    fontsize=9, fontweight='bold', pad=10)

# Update summary statistics
summary_text = "Summary Statistics:\n"
summary_text += "="*30 + "\n"
summary_text += "By alloy count:\n"
for count, category in top_categories:
    pct = (count / total_alloys) * 100 if total_alloys > 0 else 0
    summary_text += f"  {category}: {count} ({pct:.1f}%)\n"

if other_alloy_count > 0:
    pct = (other_alloy_count / total_alloys) * 100 if total_alloys > 0 else 0
    summary_text += f"  Other: {other_alloy_count} ({pct:.1f}%)\n"

summary_text += f"\nTotal Alloys: {total_alloys}\n"
summary_text += f"Network Edges: {G.number_of_edges()}\n"
if 'total_weight' in locals():
    summary_text += f"Total Co-occurrences: {total_weight}"

# Add text box with summary
fig.text(0.02, 0.02, summary_text, fontsize=9, family='monospace',
         bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray", alpha=0.8))

plt.tight_layout()
plt.subplots_adjust(bottom=0.2)
plt.show()

# Print detailed summary
print("\nDetailed Processing Methods Distribution:")
print("="*60)
for count, category in top_categories:
    pct_alloys = (count / total_alloys) * 100 if total_alloys > 0 else 0
    print(f"\n{category}:")
    print(f"  Alloys using this method: {count} ({pct_alloys:.1f}%)")
    
    # Print method groups for this category
    mg_counts = method_group_alloy_counts[category]
    for mg, mg_count in mg_counts.items():
        if mg_count > 0:
            mg_pct = (mg_count / count) * 100 if count > 0 else 0
            print(f"    └─ {mg}: {mg_count} alloys ({mg_pct:.1f}%)")

print(f"\nTotal Alloys in Dataset: {total_alloys}")
if G.number_of_nodes() > 0:
    print(f"Network nodes: {G.number_of_nodes()}")
    print(f"Network edges: {G.number_of_edges()}")
