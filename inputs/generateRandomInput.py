import random

def generate_unique_coordinates(N, num_units, used_coords):
    coords = set()
    while len(coords) < num_units:
        row = random.randint(0, N-1)
        col = random.randint(0, N-1)
        coord = (row, col)
        if coord not in used_coords and coord not in coords:
            coords.add(coord)
    return coords

def generate_input_file(N, W, T, R, filename):
    with open(filename, 'w') as f:
        # Write header
        f.write(f"{N} {W} {T} {R}\n")
        
        # Generate waves
        for wave in range(1, W+1):
            f.write(f"Wave {wave}:\n")
            used_coords = set()
            
            # Generate coordinates for each faction
            for faction in ['E', 'F', 'W', 'A']:
                coords = generate_unique_coordinates(N, T, used_coords)
                used_coords.update(coords)
                
                # Format coordinates
                coord_str = ', '.join(f"{row} {col}" for row, col in coords)
                f.write(f"{faction}: {coord_str}\n")
            


if __name__ == "__main__":
    # Example usage
    N = 24  # Grid size
    W = 2  # Number of waves
    T = 16  # Units per faction per wave
    R = 4  # Rounds per wave
    for i in range(50):
        generate_input_file(N, W, T, R, filename=f"randomInput{i}.txt")