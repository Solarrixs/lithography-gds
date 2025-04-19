import LayoutScript
from LayoutScript import *

# Create a new layout
l = project.newLayout()
project_name = "Computational_MEA16"

# Get a reference to the drawing
dr = l.drawing

# Name the first cell and create contact pads
dr.currentCell.cellName = "Contact Pads"

# Define contact pad parameters
num_electrodes_per_side = 16  # 16 electrodes per side
electrode_size = 2000000  # 2mm square (2,000,000 nm)
electrode_spacing = 1000000  # 1mm spacing (1,000,000 nm)
layer_num = 5  # Layer for contact pads

# Calculate step size and total size
step = electrode_size + electrode_spacing
total_size = num_electrodes_per_side * step - electrode_spacing
offset = int(-total_size / 2)

# Create electrodes along the perimeter
for i in range(num_electrodes_per_side):
    pos = i * step
    
    # Bottom edge
    dr.currentCell.addBox(offset + pos, offset, electrode_size, electrode_size, layer_num)
    
    # Top edge
    dr.currentCell.addBox(offset + pos, offset + total_size - electrode_size, electrode_size, electrode_size, layer_num)
    
    # Left edge (skip corners)
    if i > 0 and i < num_electrodes_per_side - 1:
        dr.currentCell.addBox(offset, offset + pos, electrode_size, electrode_size, layer_num)
    
    # Right edge (skip corners)
    if i > 0 and i < num_electrodes_per_side - 1:
        dr.currentCell.addBox(offset + total_size - electrode_size, offset + pos, electrode_size, electrode_size, layer_num)

# Create a new cell for the electrodes
new_cell = dr.addCell()
new_cell.thisCell.cellName = "Electrodes"
dr.setCell(new_cell.thisCell)

# Define electrode parameters (with updated values)
electrode_diameter = 16000  # 16μm diameter (16,000 nm)
electrode_radius = electrode_diameter // 2  # 8μm radius (8,000 nm)
electrode_spacing = 40000  # 40μm spacing (40,000 nm)
electrode_layer = 6  # Layer for electrodes

# Define grid dimensions (7×8 grid = 56 electrodes)
grid_cols = 7
grid_rows = 8

# Calculate grid positions to center at (0,0)
x_start = -((grid_cols - 1) * electrode_spacing) // 2
y_start = -((grid_rows - 1) * electrode_spacing) // 2

# Create electrode grid
for row in range(grid_rows):
    y_pos = y_start + row * electrode_spacing
    for col in range(grid_cols):
        x_pos = x_start + col * electrode_spacing
        
        # Create a point at the electrode position
        p = point(x_pos, y_pos)
        
        # Add a circle at this position
        dr.currentCell.addCircle(electrode_layer, p, electrode_radius)

# Save the result
l.drawing.saveFile(f'/Users/maxxyung/Documents/Master Documents/Nanoneuro/Nanofab/layout-editor-scripts/{project_name}.gds')

print("Microelectrode array design completed with contact pads and electrodes")