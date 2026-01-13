from simulation import Grid

# get processor id (rank) of a given x, y coordinate

def get_processor_id(x, y, sqrt_p, sub_grid_size):
    return (x // sub_grid_size) + (y // sub_grid_size)*sqrt_p + 1

# get the relation index between two processor ranks
# 0 : below
# 1 : above
# 2 : right
# 3 : left
# 4 : below left
# 5 : above left
# 6 : below right
# 7 : above right

def neighbor_relation(pid_1, pid_2, sqrt_p):

    # special case for 2x2
    if (sqrt_p == 2):
        if pid_1 == 1:
            if pid_2 == 2:
                return 2
            elif pid_2 == 3:
                return 0
            else:
                return 6
        elif pid_1 == 2:
            if pid_2 == 1:
                return 3
            elif pid_2 == 4:
                return 0
            else:
                return 4
        elif pid_1 == 3:
            if pid_2 == 1:
                return 1
            elif pid_2 == 4:
                return 2
            else:
                return 7
        elif pid_1 == 4:
            if pid_2 == 2:
                return 1
            elif pid_2 == 3:
                return 3
            else:
                return 5

    # general case        
    else:
        # check the relation between two processors

        # check if pid_2 is below pid_1
        if pid_1 == pid_2 - sqrt_p:
            return 0
        
        # check if pid_2 is above pid_1
        elif pid_1 == pid_2 + sqrt_p:
            return 1
        
        # check if pid_2 is right of pid_1
        elif pid_1 == pid_2 - 1:
            return 2
        
        # check if pid_2 is left of pid_1
        elif pid_1 == pid_2 + 1:
            return 3
        
        # check if pid_2 is below right of pid_1
        elif pid_1 == pid_2 - sqrt_p - 1:
            return 6
        
        # check if pid_2 is below left of pid_1
        elif pid_1 == pid_2 - sqrt_p + 1:
            return 4
        
        # check if pid_2 is above right of pid_1
        elif pid_1 == pid_2 + sqrt_p - 1:
            return 7
        
        # check if pid_2 is above left of pid_1
        elif pid_1 == pid_2 + sqrt_p + 1:
            return 5
    

# get possible attacks of an air unit using neighbor subgrids

def get_air_attack_pattern(unit, air_attack_pattern, subgrid, neighbour_subgrids, rank, world_size, sqrt_p):

    # accumulate all possible attacks as messages that are dictionaries structured
    # with the following keys: x, y, damage
    air_messages = []

    # check each neighbor for possible attacks
    for i in range(8):

        # track the case when it is the same unit
        collision = False
        enemy = air_attack_pattern[i]
        if (enemy[0],enemy[1]) == (unit.x, unit.y):
            collision = True
        enemy_processor = get_processor_id(enemy[0], enemy[1], sqrt_p, subgrid.get_size())
        if enemy_processor < 1 or enemy_processor > world_size - 1:
            continue

        # handle the case where the enemy is in the same processor
        if enemy_processor == rank:
            enemy_unit = subgrid.get_unit(enemy[0], enemy[1])
            if collision:
                enemy_unit = None
            if enemy_unit is not None:
                if enemy_unit.faction != unit.faction:

                    # add the attack as a message
                    air_messages.append({"x": enemy[0], "y": enemy[1],  "damage": unit.attack})
            else:
                # check the outer neighbors
                enemy = air_attack_pattern[i+8]
                enemy_processor = get_processor_id(enemy[0], enemy[1], sqrt_p, subgrid.get_size())
                if enemy_processor < 1 or enemy_processor > world_size - 1:
                    continue
                if enemy_processor == rank:
                    enemy_unit = subgrid.get_unit(enemy[0], enemy[1])
                    if enemy_unit is not None:
                        if enemy_unit.faction != unit.faction:

                            # add the attack as a message

                            air_messages.append({"x": enemy[0], "y": enemy[1],  "damage": unit.attack})
                else:
                    relation_index = neighbor_relation(rank, enemy_processor, sqrt_p)
                    enemy_unit = neighbour_subgrids[relation_index].get_unit(enemy[0], enemy[1])
                    if enemy_unit is not None:
                        if enemy_unit.faction != unit.faction:

                            # add the attack as a message
                            air_messages.append({"x": enemy[0], "y": enemy[1],  "damage": unit.attack})

        # handle the case where the enemy is in a different processor                    
        else:

            relation_index = neighbor_relation(rank, enemy_processor, sqrt_p)
            enemy_unit = neighbour_subgrids[relation_index].get_unit(enemy[0], enemy[1])
            if collision:
                enemy_unit = None
            if enemy_unit is not None:
                if enemy_unit.faction != unit.faction:
                    air_messages.append({"x": enemy[0], "y": enemy[1],  "damage": unit.attack})
            else:
                enemy = air_attack_pattern[i+8]
                enemy_processor = get_processor_id(enemy[0], enemy[1], sqrt_p, subgrid.get_size())
                if enemy_processor < 1 or enemy_processor > world_size - 1:
                    continue
                relation_index = neighbor_relation(rank, enemy_processor, sqrt_p)
                enemy_unit = neighbour_subgrids[relation_index].get_unit(enemy[0], enemy[1])
                if enemy_unit is not None:
                    if enemy_unit.faction != unit.faction:
                        air_messages.append({"x": enemy[0], "y": enemy[1],  "damage": unit.attack})
                    
    return air_messages


# simulate all possible movements of an air unit and return the best one
def simulate_movement(unit, subgrid, neighbour_subgrids, rank, world_size , sqrt_p):
    # get all possible movement positions for the unit
    neighbors = []
    neighbors.append((unit.x, unit.y))
    neighbors += subgrid.get_all_neighbors(unit.x, unit.y)
    best_messages = []
    best_x, best_y = unit.x, unit.y

    # check each possible movement for the attacks
    for x,y in neighbors:
        
        if x < 0 or y < 0 or x >= subgrid.get_size() * sqrt_p or y >= subgrid.get_size()* sqrt_p:
            continue

        enemy_processor = get_processor_id(x, y, sqrt_p, subgrid.get_size())

        # check if the enemy is in the same processor
        if rank == enemy_processor:
            if (x,y) != (unit.x, unit.y):
                if subgrid.get_unit(x,y) is not None:
                    continue
        # check if the enemy is in a different processor        
        else:
            # check the relation between the processors
            relation_index = neighbor_relation(rank, enemy_processor, sqrt_p)
            if neighbour_subgrids[relation_index].get_unit(x, y) is not None:
                continue

        air_attack_pattern = unit.get_attack_pattern(x, y)
        
        # get the attack pattern if unit moves to x,y
        messages = get_air_attack_pattern(unit, air_attack_pattern, subgrid, neighbour_subgrids, rank, world_size , sqrt_p)

        # if the attack pattern is better than the previous best, update the best
        if len(messages) > len(best_messages):
            best_messages = messages
            best_x, best_y = x, y
        
    # return the best movement
    return best_x, best_y, best_messages


# initalize a new grid from an existing grid to be passed to a neighbor processor
# num is the size of the new grid, num size of cols, rows or corner grids are passed

def split_grid(existing_grid, direction, num):

# directions are as follows:
# 0 : below
# 1 : above
# 2 : right
# 3 : left
# 4 : below left
# 5 : above left
# 6 : below right
# 7 : above right
    
    original_size = existing_grid.get_size()
    new_offset_x, new_offset_y = existing_grid.offset_x, existing_grid.offset_y
    new_grid_data = None

    # split the grid in the specified direction

    # split num amounts of rows to be passed above
    if direction == 1:
        new_grid_data = existing_grid.grid[:num, :]

    # split num amounts of rows to be passed below
    elif direction == 0:
        new_grid_data = existing_grid.grid[-num:, :]
        new_offset_y += (original_size - num)

    # split num amounts of cols to be passed left
    elif direction == 3:
        new_grid_data = existing_grid.grid[:, :num]

    # split num amounts of cols to be passed right
    elif direction == 2:
        new_grid_data = existing_grid.grid[:, -num:]
        new_offset_x += (original_size - num)

    # split num sized grid be passed above left
    elif direction == 5:
        new_grid_data = existing_grid.grid[:num, :num]

    # split num sized grid be passed above right
    elif direction == 7:
        new_grid_data = existing_grid.grid[:num, -num:]
        new_offset_x += (original_size - num)

    # split num sized grid be passed below left
    elif direction == 4:
        new_grid_data = existing_grid.grid[-num:, :num]
        new_offset_y += (original_size - num)

    # split num sized grid be passed below right
    elif direction == 6:
        new_grid_data = existing_grid.grid[-num:, -num:]
        new_offset_x += (original_size - num)
        new_offset_y += (original_size - num)


    # create the new grid instance
    new_size = max(new_grid_data.shape)
    new_grid = Grid(size=new_size, offset_x=new_offset_x, offset_y=new_offset_y, message_grid=True)

    new_grid.grid = new_grid_data


    return new_grid


# initalize new grids from an existing grid to be passed to all  neighbor processor
def split_to_all(subgrid, num):
    new_grids = []

    # split grids to be passed for all directions
    for i in range(8):
        new_grids.append(split_grid(subgrid, i, num[i]))

    return new_grids