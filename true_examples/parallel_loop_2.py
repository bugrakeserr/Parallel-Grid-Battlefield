# Import the MPI module from the mpi4py library
from mpi4py import MPI

# 4*4 matrix
matrix = [[0, 1, 2, 3],
            [4, 5, 6, 7],
            [8, 9, 10, 11],
            [12, 13, 14, 15]]


# Get the rank (unique ID) of the current process
rank = MPI.COMM_WORLD.Get_rank()

# Get the total number of processes in the communicator
n_ranks = MPI.COMM_WORLD.Get_size()

sqrt_p = int((n_ranks**0.5))

# Calculate how many numbers each rank should handle
numbers_per_rank = len(matrix) // sqrt_p

# Calculate the range of numbers this rank will handle
my_first_x = (rank//sqrt_p) * numbers_per_rank  # Starting number for this rank
my_last_x = my_first_x + numbers_per_rank  # Ending number (exclusive) for this rank
my_first_y = rank%sqrt_p * numbers_per_rank  # Starting number for this rank
my_last_y = my_first_y + numbers_per_rank  # Ending number (exclusive) for this
print(my_first_x, my_last_x, my_first_y, my_last_y)

# Loop through the assigned range and print the numbers this rank is responsible for
for i in range(my_first_x, my_last_x):
    for j in range(my_first_y, my_last_y):
        print("I'm rank {:d} and I'm printing the number {:d}.".format(rank, matrix[i][j]))
