import LayoutScript
from LayoutScript import *
import os

# Import our modules
from generator import create_contact_pads, create_electrodes

# CONFIG
# Project name
PROJECT_NAME = "Computational_MEA16_General"

# Layer definitions
CONTACT_PAD_LAYER = 5
ELECTRODE_LAYER = 6

# Contact pad parameters
PADS_PER_EDGE = 8  # Number of contact pads per edge
CONTACT_PAD_SIZE = 2000000  # in nm
CONTACT_PAD_SPACING = 1000000  # in nm

# Electrode parameters
ELECTRODE_DIAMETER = 16000  # in nm
ELECTRODE_SPACING = 40000  # in nm

# Output path
OUTPUT_PATH = '/Users/maxxyung/Documents/Master Documents/Nanoneuro/Nanofab/layout-editor-scripts/'

# END CONFIG

def main():
    # Create a new layout
    l = project.newLayout()
    
    # Get a reference to the drawing
    dr = l.drawing
    
    # Create contact pads
    contact_pad_coords, corner_indices, total_size, offset = create_contact_pads(dr)
    
    # Calculate number of available pads (excluding corners)
    available_pads_count = len(contact_pad_coords) - len(corner_indices)
    
    # Create electrodes
    electrode_coords = create_electrodes(dr, available_pads_count)
    
    # Save the result
    output_path = os.path.join(OUTPUT_PATH, f"{PROJECT_NAME}.gds")
    l.drawing.saveFile(output_path)
    
    # Print summary
    print("Design completed with:")
    print(f"  - {len(contact_pad_coords)} total contact pads")
    print(f"  - {len(electrode_coords)} electrodes")
    print(f"  - {len(corner_indices)} corner pads reserved for ground")
    
if __name__ == "__main__":
    main()