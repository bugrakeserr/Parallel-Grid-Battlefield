import numpy as np

# grid class is used to represent the grid and the units on the grid
class Grid:

    # initialize the grid with the given size and offset
    def __init__(self, size, offset_x=0, offset_y=0, message_grid=False):
        self.size = size
        # message_grid boolean is used when the new grid is splitted from another one to be passed to another processor
        if not message_grid:
            self.grid = np.full((size, size), None)
        else:
            self.grid = []
        # offset is used to keep track of the global coordinates of the grid
        self.offset_x = offset_x
        self.offset_y = offset_y

        # queues to store the units that will be removed, damaged, or moved
        self.damage_queue = []
        self.movement_queue = []
        self.removal_queue = []
        self.death_queue = []

    # import the grid data from another grid
    def import_grid(self, grid):
        self.grid = grid
    
    # place a unit on the grid
    def place_unit(self, unit):
        x, y = unit.x - self.offset_x, unit.y - self.offset_y
        if 0 <= x < self.size and 0 <= y < self.size:
            self.grid[y, x] = unit
        else:
            print(f"Error: Coordinates ({unit.x}, {unit.y}) are out of bounds.")

    # get the neighbors of a cell at the given coordinates
    def get_neighbors(self, x, y):
        neighbors = []
        directions = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
        for dx, dy in directions:
            nx, ny = x + dx - self.offset_x, y + dy - self.offset_y
            if 0 <= nx < self.size and 0 <= ny < self.size:
                neighbors.append((nx + self.offset_x, ny + self.offset_y))
        return neighbors

    # get all the neighbors of a cell at the given coordinates (no boundary check)
    def get_all_neighbors(self, x, y):
        neighbors = []
        directions = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
        for dx, dy in directions:
            nx, ny = x + dx - self.offset_x, y + dy - self.offset_y
            neighbors.append((nx + self.offset_x, ny + self.offset_y))
        return neighbors
    
    # display the grid
    def display(self):
        print("  " + " ".join(str(i + self.offset_x) for i in range(self.grid.shape[1])))
        display_rows = []
        for idx, row in enumerate(self.grid):
            display_row = [
                cell.faction[0] if isinstance(cell, Unit) else '.' for cell in row
            ]
            print(f"{idx + self.offset_y} " + ' '.join(display_row))
            display_rows.append(' '.join(display_row))
        return display_rows

    # get the size of the grid
    def get_size(self):
        return self.size
    
    # get the unit at the given coordinates
    def get_unit(self, x, y):
        """Get the unit at global coordinates (x, y) within the subgrid."""
        x, y = x - self.offset_x, y - self.offset_y  # Map global to local coordinates
        if 0 <= x < self.size and 0 <= y < self.size:
            return self.grid[y, x]
        else:
            return None  # Return None for out-of-bounds access
        
    # get all the units on the grid
    def get_all_units(self):
        return [unit for unit in self.grid.flatten() if unit is not None]
    
    # enqueue a unit to be damaged
    def enqueue(self, unit, damage):
        self.damage_queue.append((unit, damage))
        
    # enqueue a unit to be damaged from a message
    def enqueue_from_message(self, message):
        unit = self.get_unit(message['x'], message['y'])
        self.damage_queue.append((unit, message['damage']))

    # enqueue a unit to be moved
    def enqueue_movement(self, unit, new_x, new_y):
        self.movement_queue.append((unit, new_x, new_y))
    
    # enqueue a unit to be moved from a message
    def enqueue_movement_from_message(self, message):
        self.movement_queue.append((message["unit"], message['x'], message['y']))

    # resolve the movement of the units
    def resolve_movement(self, debug):
        for unit, new_x, new_y in self.movement_queue:
            existing_unit = self.get_unit(new_x, new_y)
            if existing_unit is not None:
                unit.upgrade(existing_unit)
                if debug:
                    print(f"💪 {unit.faction} unit at ({unit.x}, {unit.y}) upgraded.")
            unit.x = new_x 
            unit.y = new_y
            self.place_unit(unit)
            
        self.movement_queue = []

    # enqueue a unit to be removed
    def enqueue_removal(self, unit,x, y):
        self.removal_queue.append((unit,x,y))
    
    # resolve the removal of the units
    def resolve_removal(self):
        for (unit,x,y) in self.removal_queue:
            self.grid[y-self.offset_y, x-self.offset_x] = None
        self.removal_queue = []
     
    # resolve the damage of the units
    def resolve_damage(self, debug):
        for unit, damage in self.damage_queue:
            unit.total_damage += damage
            if debug:
                print(f"🗡️ {unit.faction} unit at ({unit.x}, {unit.y}) took 🩹 {damage} damage. 💜 HP: {unit.hp}")
        self.damage_queue = []
        for unit in self.get_all_units():
            unit.get_damaged(unit.total_damage)
            unit.total_damage = 0
            if unit.is_dead():
                if debug:
                    print(f"💀 {unit.faction} unit at ({unit.x}, {unit.y}) has died")
                self.death_queue.append((unit.x,unit.y))
                self.remove_unit(unit)
        
    # resolve the healing of the units
    def resolve_healing(self, debug):
        for unit in self.get_all_units():
            if unit.decision == "Skip":
                unit.get_healed()
                if debug:
                    print(f"😇 {unit.faction} unit at ({unit.x}, {unit.y}) healing .... HP: {unit.hp}")

            else:
                unit.decision = "Skip"
    
    # remove a unit from the grid
    def remove_unit(self, unit):
        x, y = unit.x - self.offset_x, unit.y - self.offset_y
        self.grid[y, x] = None

    # replace a unit on the grid
    def replace_unit(self, unit, new_x, new_y):
        self.remove_unit(unit)
        unit.x = new_x
        unit.y = new_y
        self.place_unit(unit)

    # override the string representation of the grid
    def __str__(self):
        self.display()
        return ""

# unit class is used to represent the units on the grid
class Unit:
    # initialize the unit with the given faction, coordinates, and grid
    def __init__(self, faction, x, y, grid):
        self.faction = faction
        self.grid = grid
        self.x = x
        self.y = y
        self.hp = 0
        self.decision = "Skip"
        self.threshold = 0
        self.heal = 0
        self.total_damage = 0
        self.grid.place_unit(self)
    
    # heal the unit as long as the hp does not exceed the maximum hp
    def get_healed(self):
        if self.hp + self.heal > self.maximum_hp:
            self.hp = self.maximum_hp
        else:
            self.hp += self.heal

    # damage the unit
    def get_damaged(self, damage):
        self.hp -= damage
    
    # check if the unit is dead
    def is_dead(self):
        return self.hp <= 0
    
    # get the special attack pattern of the unit
    def get_attack_pattern(self, directions):
        n = self.grid.get_size()
        neighbors = []
        for dx, dy in directions:
            nx, ny = self.x + dx, self.y + dy
            if 0 <= nx and 0 <= ny:
                neighbors.append((nx, ny))
        return neighbors
    
    # decide whether to attack or skip
    def decide(self):
        if self.threshold > self.hp:
            self.decision = "Skip"
        else:
            self.decision = "Attack"
            
        return self.decision
        
    # print the unit object
    def __str__(self):
        faction_emoji = {
            'Earth': '🌍',
            'Fire': '🔥',
            'Water': '💧',
            'Air': '🛩️'
        }
        emoji = faction_emoji.get(self.faction, '')
        return f"{emoji} {self.faction} unit at ({self.x}, {self.y}) with 💙 {self.hp} HP with attack power: {self.attack}."


# subclass of the unit class representing the Earth unit
class EarthUnit(Unit):
    def __init__(self, x, y, grid):
        # call Unit's constructor
        super().__init__('Earth', x, y, grid)  
        
        # set the Earth unit's attributes
        self.hp = 18
        self.attack = 2
        self.heal = 3
        self.threshold = 9
        self.maximum_hp = 18

    # fortification decreases the damage taken by half
    def get_damaged(self, damage):
        self.hp -= damage // 2

    # get the attack pattern of the Earth unit
    def get_attack_pattern(self):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        return super().get_attack_pattern(directions)


# subclass of the unit class representing the Fire unit
class FireUnit(Unit):
    def __init__(self, x, y, grid):
        # call Unit's constructor
        super().__init__('Fire', x, y, grid)

        # set the Fire unit's attributes
        self.hp = 12
        self.attack = 4
        self.heal = 1
        self.threshold = 6
        self.maximum_hp = 12
        self.attacked_to = []

    # increase the attack power of the Fire unit
    def increase_attack_power(self, debug):
        if self.attack < 6:
            self.attack += 1
            if debug:
                print(f"🔥 {self.faction} unit at ({self.x}, {self.y}) increased attack power to {self.attack}")

    # reset the attack power of the Fire unit
    def reset_attack_power(self):
        self.attack = 4

    # get the attack pattern of the Fire unit
    def get_attack_pattern(self):
        return self.grid.get_neighbors(self.x, self.y)


# subclass of the unit class representing the Water unit
class WaterUnit(Unit):
    # initialize the Water unit with the given coordinates and grid
    def __init__(self, x, y, grid):

        # call Unit's constructor
        super().__init__('Water', x, y, grid)

        # set the Water unit's attributes
        self.hp = 14
        self.attack = 3
        self.heal = 2
        self.threshold = 7
        self.maximum_hp = 14

    # get the attack pattern of the Water unit
    def get_attack_pattern(self):
        directions = [(-1, -1), (1, 1), (-1, 1), (1, -1)]
        return super().get_attack_pattern(directions)


# subclass of the unit class representing the Air unit
class AirUnit(Unit):
    # initialize the Air unit with the given coordinates and grid
    def __init__(self, x, y, grid):

        # call Unit's constructor
        super().__init__('Air', x, y, grid)

        # set the Air unit's attributes
        self.hp = 10
        self.attack = 2
        self.heal = 2
        self.threshold = 5
        self.maximum_hp = 10
        self.attack_messages = []

    # move to a new position
    def move(self, x, y):
        self.x = x
        self.y = y
        
    # get the attack pattern of the Air unit
    def get_attack_pattern(self, x, y):
        directions = [(-1, -1), (1, 1), (-1, 1), (1, -1), (-1, 0), (1, 0), (0, -1), (0, 1)]
        additional_directions = [(2 * dx, 2 * dy) for dx, dy in directions]
        directions = directions + additional_directions
        neighbors = []
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            neighbors.append((nx, ny))
        return neighbors
    
    
    # upgrade an air unit when two of them move the same position
    def upgrade(self,existing_unit):
        self.attack += existing_unit.attack
        self.hp += existing_unit.hp
        if self.hp > self.maximum_hp:
            self.hp = self.maximum_hp