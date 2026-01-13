# parses the input file and returns the grid size, round, and units to be placed on the grid in the new wave
def parse_input(input):
    with open(input) as f:
        line = f.readline().split()
        # the first line of the input file contains the grid size, wave count, units per faction, and round
        grid_size = int(line[0])
        wave_count = int(line[1])
        unit_per_faction = int(line[2])
        round = int(line[3])
        # initialize the units list to store the units to be placed on the grid
        units = []
        # read the input file line by line and store the units in the units list
        for i in range(wave_count):
            # each wave contains units for each faction
            sub_units = []
            # read an empty line to separate the waves
            empty_line = f.readline().strip()
            # read the units for each faction
            for j in range(4):
                line = f.readline().split()
                # the first element of the line is the faction name
                faction = line[0].strip(":")
                line.pop(0)
                # read the x and y coordinates of the units and store them in the sub_units list
                # the x and y coordinates are separated by a comma
                for k in range(0, 2*unit_per_faction,2):
                    x = int(line[k])
                    y = int(line[k+1].strip(","))
                    sub_units.append((faction, y, x))
            # append the units for the current wave to the units list
            units.append(sub_units)
        # return the grid size, round, and units to be placed on the grid in the new wave
        return grid_size, round, units
