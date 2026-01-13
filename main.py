import numpy as np
from mpi4py import MPI
from simulation import Grid, FireUnit, WaterUnit, EarthUnit, AirUnit
from communication import communicate
from utils import get_processor_id, neighbor_relation, simulate_movement, get_air_attack_pattern, split_to_all
from parser import parse_input
import sys
import os


# Initialize the communicator
comm = MPI.COMM_WORLD
world_size = comm.Get_size()
rank = comm.Get_rank()

DEBUG = False

#if debug mode is off, redirect the output to /dev/null and write the debug information to an output file sys.argv[2]_detailed
if not DEBUG:
    sys.stdout = open(os.devnull, 'w')
    sys.stdout = open(sys.argv[2][:-4] + "_detailed.txt", "w")
    
    

#if the rank is 0, then it is the manager process
if rank == 0:

    #parse the input file
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    grid_size, rounds, waves = parse_input(input_file)    

    #send the wave information to the worker processes
    for proc in range(1, world_size):
        comm.send({"rounds": rounds, "waves": len(waves)}, dest=proc, tag=101)
    comm.Barrier()



    #create the main grid
    main_grid = Grid(grid_size)

    
    #initialize the units in the main grid
    for wave in waves:

        for unit in wave:
            if main_grid.get_unit(unit[1], unit[2]) is None:
                if unit[0] == "E":
                    EarthUnit(unit[1], unit[2], main_grid)
                elif unit[0] == "W":
                    WaterUnit(unit[1], unit[2], main_grid)
                elif unit[0] == "F":
                    FireUnit(unit[1], unit[2], main_grid)
                elif unit[0] == "A":
                    AirUnit(unit[1], unit[2], main_grid)


        sqrt_p = int((world_size - 1)**0.5)

        # Check if the number of worker processes is a perfect square minus one
        if sqrt_p * sqrt_p != (world_size - 1):
            raise ValueError("Number of worker processes must be sqrt_p perfect square minus one.")


        # Check if the grid size is divisible by sqrt_p
        if grid_size % sqrt_p != 0:
            raise ValueError("Grid size must be divisible by sqrt(number of worker processes).")


        print("--------------------")   
        print(f"🏄🏿 Wave {waves.index(wave) + 1} Initialization:")
        main_grid.display()
        print("--------------------")      

        print("Units:")


        #print all units in the main grid for debugging purposes
        for unit in main_grid.get_all_units():
            print(unit)

        print("--------------------")      

        subgrid_size = grid_size // sqrt_p  # Size of each subgrid


        #send the subgrids to the worker processes
        for proc in range(1, world_size):
            # Calculate subgrid offsets
            start_x = ((proc - 1) % sqrt_p) * subgrid_size
            start_y = ((proc - 1) // sqrt_p) * subgrid_size

            # Create sqrt_p subgrid instance with appropriate offset
            subgrid = Grid(subgrid_size, offset_x=start_x, offset_y=start_y)

            # Populate the subgrid with units from the main grid
            for i in range(start_x, start_x + subgrid_size):
                for j in range(start_y, start_y + subgrid_size):
                    unit = main_grid.get_unit(i, j)
                    if unit is not None:
                        subgrid.place_unit(unit)

            # Send the subgrid directly to the worker
            comm.send(subgrid, dest=proc, tag=100)
        comm.Barrier()


        #receive the subgrids from the worker processes
        for round in range(rounds):
            main_grid = Grid(grid_size)
            
            #sync the processes
            comm.Barrier()
            comm.Barrier()
            comm.Barrier()
            comm.Barrier()
            comm.Barrier()
            comm.Barrier()
            comm.Barrier()
            

            # if debug mode is on, then display the grid every round for debugging purposes
            if DEBUG:
                # receive computed subgrids from workers and combine them and display the final grid
                for proc in range(1, world_size):
                    # print(f"Receiving subgrid from {proc}")
                    subgrid = comm.recv(source=proc, tag=102)
                    # print(f"Received subgrid from {proc}")
                    start_x = ((proc - 1) % sqrt_p) * subgrid_size
                    start_y = ((proc - 1) // sqrt_p) * subgrid_size
                    for i in range(start_x, start_x + subgrid_size):
                        for j in range(start_y, start_y + subgrid_size):
                            unit = subgrid.get_unit(i, j)
                            if unit is not None:
                                main_grid.place_unit(unit)
                
                #display the final grid for debugging purposes
                comm.Barrier()
                print("--------------------")   
                print(f"🌟 Round {round + 1} End:")
                main_grid.display()
                print("--------------------")   

            
        #send the subgrids to the worker processes
        comm.Barrier()

        main_grid = Grid(grid_size)
        for proc in range(1, world_size):
            # print(f"Receiving subgrid from {proc}")
            subgrid = comm.recv(source=proc, tag=103)
            # print(f"Received subgrid from {proc}")
            start_x = ((proc - 1) % sqrt_p) * subgrid_size
            start_y = ((proc - 1) // sqrt_p) * subgrid_size
            for i in range(start_x, start_x + subgrid_size):
                for j in range(start_y, start_y + subgrid_size):
                    unit = subgrid.get_unit(i, j)
                    if unit is not None:
                        main_grid.place_unit(unit)
                     
        #display the final grid for debugging purposes   
        print("--------------------")   
        print(f"🌊 Wave {waves.index(wave) + 1} End:")
        main_grid.display()
        for unit in main_grid.get_all_units():
            print(unit)
        print("--------------------")
        comm.Barrier()

    #print all units to the output file
    with open(output_file, "w") as f:
    
        print("Final Output:")
        display_rows = main_grid.display()
        for row in display_rows:
            f.write("".join(row))
            
            f.write("\n")
    

# if the rank is not 0, then it is a worker process    
else:
    #send the wave information to the worker processes
    wave_info = comm.recv(source=0, tag=101)
    comm.Barrier()

    waves = wave_info["waves"]
    rounds = wave_info["rounds"]
    for wave in range(waves):
        
        # Receive the subgrid

        subgrid = comm.recv(source=0, tag=100)
        comm.Barrier()
        sqrt_p = int((world_size - 1)**0.5)


        for round in range(rounds):

            # print(f"🌟 Round {round + 1}: , rank: {rank}")


            # Create a list of subgrids to store the neighbours for the movement phase
            neighbour_subgrids = [Grid(subgrid.get_size(), -100,-100)] *8

            neighbour_subgrids = communicate(neighbour_subgrids,split_to_all(subgrid,[3]* 8) ,rank,sqrt_p,comm)

           #create a list to store the selected movements

            selected_movements = [[] for i in range(8)]

            #iterate over all units in the subgrid
            for unit in subgrid.get_all_units():
                
                #if the unit is an air unit, simulate the movement to fşnd the new x and y coordinates
                if unit.faction == "Air":
                    x,y,unit.attack_messages = simulate_movement(unit, subgrid, neighbour_subgrids, rank, world_size , sqrt_p)
                    # which processor the unit should move to
                    movement_processor = get_processor_id(x, y, sqrt_p, subgrid.get_size())
                
                    # if the unit should stay in the same processor
                    if movement_processor == rank:
                        if DEBUG:
                            print("🛫 unit:", unit, "moved to x,y :", x,y)

                        # enqueue the movement and removal of the unit
                        subgrid.enqueue_removal(unit, unit.x, unit.y)
                        subgrid.enqueue_movement(unit, x, y)

                    # if the unit should move to another processor
                    else:
                        if DEBUG:
                            print("🛫 unit:", unit, "moved to x,y :", x,y)

                        # find the relation index of the neighbour processor
                        relation_index = neighbor_relation(rank, movement_processor, sqrt_p)
                        # add the movement to the selected movements list
                        selected_movements[relation_index].append({"x": x, "y": y, "unit": unit})
                        # enqueue the removal of the unit
                        subgrid.enqueue_removal(unit, unit.x, unit.y)


            # communicate the selected movements to the neighbour processors to inform them about the movements
            subgrid_movement_queues = [[] for i in range(8)]
            subgrid_movement_queues = communicate(subgrid_movement_queues, selected_movements, rank, sqrt_p, comm)

            # sync the processes
            comm.Barrier()

            # iterate over the subgrid movement queues and enqueue the movements
            for i in range(8):
                for message in subgrid_movement_queues[i]:
                    subgrid.enqueue_movement_from_message(message)

            # resolve the removal and movement of the units
            subgrid.resolve_removal()
            subgrid.resolve_movement(DEBUG)

            # sync the processes
            comm.Barrier() 

            # Create a list of subgrids to store the neighbours for the attack phase
            neighbour_subgrids = [Grid(subgrid.get_size(), -100,-100)] *8

            neighbour_subgrids = communicate(neighbour_subgrids, split_to_all(subgrid,[2]* 8),rank,sqrt_p,comm)

            # sync the processes
            comm.Barrier()

            #create a list to store the selected attacks
            selected_attacks = [[] for i in range(8)]

            # iterate over all units in the subgrid
            for unit in subgrid.get_all_units():
                attacked = False
                # if the unit's health is above the threshold, then decide to attack
                if unit.decide() == "Attack":
                    
                    # if the unit is an air unit, get the attack pattern and attack the enemies
                    if unit.faction == "Air":

                        air_attack_pattern = unit.get_attack_pattern(unit.x, unit.y)
                        unit.attack_messages = get_air_attack_pattern(unit, air_attack_pattern, subgrid, neighbour_subgrids, rank, world_size , sqrt_p)

                        # iterate over the attack messages and enqueue the attacks
                        for message in unit.attack_messages:
                            enemy_processor = get_processor_id(message["x"], message["y"], sqrt_p, subgrid.get_size())
        
                            if enemy_processor == rank:
                                subgrid.enqueue_from_message(message)
                                
                                # print for debugging purposes
                                if DEBUG:
                                    print("🎯 unit:", unit, "⚔️ decided to attack ➡️ enemy:", (message["x"],message["y"]), "is in rank:", enemy_processor)
                                # set the attacked flag to true
                                attacked = True

                                    
                            else:
                                # find the relation index of the neighbour processor and add the attack to the selected attacks list accordingly
                                relation_index = neighbor_relation(rank, enemy_processor, sqrt_p)
                                selected_attacks[relation_index].append(message)
                                # print for debugging purposes
                                if DEBUG:
                                    print("🎯 unit:", unit, "⚔️ decided to attack ➡️  enemy:", (message["x"],message["y"]), "is in rank:", enemy_processor)
                                # set the attacked flag to true
                                attacked = True
                        # at the end of the attack, reset the attack messages for the next round
                        unit.attack_messages = []
                                    
                    # if the unit is not an air unit, then get the attack pattern and attack the enemies
                    else:
                        for enemy in unit.get_attack_pattern():
                            enemy_processor = get_processor_id(enemy[0], enemy[1], sqrt_p, subgrid.get_size())
                            # check whether the enemy is in the same processor
                            if enemy_processor == rank:
                                enemy_unit = subgrid.get_unit(enemy[0], enemy[1])
                                # if there is an enemy unit, then attack the enemy if the enemy is not in the same faction
                                if enemy_unit is not None:
                                    if enemy_unit.faction != unit.faction:
                                        subgrid.enqueue(enemy_unit, unit.attack)
                                        # print for debugging purposes
                                        if DEBUG:
                                            print("🎯 unit:", unit, "⚔️ decided to attack ➡️ enemy:", enemy, "is in rank:", enemy_processor)
                                        # set the attacked flag to true
                                        attacked = True
                                        # if the unit is a fire unit, then add the enemy to the attacked_to list due to the possible increase in attack power
                                        if unit.faction == "Fire":
                                            unit.attacked_to.append(enemy)
                                    
                            else:
                                relation_index = neighbor_relation(rank, enemy_processor, sqrt_p)
                                enemy_unit = neighbour_subgrids[relation_index].get_unit(enemy[0], enemy[1])
                                # if there is an enemy unit, then attack the enemy if the enemy is not in the same faction
                                if enemy_unit is not None:
                                    if enemy_unit.faction != unit.faction:
                                        selected_attacks[relation_index].append({"x": enemy[0], "y": enemy[1],  "damage": unit.attack})
                                        # print for debugging purposes
                                        if DEBUG:
                                            print("🎯 unit:", unit, "⚔️ decided to attack ➡️  enemy:", enemy, "is in rank:", enemy_processor)
                                        # set the attacked flag to true
                                        attacked = True
                                        # if the unit is a fire unit, then add the enemy to the attacked_to list due to the possible increase in attack power
                                        if unit.faction == "Fire":
                                            unit.attacked_to.append(enemy)
                # if the unit is not attacking, then skip the attack phase and set the decision to skip to heal
                if not attacked:
                    unit.decision = "Skip"
                    if DEBUG:
                        print("🚫 unit:", unit, "didn't attack.")
            
            # communicate the selected attacks to the neighbour processors to inform them about the attacks
            subgrid_damage_queues = [[] for i in range(8)]
            subgrid_damage_queues = communicate(subgrid_damage_queues, selected_attacks, rank, sqrt_p, comm)
            for i in range(8):
                for message in subgrid_damage_queues[i]:
                    subgrid.enqueue_from_message(message) 
            
            # sync the processes and resolve the damage and healing phases
            comm.Barrier() 
            
            subgrid.resolve_damage(DEBUG)

            comm.Barrier() 
            
            subgrid.resolve_healing(DEBUG)
            
            comm.Barrier() 

            # Create a list of deaths to check if the units are dead for informing the fire units

            neighbour_deaths = [[] for i in range(8)] 

            neighbour_deaths = communicate(neighbour_deaths, [subgrid.death_queue] * 8,rank,sqrt_p,comm)

            # inform the fire units about the deaths and increase their attack power accordingly
            for fire_unit in subgrid.get_all_units():
                if fire_unit.faction == "Fire":
                    for i in range(8):
                        for death in neighbour_deaths[i]:
                            if death in fire_unit.attacked_to:
                                fire_unit.increase_attack_power(DEBUG)
                    for internal_death in subgrid.death_queue:
                        if internal_death in fire_unit.attacked_to:
                            fire_unit.increase_attack_power(DEBUG)
                    fire_unit.attacked_to = []
            # reset the death queue for the next round
            subgrid.death_queue = []
            
            # sync the processes
            comm.Barrier()
            
            
            # if debug mode is on, then send the subgrid back to the manager at the end of the round for debugging purposes
            if DEBUG:
                # Send the subgrid back to the manager
                comm.send(subgrid, dest=0, tag=102)    
                
    
                comm.Barrier()

        # check if there is any water unit in the subgrid and spawn new water units accordingly due to the water units' flood ability
        neighbour_subgrids = [Grid(subgrid.get_size(), -100,-100)] *8
        
        neighbour_subgrids = communicate(neighbour_subgrids, split_to_all(subgrid,[1]* 8),rank,sqrt_p,comm)
        spawn_in_p = []
        selected_spawns = [[] for i in range(8)]

        # iterate over all units in the subgrid and check if there is any water unit
        for unit in subgrid.get_all_units():
            if unit.faction == "Water":
                neighbors = subgrid.get_all_neighbors(unit.x, unit.y)
                for neighbor in neighbors:
                    # check if the neighbor is out of the grid
                    if neighbor[0] < 0 or neighbor[0] >= subgrid.get_size()*sqrt_p or neighbor[1] < 0 or neighbor[1] >= subgrid.get_size()*sqrt_p:
                        continue
                    # check if the neighbor is in the same processor
                    neighbor_p = get_processor_id(neighbor[0], neighbor[1], sqrt_p, subgrid.get_size())
                    if neighbor_p == rank:
                        neighbor_unit = subgrid.get_unit(neighbor[0], neighbor[1])
                        # if there is no unit in the neighbor, then spawn a new water unit
                        if neighbor_unit is None:
                            spawn_in_p.append((neighbor[0], neighbor[1]))
                            break
                    else:
                        # find the relation index of the neighbour processor
                        relation_index = neighbor_relation(rank, neighbor_p, sqrt_p)
                        neighbor_unit = neighbour_subgrids[relation_index].get_unit(neighbor[0], neighbor[1])
                        # if there is no unit in the neighbor, then spawn a new water unit
                        if neighbor_unit is None:
                            selected_spawns[relation_index].append((neighbor[0], neighbor[1]))
                            break
        # spawn the water units in the same processor
        for spawn in spawn_in_p:
            WaterUnit(spawn[0], spawn[1], subgrid)
            # print for debugging purposes
            if DEBUG:
                print(f"💧 {subgrid.get_unit(spawn[0], spawn[1]).faction} unit at ({spawn[0]}, {spawn[1]}) has spawned")

        # communicate the selected spawns to the neighbour processors to inform them about the spawns
        spawn_queues = [[] for i in range(8)]
        spawn_queues = communicate(spawn_queues, selected_spawns, rank, sqrt_p, comm)

        # iterate over the spawn queues and spawn the water units in the neighbour processors
        for message in spawn_queues:
            for spawn in message:
                WaterUnit(spawn[0], spawn[1], subgrid)
                # print for debugging purposes
                if DEBUG:
                    print(f"💧 {subgrid.get_unit(spawn[0], spawn[1]).faction} unit at ({spawn[0]}, {spawn[1]}) has spawned")

        # at the end of the wave, reset the attack power of the fire units
        for fire_unit in subgrid.get_all_units():
            if fire_unit.faction == "Fire":
                fire_unit.reset_attack_power()
        
        # sync the processes and send the subgrid back to the manager
        comm.Barrier() 
        comm.send(subgrid, dest=0, tag=103)
        comm.Barrier()
        
    