# generator.py

from LayoutScript import *
import main
import math

def create_contact_pads(drawing):
    """
    Create contact pads around the perimeter and return their coordinates.
    [Code for create_contact_pads remains unchanged - omitted for brevity]
    """
    # Name the first cell
    drawing.currentCell.cellName = "Contact Pads"

    # Calculate step size and total size
    step = main.CONTACT_PAD_SIZE + main.CONTACT_PAD_SPACING
    total_size = main.PADS_PER_EDGE * step - main.CONTACT_PAD_SPACING
    offset = int(-total_size / 2)

    # Store contact pad coordinates and corner indices
    contact_pad_coords = []
    corner_indices = []
    pad_index = 0

    # Create contact pads and store their coordinates
    # Loop adjusted to handle potential PADS_PER_EDGE=1 case gracefully
    for i in range(main.PADS_PER_EDGE):
        pos = i * step

        # Bottom edge
        if main.PADS_PER_EDGE > 0:
            x_coord = offset + pos + main.CONTACT_PAD_SIZE//2
            y_coord = offset + main.CONTACT_PAD_SIZE//2
            drawing.currentCell.addBox(offset + pos, offset, main.CONTACT_PAD_SIZE, main.CONTACT_PAD_SIZE, main.CONTACT_PAD_LAYER)
            contact_pad_coords.append((pad_index, x_coord, y_coord))
            # Mark corners - avoid double counting if PADS_PER_EDGE=1
            if i == 0 or (i == main.PADS_PER_EDGE - 1 and main.PADS_PER_EDGE > 1):
                corner_indices.append(pad_index)
            pad_index += 1

        # Top edge (only if PADS_PER_EDGE > 1 to avoid overlap with bottom for single pad edge)
        if main.PADS_PER_EDGE > 1:
            x_coord = offset + pos + main.CONTACT_PAD_SIZE//2
            y_coord = offset + total_size - main.CONTACT_PAD_SIZE//2
            drawing.currentCell.addBox(offset + pos, offset + total_size - main.CONTACT_PAD_SIZE,
                                      main.CONTACT_PAD_SIZE, main.CONTACT_PAD_SIZE, main.CONTACT_PAD_LAYER)
            contact_pad_coords.append((pad_index, x_coord, y_coord))
            if i == 0 or i == main.PADS_PER_EDGE - 1:
                corner_indices.append(pad_index)
            pad_index += 1

        # Left edge (skip corners, only if PADS_PER_EDGE > 2)
        if i > 0 and i < main.PADS_PER_EDGE - 1:
             x_coord = offset + main.CONTACT_PAD_SIZE//2
             y_coord = offset + pos + main.CONTACT_PAD_SIZE//2
             drawing.currentCell.addBox(offset, offset + pos, main.CONTACT_PAD_SIZE, main.CONTACT_PAD_SIZE, main.CONTACT_PAD_LAYER)
             contact_pad_coords.append((pad_index, x_coord, y_coord))
             pad_index += 1

        # Right edge (skip corners, only if PADS_PER_EDGE > 2)
        if i > 0 and i < main.PADS_PER_EDGE - 1:
             x_coord = offset + total_size - main.CONTACT_PAD_SIZE//2
             y_coord = offset + pos + main.CONTACT_PAD_SIZE//2
             drawing.currentCell.addBox(offset + total_size - main.CONTACT_PAD_SIZE, offset + pos,
                                       main.CONTACT_PAD_SIZE, main.CONTACT_PAD_SIZE, main.CONTACT_PAD_LAYER)
             contact_pad_coords.append((pad_index, x_coord, y_coord))
             pad_index += 1

    # Ensure corner indices are unique if PADS_PER_EDGE=1 resulted in duplicates
    corner_indices = sorted(list(set(corner_indices)))

    return contact_pad_coords, corner_indices, total_size, offset


def create_electrodes(drawing, available_pads_count):
    """
    Create electrodes. Uses a perfect square grid (NxN) if available_pads_count
    is a perfect square. Otherwise, uses a "block circle" pattern by selecting
    all grid points within a radius that encompasses approximately N points.

    Args:
        drawing: The drawing reference
        available_pads_count: Number of available contact pads (excluding corners)

    Returns:
        list: List of (index, x, y) tuples for all electrodes created.
    """

    # --- Nested Helper Function ---
    def _is_perfect_square(n):
        """Checks if n is a perfect square. If yes, returns its integer root."""
        if n < 0: return None
        if n == 0: return 0
        x = int(math.sqrt(n))
        if x * x == n:
            return x
        else:
            return None
    # --- End of Nested Helper Function ---

    # Create a new cell for electrodes
    new_cell = drawing.addCell()
    new_cell.thisCell.cellName = "Electrodes"
    drawing.setCell(new_cell.thisCell)

    electrode_coords = []
    if available_pads_count <= 0:
        print("Warning: No available pads for electrodes.")
        return electrode_coords # Return empty list if no electrodes needed

    electrode_radius = main.ELECTRODE_DIAMETER // 2
    N = available_pads_count # Target number of electrodes

    # --- Decision Logic: Perfect Square Grid or Block Circle? ---
    grid_side = _is_perfect_square(N)

    if grid_side is not None:
        # It is a perfect square! Use grid layout.
        grid_rows = grid_cols = grid_side
        print(f"Creating electrodes in a perfect square {grid_rows}x{grid_cols} grid.")
        # --- Grid Placement Logic ---
        x_start = -((grid_cols - 1) * main.ELECTRODE_SPACING) // 2
        y_start = -((grid_rows - 1) * main.ELECTRODE_SPACING) // 2
        electrode_index = 0

        for row in range(grid_rows):
            y_pos = y_start + row * main.ELECTRODE_SPACING
            for col in range(grid_cols):
                if electrode_index >= N: break # Safety

                x_pos = x_start + col * main.ELECTRODE_SPACING
                p = point(x_pos, y_pos)
                drawing.currentCell.addCircle(main.ELECTRODE_LAYER, p, electrode_radius)
                electrode_coords.append((electrode_index, x_pos, y_pos))
                electrode_index += 1
            if electrode_index >= N: break

    else:
        # Not a perfect square. Use "Block Circle" approximation.
        print(f"{N} is not a perfect square. Using block circle approximation for electrodes.")
        # --- Block Circle Approximation Logic ---

        candidate_points = []
        # Estimate max grid steps needed, add buffer. Might need tuning.
        # Needs to generate *at least* N points.
        max_grid_steps = math.ceil(math.sqrt(N) / 1.5) + 4 # Increased buffer slightly

        # Generate candidate points and distances
        for ix in range(-max_grid_steps, max_grid_steps + 1):
             for iy in range(-max_grid_steps, max_grid_steps + 1):
                x_pos = ix * main.ELECTRODE_SPACING
                y_pos = iy * main.ELECTRODE_SPACING
                dist_sq = x_pos**2 + y_pos**2
                # Store raw coords and dist_sq
                candidate_points.append({'x': x_pos, 'y': y_pos, 'dist_sq': dist_sq})

        # Check if enough candidate points were generated
        if len(candidate_points) < N:
             print(f"Warning: Generated only {len(candidate_points)} candidate points within search radius, less than the required {N}. Placing all generated points.")
             # In this case, we just use all generated points
             sorted_points = sorted(candidate_points, key=lambda p: p['dist_sq'])
             selected_points = sorted_points
             # Adjust N if we couldn't generate enough points
             N = len(selected_points)
        else:
            # Sort all candidates by distance
            sorted_points = sorted(candidate_points, key=lambda p: p['dist_sq'])

            # Find the squared distance of the Nth point (index N-1)
            threshold_dist_sq = sorted_points[N-1]['dist_sq']

            # Select points: All points strictly closer, plus just enough points at the threshold distance
            selected_points = []
            points_at_threshold = []
            for p in sorted_points:
                if p['dist_sq'] < threshold_dist_sq:
                    selected_points.append(p)
                elif p['dist_sq'] == threshold_dist_sq:
                    # Collect all points exactly at the threshold distance
                    points_at_threshold.append(p)
                else:
                    # Since sorted, we can stop early once distance exceeds threshold
                    break

            # Calculate how many more points we need from the threshold distance group
            num_needed_from_threshold = N - len(selected_points)

            # Add the required number of points from the threshold group
            # Takes the first ones encountered in the sorted list
            if num_needed_from_threshold > 0:
                 selected_points.extend(points_at_threshold[:num_needed_from_threshold])

        # Create electrodes from the final selected_points list
        for index, point_data in enumerate(selected_points):
             # Make sure we don't exceed N if something went wrong
             if index >= N: break

             x_pos = point_data['x']
             y_pos = point_data['y']
             p = point(x_pos, y_pos)
             drawing.currentCell.addCircle(main.ELECTRODE_LAYER, p, electrode_radius)
             # Use the loop index 'index' for the electrode ID
             electrode_coords.append((index, x_pos, y_pos))

    # Sort the final list by index for consistency (optional but good practice)
    electrode_coords.sort(key=lambda c: c[0])

    return electrode_coords